#include "state.hpp"

namespace robot {

void RobotState::reset() {
    x       = 0;
    y       = 0;
    heading = Direction::NORTH;

    // std::array::fill is the idiomatic way to zero out a fixed-size array.
    // On most compilers this lowers to a single memset instruction.
    walls.fill(0);
    walls_known.fill(0);
}

void RobotState::mark_wall(int cx, int cy, Direction dir, bool present) {
    const int     idx = cell_index(cx, cy);
    const uint8_t bit = WALL_BITS[static_cast<int>(dir)];

    if (present)
        walls[idx] |=  bit;   // set the wall bit
    else
        walls[idx] &= ~bit;   // clear the wall bit (confirmed opening)

    // Either way, we now have a definitive reading for this wall.
    walls_known[idx] |= bit;
}

bool RobotState::has_wall(int cx, int cy, Direction dir) const {
    return (walls[cell_index(cx, cy)] & WALL_BITS[static_cast<int>(dir)]) != 0;
}

bool RobotState::is_known(int cx, int cy, Direction dir) const {
    return (walls_known[cell_index(cx, cy)] & WALL_BITS[static_cast<int>(dir)]) != 0;
}

Direction RobotState::relative_to_absolute(int relative_offset) const {
    // The + 4 before the modulo prevents undefined behaviour on negative
    // offsets (e.g. relative_offset = -1). In Python, -1 % 4 == 3 because
    // Python's modulo always returns a non-negative result; C++'s does not.
    return static_cast<Direction>(
        (static_cast<int>(heading) + relative_offset + 4) % 4
    );
}

} // namespace robot
