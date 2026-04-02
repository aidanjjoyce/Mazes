#pragma once
#include "state.hpp"
#include "hal.hpp"
#include <array>

namespace robot {

// ---------------------------------------------------------------------------
// FloodFill — adaptive flood-fill navigation algorithm
//
// The flood-fill algorithm treats the maze like a basin of water with the
// goal as a drain. Every cell is assigned a "distance" value representing
// the minimum number of steps to the goal assuming all currently-known
// walls. The robot always steps to the lowest-distance open neighbour.
//
// When the robot senses a wall it did not previously know about, it
// recomputes the entire distance map (re-floods) and re-plans. This means
// the robot always follows the globally-optimal path given what it knows,
// and self-corrects as it discovers new walls — unlike the wall-follower,
// it cannot be trapped by loops or islands.
//
// The distance map (_dist) is algorithm-specific state and lives here, not
// in RobotState. RobotState holds only the robot's model of the physical
// world (position, heading, wall map); FloodFill holds its planning data.
//
// Same design constraints as WallFollower: takes RobotState and Hal by
// reference, no global mutable state, no heap allocation.
// ---------------------------------------------------------------------------
class FloodFill {
public:
    // HAL is validated immediately — fail at startup, not mid-run.
    FloodFill(RobotState& state, Hal& hal);

    // Run flood-fill until the goal cell (WIDTH-1, HEIGHT-1).
    void run();

    // Read-only access to the firmware's internal state.
    const RobotState& state() const { return _state; }

private:
    // Sense wall in relative direction, record result in wall map.
    // Returns true if a wall is present.
    bool _sense_and_record(int relative_offset);

    // Mark passage walls, advance firmware position, then notify the HAL.
    void _move_forward_and_record();

    // Update heading and fire the HAL turn callback.
    void _turn_left();
    void _turn_right();

    // Recompute the distance map via BFS from the goal, respecting all walls
    // currently recorded in _state.walls.  Unknown walls are treated as open
    // (optimistic assumption — self-corrects when walls are later sensed).
    void _flood();

    RobotState& _state;
    Hal&        _hal;

    // Distance-to-goal for each cell.  255 is used as "unreachable" sentinel.
    // Sized at compile time — no heap allocation.
    std::array<uint8_t, CELLS> _dist;
};

} // namespace robot
