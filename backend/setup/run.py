##########################################################################
# Medicinal Magician backend: run.py   <-- THIS IS THE FILE YOU RUN
#
# PURPOSE
# Starts the backend server with one command.
#
# HOW TO RUN (from the backend/setup folder, with the venv activated)
#     python run.py
# Or press the Run button in VS Code with this file open.
#
# THEN
# Open http://127.0.0.1:8000/docs in your browser.
# Leave the terminal alone while you use it. Ctrl+C stops the server.
#
# WHAT IT DOES
# Launches uvicorn (the web server) pointed at app/main.py, with
# auto-reload: save any .py file and the server restarts by itself.
##########################################################################
import uvicorn

if __name__ == "__main__":
    print("\n  Medicinal Magician backend starting...")
    print("  Open http://127.0.0.1:8000/docs   (Ctrl+C to stop)\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
