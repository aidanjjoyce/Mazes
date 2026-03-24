"""
Simulator implementation of the HAL.

This is the only file that knows about both the firmware (robot/) and
the ground truth maze (generation/). It is the platform layer — the
equivalent of the hardware drivers on a real micromouse.

The firmware never imports this. It is wired up at startup via hal.register().
"""
import robot.hal as hal
import robot.state as firmware
import simulation.sim_state as sim

_on_render = None


def _wall_in_absolute_direction(absolute_direction):
    """
    Query the ground truth maze for a wall adjacent to the robot's
    actual position in a given absolute direction.
    """
    from generation.maze_generator import Direction
    direction_map = {
        firmware.NORTH: Direction.N,
        firmware.EAST:  Direction.E,
        firmware.SOUTH: Direction.S,
        firmware.WEST:  Direction.W,
    }
    cell = sim.maze.cell_at(sim.x, sim.y)
    return cell.walls[direction_map[absolute_direction]]


def _sense_left() -> bool:
    return _wall_in_absolute_direction(firmware.relative_to_absolute(-1))

def _sense_front() -> bool:
    return _wall_in_absolute_direction(firmware.relative_to_absolute(0))

def _sense_right() -> bool:
    return _wall_in_absolute_direction(firmware.relative_to_absolute(1))


def _move_forward() -> None:
    """
    Advance both firmware believed position and ground truth position,
    then fire the render callback if one is registered.
    """
    firmware.x += firmware.DX[firmware.heading]
    firmware.y += firmware.DY[firmware.heading]
    sim.advance()
    if _on_render is not None:
        _on_render()


def init(maze, on_render=None):
    """
    Initialise the simulator and register this platform with the HAL.
    on_render: optional callable fired after every move_forward.
    Call this once before running any firmware code.
    """
    global _on_render
    _on_render = on_render
    sim.init(maze)
    hal.register(
        sense_left=_sense_left,
        sense_front=_sense_front,
        sense_right=_sense_right,
        move_forward=_move_forward,
    )