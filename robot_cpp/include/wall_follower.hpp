#pragma once
#include "state.hpp"
#include "hal.hpp"

namespace robot {

// ---------------------------------------------------------------------------
// WallFollower — left-hand rule navigation algorithm
//
// This class is the firmware equivalent of robot/wall_follower.py.
// It only knows about RobotState and Hal — never about the maze, the
// simulator, or Python. That boundary is enforced by the include list above.
//
// Firmware best practice: take dependencies by reference, not by value.
//   WallFollower does not own its state or HAL — it merely uses them.
//   Ownership stays with whoever creates the robot (the pybind11 module in
//   bindings.cpp). This makes the lifetime explicit and avoids hidden copies.
//
// Firmware best practice: no global mutable state.
//   Everything this class needs is held in _state and _hal. Creating a
//   second WallFollower with a different RobotState would just work.
// ---------------------------------------------------------------------------
class WallFollower {
public:
    // HAL is validated immediately in the constructor — fail at startup,
    // not halfway through a maze run.
    WallFollower(RobotState& state, Hal& hal);

    // Run the left-hand rule until the goal cell (WIDTH-1, HEIGHT-1).
    void run();

    // Read-only access to the firmware's internal state.
    // The const& prevents the caller copying or modifying the state.
    // Python gets this via the pybind11 binding with reference semantics.
    const RobotState& state() const { return _state; }

private:
    // Sense wall in relative direction, record result in wall map.
    // Returns true if a wall is present.
    bool _sense_and_record(int relative_offset);

    // Mark passage walls, advance firmware position, then notify the HAL.
    void _move_forward_and_record();

    // Update heading and fire the HAL turn callback (simulator snapshot hook).
    void _turn_left();
    void _turn_right();

    RobotState& _state;
    Hal&        _hal;
};

} // namespace robot
