"""
Hardware Abstraction Layer Interface.

The firmware calls only these six functions. It never imports from
simulation/ or generation/. How they are implemented is the platform's
problem, not the firmware's.

In real firmware these would call sensor driver functions and write to
motor control registers. Here they raise NotImplementedError until a
concrete platform (e.g. hal_sim.py) replaces them at startup.
"""


def _not_implemented(*_):
    raise NotImplementedError("No HAL platform has been registered.")

def _noop():
    pass


_sense_wall_left  = _not_implemented
_sense_wall_front = _not_implemented
_sense_wall_right = _not_implemented
_move_robot_forward = _not_implemented
_on_turn_left = _noop
_on_turn_right = _noop


def register(sense_left, sense_front, sense_right, move_forward,
             on_turn_left=None, on_turn_right=None):
    """
    Called once at startup by the platform (simulator or real hardware)
    to wire up platform-specific functions.
    on_turn_left / on_turn_right: optional callbacks fired after each turn.
    """
    global _sense_wall_left, _sense_wall_front, _sense_wall_right
    global _move_robot_forward, _on_turn_left, _on_turn_right
    _sense_wall_left    = sense_left
    _sense_wall_front   = sense_front
    _sense_wall_right   = sense_right
    _move_robot_forward = move_forward
    _on_turn_left  = on_turn_left  or _noop
    _on_turn_right = on_turn_right or _noop


def sense_wall_left() -> bool:
    return _sense_wall_left()

def sense_wall_front() -> bool:
    return _sense_wall_front()

def sense_wall_right() -> bool:
    return _sense_wall_right()

def move_robot_forward() -> None:
    _move_robot_forward()

def turn_left() -> None:
    import robot.state as state
    state.heading = (state.heading - 1) % 4
    _on_turn_left()

def turn_right() -> None:
    import robot.state as state
    state.heading = (state.heading + 1) % 4
    _on_turn_right()