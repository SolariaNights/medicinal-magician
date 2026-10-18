##########################################################################
# Medicinal Magician backend: retrieval.py  (the "R" in RAG)
#
# PURPOSE
# Before asking the AI anything, find the guideline sections that match the
# patient's symptoms. Giving the AI real reference text to work from is what
# keeps it from making things up (the RAG idea in the blueprint).
#
# INPUT
# symptoms (most important) + patient history (small nudge, weight 0.25)
#
# OUTPUT
# The top matching guideline chunks from data/guidelines/*.md
# (each "## " heading in those files is one chunk).
#
# HOW IT SCORES (version 1)
# Counts shared keywords, giving rare words more weight than common ones.
# Weakness: it doesn't know synonyms ("peeing a lot" != "urination").
#
# LATER MILESTONE
# Replace search() with embedding (vector) search in Postgres/pgvector.
# Keep the same function name and inputs so nothing else has to change.
##########################################################################
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

_WORD = re.compile(r"[a-z0-9]+")
_STOP = set("""a an and are as at be by for from has have in is it its of on or
that the to was were with without this these those patient patients""".split())


_SUFFIXES = ("ing", "ed", "es", "s", "y")


def _stem(w: str) -> str:
    # Crude on purpose: "thirsty"->"thirst", "vomiting"->"vomit". Embeddings replace this in v2.
    for suf in _SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def _tokens(text: str) -> list[str]:
    return [_stem(w) for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2]


@dataclass
class Chunk:
    id: str
    source: str
    heading: str
    text: str


class GuidelineIndex:
    def __init__(self, folder: Path):
        self.chunks: list[Chunk] = []
        self._tf: list[Counter] = []
        self._df: Counter = Counter()
        for path in sorted(folder.glob("*.md")):
            self._add_file(path)

    def _add_file(self, path: Path) -> None:
        parts = re.split(r"^## ", path.read_text(encoding="utf-8"), flags=re.M)
        for i, part in enumerate(parts[1:], start=1):
            heading, _, body = part.partition("\n")
            chunk = Chunk(id=f"{path.stem}#{i}", source=path.stem,
                          heading=heading.strip(), text=body.strip())
            tf = Counter(_tokens(heading + " " + heading + " " + body))
            self.chunks.append(chunk)
            self._tf.append(tf)
            self._df.update(tf.keys())

    def search(self, symptoms: str, history: str = "", k: int = 6) -> list[Chunk]:
        """Symptoms drive the match; history only nudges (weight 0.25)."""
        weights = {w: 0.25 for w in _tokens(history)}
        weights.update({w: 1.0 for w in _tokens(symptoms)})
        n = len(self.chunks) or 1
        scored = []
        for chunk, tf in zip(self.chunks, self._tf):
            s = sum(wt * (1 + math.log(tf[w])) * math.log(1 + n / self._df[w])
                    for w, wt in weights.items() if w in tf)
            if s > 0:
                scored.append((s, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]
