"""
Simulator implementation of the HAL.

This is the only file that knows about both the C++ firmware (robot_cpp) and
the ground-truth maze (generation/). It is the platform layer — the equivalent
of the hardware drivers on a real micromouse.

The firmware never imports this. It is wired up at startup via init().
"""
import robot_cpp
import simulation.sim_state as sim

# The C++ objects are kept as module-level references so the sensing
# functions below can close over them, and so app.py can read the
# firmware state for snapshot recording.
firmware: robot_cpp.RobotState | None = None
_hal:     robot_cpp.Hal        | None = None
_on_render = None


# ---------------------------------------------------------------------------
# HAL implementations — registered with the C++ Hal object at startup.
# The firmware calls these; they query / update the ground-truth simulator.
# ---------------------------------------------------------------------------

def _wall_in_absolute_direction(absolute_direction: int) -> bool:
    """
    Query the ground-truth maze for a wall adjacent to the robot's *actual*
    position in a given absolute direction (0=N, 1=E, 2=S, 3=W).
    """
    from generation.maze_generator import Direction as MazeDir
    _dir_map = {
        0: MazeDir.N,
        1: MazeDir.E,
        2: MazeDir.S,
        3: MazeDir.W,
    }
    cell = sim.maze.cell_at(sim.x, sim.y)
    return cell.walls[_dir_map[absolute_direction]]


def _sense_left()  -> bool:
    return _wall_in_absolute_direction(firmware.relative_to_absolute(-1))

def _sense_front() -> bool:
    return _wall_in_absolute_direction(firmware.relative_to_absolute(0))

def _sense_right()  -> bool:
    return _wall_in_absolute_direction(firmware.relative_to_absolute(1))


def _move_forward() -> None:
    """
    Advance the ground-truth position by one cell, then fire the render
    callback so the API can record a state snapshot.

    Note: the firmware's own x/y are updated *inside* the C++ WallFollower
    before this function is called (in _move_forward_and_record). This
    function is responsible only for the ground-truth (simulator) side.
    """
    sim.advance()
    if _on_render is not None:
        _on_render()


# ---------------------------------------------------------------------------
# init — called once by app.py before every simulation run
# ---------------------------------------------------------------------------

def init(maze, on_render=None, on_turn=None) -> robot_cpp.WallFollower:
    """
    Create fresh C++ firmware objects, wire up the HAL, and return the
    WallFollower ready to run.

    on_render: called after every move_forward (position snapshot)
    on_turn:   called after every turn_left / turn_right (heading snapshot)
    """
    global firmware, _hal, _on_render
    _on_render = on_render

    firmware = robot_cpp.RobotState()
    _hal     = robot_cpp.Hal()

    # Initialise ground-truth state and reset the C++ firmware state.
    sim.init(maze, firmware)

    # Wire Python callables into the C++ HAL.
    _hal.sense_left    = _sense_left
    _hal.sense_front   = _sense_front
    _hal.sense_right   = _sense_right
    _hal.move_forward  = _move_forward
    _hal.on_turn_left  = on_turn or (lambda: None)
    _hal.on_turn_right = on_turn or (lambda: None)

    # Construct and return the C++ WallFollower.
    # pybind11 keep_alive ensures firmware and _hal stay alive for its lifetime.
    return robot_cpp.WallFollower(firmware, _hal)
