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
    solver: str = "wall_follower"  # "wall_follower" or "flood_fill"


@app.post("/generate")
def generate(req: MazeRequest):
    """Generate a new maze and return it as JSON."""
    maze = generate_maze(req.width, req.height)
    return maze_to_dict(maze)


@app.post("/simulate")
def simulate(req: MazeRequest):
    """
    Generate a maze, run the C++ firmware solver, and return every state
    snapshot captured after each turn or move.
    """
    import robot_cpp
    from fastapi import HTTPException
    from simulation.hal_sim import init as sim_init
    import simulation.hal_sim as hal_sim

    # The C++ firmware is compiled for a fixed grid size.  Reject requests that
    # don't match — running a larger maze causes out-of-bounds array writes.
    if req.width != robot_cpp.WIDTH or req.height != robot_cpp.HEIGHT:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Simulation requires a {robot_cpp.WIDTH}×{robot_cpp.HEIGHT} maze "
                f"(firmware is compiled for this size). Got {req.width}×{req.height}."
            ),
        )

    maze = generate_maze(req.width, req.height)

    steps = []

    def record():
        # Read the firmware state directly from the C++ RobotState object.
        # hal_sim.firmware is the RobotState created in sim_init().
        f = hal_sim.firmware
        if req.solver == "flood_fill":
            print(f"[flood_fill] step={len(steps):4d}  pos=({f.x:2d},{f.y:2d})  heading={f.heading}")
        steps.append({
            "x":           f.x,
            "y":           f.y,
            "heading":     f.heading,        # int 0–3 via C++ property
            "walls":       list(f.walls),    # list of ints via pybind11/stl
            "walls_known": list(f.walls_known),
        })

    # sim_init wires up the HAL and returns the requested solver.
    robot = sim_init(maze, on_render=record, on_turn=record, solver=req.solver)

    # Capture the starting position before any movement.
    record()

    # Run the C++ firmware — this call blocks until the goal is reached.
    robot.run()

    f = hal_sim.firmware
    solved = (f.x == robot_cpp.WIDTH - 1 and f.y == robot_cpp.HEIGHT - 1)
    if not solved:
        print(f"[{req.solver}] did not reach goal — ended at ({f.x},{f.y}) after {len(steps)} steps")

    return {"maze": maze_to_dict(maze), "steps": steps, "solved": solved}
