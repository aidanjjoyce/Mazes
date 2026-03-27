from fastapi import FastAPI
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


class MazeRequest(BaseModel):
    width: int = 15
    height: int = 15


@app.post("/generate")
def generate(req: MazeRequest):
    """Generate a new maze and return it as JSON."""
    maze = generate_maze(req.width, req.height)
    return maze_to_dict(maze)


@app.post("/simulate")
def simulate(req: MazeRequest):
    """
    Generate a maze, run the wall-follower simulation, and return every
    state snapshot captured after each turn or move.
    """
    import robot.state as robot_state
    from simulation.hal_sim import init as sim_init
    from robot import wall_follower

    maze = generate_maze(req.width, req.height)

    # Resize firmware state arrays to match this maze before reset
    robot_state.WIDTH  = maze.width
    robot_state.HEIGHT = maze.height
    robot_state.walls       = bytearray(maze.width * maze.height)
    robot_state.walls_known = bytearray(maze.width * maze.height)

    steps = []

    def record():
        steps.append({
            "x":           robot_state.x,
            "y":           robot_state.y,
            "heading":     robot_state.heading,
            "walls":       list(robot_state.walls),
            "walls_known": list(robot_state.walls_known),
        })

    # sim_init calls sim_state.init → firmware.reset, then registers HAL
    sim_init(maze, on_render=record, on_turn=record)

    # Capture starting position before any movement
    record()

    wall_follower.run()

    return {"maze": maze_to_dict(maze), "steps": steps}
