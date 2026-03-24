"""
Hardware Abstraction Layer — interface only.
 
The firmware calls only these six functions. It never imports from
simulation/ or generation/. How they are implemented is the platform's
problem, not the firmware's.
 
In real firmware these would call sensor driver functions and write to
motor control registers. Here they raise NotImplementedError until a
concrete platform (e.g. hal_sim.py) replaces them at startup.
"""
 
 
def _not_implemented(*_):
    raise NotImplementedError("No HAL platform has been registered.")
 
 
# --- Function pointers (equivalent to a C vtable) ---
_sense_wall_left  = _not_implemented
_sense_wall_front = _not_implemented
_sense_wall_right = _not_implemented
_move_forward     = _not_implemented
 
 
def register(sense_left, sense_front, sense_right, move_forward):
    """
    Called once at startup by the platform (simulator or real hardware)
    to wire up all four platform-specific functions.
    """
    global _sense_wall_left, _sense_wall_front, _sense_wall_right, _move_forward
    _sense_wall_left  = sense_left
    _sense_wall_front = sense_front
    _sense_wall_right = sense_right
    _move_forward     = move_forward
 
 
# --- The six HAL calls the firmware is allowed to make ---
 
def sense_wall_left() -> bool:
    return _sense_wall_left()
 
def sense_wall_front() -> bool:
    return _sense_wall_front()
 
def sense_wall_right() -> bool:
    return _sense_wall_right()
 
def move_forward() -> None:
    _move_forward()
 
def turn_left() -> None:
    import robot.state as state
    state.heading = (state.heading - 1) % 4
 
def turn_right() -> None:
    import robot.state as state
    state.heading = (state.heading + 1) % 4