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
    Generate a maze, run the C++ wall-follower firmware, and return every
    state snapshot captured after each turn or move.
    """
    import robot_cpp
    from simulation.hal_sim import init as sim_init
    import simulation.hal_sim as hal_sim

    maze = generate_maze(req.width, req.height)

    steps = []

    def record():
        # Read the firmware state directly from the C++ RobotState object.
        # hal_sim.firmware is the RobotState created in sim_init().
        f = hal_sim.firmware
        steps.append({
            "x":           f.x,
            "y":           f.y,
            "heading":     f.heading,        # int 0–3 via C++ property
            "walls":       list(f.walls),    # list of ints via pybind11/stl
            "walls_known": list(f.walls_known),
        })

    # sim_init wires up the HAL and returns the C++ WallFollower.
    robot = sim_init(maze, on_render=record, on_turn=record)

    # Capture the starting position before any movement.
    record()

    # Run the C++ firmware — this call blocks until the goal is reached.
    robot.run()

    return {"maze": maze_to_dict(maze), "steps": steps}
