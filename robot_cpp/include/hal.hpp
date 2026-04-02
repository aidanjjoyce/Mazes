#pragma once
#include <functional>
#include <stdexcept>

namespace robot {

// ---------------------------------------------------------------------------
// Hardware Abstraction Layer
//
// The firmware calls only these six operations. It never knows whether it is
// running on real hardware or inside a Python simulation. That is the whole
// point of the HAL — the platform registers concrete implementations at
// startup and the firmware remains untouched.
//
// On real hardware these std::functions would be replaced by direct calls to
// sensor drivers and motor-control registers. Here they are filled by
// pybind11-wrapped Python callables from hal_sim.py.
//
// Firmware best practice: the HAL is a pure interface — no logic lives here.
// ---------------------------------------------------------------------------

struct Hal {
    // bool() — sense a wall in the relative direction, return true if present
    using SenseFn  = std::function<bool()>;

    // void() — actuate a motor or fire a notification callback
    using ActionFn = std::function<void()>;

    SenseFn  sense_left;
    SenseFn  sense_front;
    SenseFn  sense_right;
    ActionFn move_forward;

    // Optional callbacks fired after each turn so the simulator can record
    // a state snapshot. std::function evaluates to false when empty, so the
    // wall follower can safely check before calling.
    ActionFn on_turn_left;
    ActionFn on_turn_right;

    // Called in the WallFollower constructor. Fails loudly at initialisation
    // time rather than silently mid-run with a null-function dereference.
    void validate() const {
        if (!sense_left || !sense_front || !sense_right || !move_forward)
            throw std::logic_error(
                "HAL not fully registered — "
                "sense_left, sense_front, sense_right and move_forward are required.");
    }
};

} // namespace robot
