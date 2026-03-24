"""
Simulator ground truth state.

This is physical reality — where the robot actually is in the maze.
The firmware cannot import this. Only hal_sim.py reads from it.

In a perfect simulation this stays in sync with robot.state.
Later, introducing motor slip or sensor noise would cause drift.
"""
import robot.state as firmware

x = 0
y = 0
maze = None


def init(m):
    """Called once at startup with the ground truth maze."""
    global x, y, maze
    maze = m
    x, y = m.start
    firmware.reset()
    firmware.x, firmware.y = m.start


def advance():
    """Move ground truth position one step in the current heading."""
    global x, y
    x += firmware.DX[firmware.heading]
    y += firmware.DY[firmware.heading]
