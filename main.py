"""
Single entrypoint: starts the FastAPI server and opens the browser.
Run with:  python main.py
"""
import threading
import time
import webbrowser
import uvicorn
 
HOST = "127.0.0.1"
PORT = 8000
URL  = f"http://{HOST}:{PORT}"
 
 
def _open_browser():
    time.sleep(1.2)   # give uvicorn a moment to start
    webbrowser.open(URL)
 
 
if __name__ == "__main__":
    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run("api.app:app", host=HOST, port=PORT, reload=True)
 