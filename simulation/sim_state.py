"""
Simulator ground-truth state.

This models the physical reality of where the robot actually is in the maze,
independent of the robot's internal model (held in the C++ RobotState).

In a perfect simulation the two positions stay in sync. If the firmware's
dead-reckoning ever diverged from reality, you could detect it here.

Only hal_sim.py reads from and writes to this module.
"""
import robot_cpp

x    = 0
y    = 0
maze = None

# Reference to the C++ RobotState, set by init().
# advance() reads heading from it to know which direction to step.
_firmware: robot_cpp.RobotState | None = None


def init(m, firmware_state: robot_cpp.RobotState) -> None:
    """
    Called once per simulation run by hal_sim.init().
    Resets ground-truth position to the maze start and resets C++ firmware.
    """
    global x, y, maze, _firmware
    maze      = m
    _firmware = firmware_state

    x, y = m.start

    # Reset the C++ firmware state and place it at the start cell.
    firmware_state.reset()
    firmware_state.x = m.start[0]
    firmware_state.y = m.start[1]


def advance() -> None:
    """
    Move the ground-truth position one step in the firmware's current heading.
    Called by hal_sim._move_forward() after the C++ firmware has already
    updated its own believed position.
    """
    global x, y
    heading = _firmware.heading          # int 0–3 from the C++ property
    x += robot_cpp.DX[heading]
    y += robot_cpp.DY[heading]
