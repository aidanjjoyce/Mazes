#include "wall_follower.hpp"

namespace robot {

WallFollower::WallFollower(RobotState& state, Hal& hal)
    : _state(state), _hal(hal)
{
    // Validate immediately — any missing HAL function is a programming error
    // that should blow up at construction time, not buried in run().
    _hal.validate();
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

bool WallFollower::_sense_and_record(int relative_offset) {
    // Ask the HAL for the physical wall reading.
    bool wall = false;
    if      (relative_offset == -1) wall = _hal.sense_left();
    else if (relative_offset ==  0) wall = _hal.sense_front();
    else                            wall = _hal.sense_right();

    // Record the result into the firmware's wall map.
    const Direction absolute = _state.relative_to_absolute(relative_offset);
    _state.mark_wall(_state.x, _state.y, absolute, wall);

    return wall;
}

void WallFollower::_move_forward_and_record() {
    const Direction dir = _state.relative_to_absolute(0);

    // Mark the wall we are about to pass through as absent in the current cell.
    _state.mark_wall(_state.x, _state.y, dir, false);

    // Advance the firmware's believed position.
    // This happens here — inside the firmware — rather than inside the HAL
    // implementation. On real hardware the encoder/odometry callback would
    // confirm the move; here we trust the simulation is perfect.
    _state.x += DX[static_cast<int>(_state.heading)];
    _state.y += DY[static_cast<int>(_state.heading)];

    // Notify the HAL. In simulation this advances the ground-truth position
    // and fires the Python record() callback to capture a state snapshot.
    _hal.move_forward();

    // Mark the opposite wall in the new cell as absent (we just came through it).
    const Direction opposite = static_cast<Direction>(
        (static_cast<int>(dir) + 2) % 4
    );
    _state.mark_wall(_state.x, _state.y, opposite, false);
}

void WallFollower::_turn_left() {
    // Heading decrements by 1 (mod 4).  The + 4 prevents a negative result
    // for the same reason as in relative_to_absolute — C++ modulo can be
    // negative when the left operand is negative; Python's cannot.
    _state.heading = static_cast<Direction>(
        (static_cast<int>(_state.heading) + 3) % 4
    );

    // Fire the optional snapshot callback. std::function evaluates to false
    // when empty, so this is safe even if the simulator didn't register one.
    if (_hal.on_turn_left) _hal.on_turn_left();
}

void WallFollower::_turn_right() {
    _state.heading = static_cast<Direction>(
        (static_cast<int>(_state.heading) + 1) % 4
    );
    if (_hal.on_turn_right) _hal.on_turn_right();
}

// ---------------------------------------------------------------------------
// Main loop
// ---------------------------------------------------------------------------

void WallFollower::run() {
    // Run until the firmware's believed position reaches the goal.
    while (_state.x != WIDTH - 1 || _state.y != HEIGHT - 1) {
        const bool wall_left  = _sense_and_record(-1);
        const bool wall_front = _sense_and_record( 0);
        const bool wall_right = _sense_and_record(+1);

        if (!wall_left) {
            // Left is open — turn left and move (classic left-hand rule)
            _turn_left();
            _move_forward_and_record();
        } else if (!wall_front) {
            // Can go straight
            _move_forward_and_record();
        } else if (!wall_right) {
            // Turn right and move
            _turn_right();
            _move_forward_and_record();
        } else {
            // Dead end — turn around (two left turns)
            _turn_left();
            _turn_left();
        }
    }
}

} // namespace robot
