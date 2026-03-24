"""
Wall follower firmware — left-hand rule.

Only imports from robot/. Never touches simulation/ or generation/.
Navigates by always attempting to turn left first, then go forward,
then turn right, then turn around — the classic left-hand rule.
"""
import robot.hal as hal
import robot.state as state


def _sense_and_record(relative_offset) -> bool:
    """
    Sense a wall in a relative direction and record it in the wall map.
    relative_offset: -1 = left, 0 = front, +1 = right
    Returns True if there is a wall.
    """
    if relative_offset == -1:
        wall = hal.sense_wall_left()
    elif relative_offset == 0:
        wall = hal.sense_wall_front()
    else:
        wall = hal.sense_wall_right()

    absolute = state.relative_to_absolute(relative_offset)
    state.mark_wall(state.x, state.y, absolute, present=wall)

    return wall


def run():
    """
    Run the wall follower until the robot reaches the goal cell.
    Senses all three directions at each step before deciding where to move.
    """
    while (state.x, state.y) != (state.WIDTH - 1, state.HEIGHT - 1):
        wall_left  = _sense_and_record(-1)
        wall_front = _sense_and_record( 0)
        wall_right = _sense_and_record(+1)

        if not wall_left:
            hal.turn_left()
            hal.move_robot_forward()
        elif not wall_front:
            hal.move_robot_forward()
        elif not wall_right:
            hal.turn_right()
            hal.move_robot_forward()
        else:
            hal.turn_left()
            hal.turn_left()