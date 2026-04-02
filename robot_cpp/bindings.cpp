#include <pybind11/pybind11.h>
#include <pybind11/functional.h>  // std::function <-> Python callable
#include <pybind11/stl.h>         // std::array / std::vector <-> Python list

#include "state.hpp"
#include "hal.hpp"
#include "wall_follower.hpp"

namespace py = pybind11;
using namespace robot;

// ---------------------------------------------------------------------------
// This is the only file that knows about pybind11.
//
// Everything in include/ and src/ is pure C++17 — it compiles and links
// independently of Python. bindings.cpp is the adapter layer that maps
// C++ types to Python objects. Keeping the two concerns separate means
// the firmware code could also be compiled into a standalone test binary
// or linked directly against real hardware drivers.
// ---------------------------------------------------------------------------

PYBIND11_MODULE(robot_cpp, m) {
    m.doc() = "C++ robot firmware — wall-follower micromouse";

    // -----------------------------------------------------------------------
    // Module-level constants
    // Exposed so sim_state.py can do: robot_cpp.DX[heading]
    // without reimplementing the lookup tables in Python.
    // -----------------------------------------------------------------------
    m.attr("WIDTH")  = WIDTH;
    m.attr("HEIGHT") = HEIGHT;

    // std::array is not directly iterable from Python; copy into a vector
    // so pybind11/stl.h converts it to a plain Python list.
    m.attr("DX") = std::vector<int>(DX.begin(), DX.end());
    m.attr("DY") = std::vector<int>(DY.begin(), DY.end());

    // -----------------------------------------------------------------------
    // Direction enum
    //
    // export_values() hoists the names into the module scope so Python code
    // can write either robot_cpp.Direction.NORTH or just robot_cpp.NORTH.
    // -----------------------------------------------------------------------
    py::enum_<Direction>(m, "Direction")
        .value("NORTH", Direction::NORTH)
        .value("EAST",  Direction::EAST)
        .value("SOUTH", Direction::SOUTH)
        .value("WEST",  Direction::WEST)
        .export_values();

    // -----------------------------------------------------------------------
    // RobotState
    //
    // Exposed so the simulation layer (hal_sim.py, sim_state.py, app.py) can
    // read x, y, heading, walls and walls_known without knowing anything
    // about the C++ internals.
    //
    // heading is exposed as a plain int (0–3) rather than the Direction enum.
    // This keeps the JSON-serialisation in app.py simple and matches the
    // original Python state module's integer representation exactly.
    //
    // walls / walls_known are exposed as Python lists of ints via pybind11/stl.
    // list(state.walls) in app.py therefore works identically to before.
    // -----------------------------------------------------------------------
    py::class_<RobotState>(m, "RobotState")
        .def(py::init<>())

        .def_readwrite("x", &RobotState::x)
        .def_readwrite("y", &RobotState::y)

        // heading: int in Python, Direction enum internally in C++
        .def_property("heading",
            [](const RobotState& s) { return static_cast<int>(s.heading); },
            [](RobotState& s, int v) { s.heading = static_cast<Direction>(v); })

        // Read-only views of the wall arrays as Python lists of ints.
        .def_property_readonly("walls", [](const RobotState& s) {
            return std::vector<uint8_t>(s.walls.begin(), s.walls.end());
        })
        .def_property_readonly("walls_known", [](const RobotState& s) {
            return std::vector<uint8_t>(s.walls_known.begin(), s.walls_known.end());
        })

        .def("reset",    &RobotState::reset)
        .def("has_wall", &RobotState::has_wall)
        .def("is_known", &RobotState::is_known)

        // Used by hal_sim.py to compute absolute sensor directions.
        // Returns an int (0–3) so the Python direction_map can use plain
        // integer keys rather than C++ enum values.
        .def("relative_to_absolute", [](const RobotState& s, int offset) {
            return static_cast<int>(s.relative_to_absolute(offset));
        });

    // -----------------------------------------------------------------------
    // Hal
    //
    // pybind11/functional.h makes std::function<bool()> accept any Python
    // callable — a plain function, a lambda, or a bound method. The Python
    // simulation layer simply assigns Python functions to these attributes.
    // -----------------------------------------------------------------------
    py::class_<Hal>(m, "Hal")
        .def(py::init<>())
        .def_readwrite("sense_left",    &Hal::sense_left)
        .def_readwrite("sense_front",   &Hal::sense_front)
        .def_readwrite("sense_right",   &Hal::sense_right)
        .def_readwrite("move_forward",  &Hal::move_forward)
        .def_readwrite("on_turn_left",  &Hal::on_turn_left)
        .def_readwrite("on_turn_right", &Hal::on_turn_right);

    // -----------------------------------------------------------------------
    // WallFollower
    //
    // Takes RobotState and Hal by reference — Python must keep those objects
    // alive for as long as the WallFollower exists.
    // py::keep_alive<1, 2> and <1, 3> enforce this: argument 2 (state) and
    // argument 3 (hal) are kept alive for at least as long as argument 1
    // (the WallFollower instance).
    // -----------------------------------------------------------------------
    py::class_<WallFollower>(m, "WallFollower")
        .def(py::init<RobotState&, Hal&>(),
             py::keep_alive<1, 2>(),   // WallFollower keeps state alive
             py::keep_alive<1, 3>())   // WallFollower keeps hal alive
        .def("run", &WallFollower::run)
        .def_property_readonly("state", &WallFollower::state,
             py::return_value_policy::reference_internal);
}
