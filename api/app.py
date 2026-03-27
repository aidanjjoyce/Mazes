from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
from generation.maze_generator import generate_maze, maze_to_dict
 
app = FastAPI(title="Mazes API")
 
# Serve the React frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
 
 
@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
 
 
class GenerateRequest(BaseModel):
    width: int = 15
    height: int = 15
 
 
@app.post("/generate")
def generate(req: GenerateRequest):
    """Generate a new maze and return it as JSON."""
    maze = generate_maze(req.width, req.height)
    return maze_to_dict(maze)
 