#pragma once
#include <array>
#include <cstdint>   // uint8_t — guaranteed 8-bit regardless of platform

namespace robot {

// ---------------------------------------------------------------------------
// Compile-time maze dimensions
//
// Firmware best practice: use constexpr not #define.
//   - constexpr has a type  (#define does not)
//   - constexpr has scope   (#define pollutes every translation unit)
//   - constexpr is visible  (debuggers can show its value; #define cannot)
//
// On real hardware these would be set once for the specific maze competition
// and never change at runtime — baking them in at compile time is intentional.
// ---------------------------------------------------------------------------
inline constexpr int WIDTH  = 15;
inline constexpr int HEIGHT = 15;
inline constexpr int CELLS  = WIDTH * HEIGHT;

// ---------------------------------------------------------------------------
// Direction
//
// Firmware best practice: use enum class, not plain enum.
//   - Plain enum leaks names into the enclosing scope (NORTH, EAST, etc.
//     become global symbols that can clash with anything else).
//   - enum class requires Direction::NORTH — explicit and impossible to
//     accidentally mix with an unrelated integer.
//   - The underlying type is fixed as uint8_t: a direction fits in one byte,
//     and we never want it silently promoted to a larger integer type.
// ---------------------------------------------------------------------------
enum class Direction : uint8_t {
    NORTH = 0,
    EAST  = 1,
    SOUTH = 2,
    WEST  = 3
};

// ---------------------------------------------------------------------------
// Lookup tables — displacement and wall bitmasks
//
// Firmware best practice: static constexpr arrays live in flash/ROM on a
// real MCU. They cost zero RAM and are evaluated entirely at compile time.
// std::array is preferred over raw C arrays because it knows its own size
// and participates in range-based for loops and STL algorithms.
// ---------------------------------------------------------------------------
inline constexpr std::array<int, 4>     DX        {  0,  1,  0, -1 };  // N E S W
inline constexpr std::array<int, 4>     DY        { -1,  0,  1,  0 };  // N E S W
inline constexpr std::array<uint8_t, 4> WALL_BITS { 0x1, 0x2, 0x4, 0x8 }; // N E S W

// ---------------------------------------------------------------------------
// RobotState — the firmware's internal model of itself and the maze
//
// Firmware best practice: no global mutable variables.
// The Python version used module-level globals (x, y, heading, walls…).
// Encapsulating everything in a struct means:
//   - Two robot instances can coexist without stepping on each other
//   - State is explicit — callers know exactly what they are touching
//   - Testing is straightforward — create an instance, poke it, assert on it
//
// Firmware best practice: no heap allocation.
// walls and walls_known use std::array with a compile-time size (CELLS).
// On a real MCU this means they live in BSS/data segment with a known,
// fixed address — no malloc, no fragmentation, no surprise out-of-memory.
// ---------------------------------------------------------------------------
struct RobotState {
    int       x       = 0;
    int       y       = 0;
    Direction heading = Direction::NORTH;

    // One byte per cell. Lower 4 bits encode wall presence (N/E/S/W).
    std::array<uint8_t, CELLS> walls       {};

    // One byte per cell. Lower 4 bits encode which walls have been sensed.
    // A set bit means we have a definitive reading for that wall direction.
    std::array<uint8_t, CELLS> walls_known {};

    // Reset all state to start-of-run defaults.
    void reset();

    // Record a wall-sensing result. present=true  → wall exists.
    //                               present=false → opening confirmed.
    // Both cases mark the wall as "known" in walls_known.
    void mark_wall(int cx, int cy, Direction dir, bool present);

    bool has_wall(int cx, int cy, Direction dir) const;
    bool is_known(int cx, int cy, Direction dir) const;

    // Convert a sensor's relative offset to an absolute heading.
    // relative_offset: -1 = left of current heading
    //                   0 = directly ahead
    //                  +1 = right of current heading
    Direction relative_to_absolute(int relative_offset) const;

private:
    // Inline so the compiler can fold it into every call site — no function
    // call overhead on a tight embedded loop.
    static constexpr int cell_index(int cx, int cy) { return cy * WIDTH + cx; }
};

} // namespace robot
