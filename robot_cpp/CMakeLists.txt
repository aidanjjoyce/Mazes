# To build:
#   cd robot_cpp
#   mkdir build && cd build
#   cmake ..
#   cmake --build . --config Release
#
# The compiled robot_cpp.pyd will be placed in the project root (Mazes/)
# and can then be imported directly by the Python simulation code.
#
# Prerequisites:
#   pip install pybind11

cmake_minimum_required(VERSION 3.15)
project(robot_cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- Locate Python then use it to find pybind11's cmake dir ---
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

execute_process(
    COMMAND ${Python3_EXECUTABLE} -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

find_package(pybind11 CONFIG REQUIRED)

# --- The extension module ---
pybind11_add_module(robot_cpp
    src/state.cpp
    src/wall_follower.cpp
    bindings.cpp
)

target_include_directories(robot_cpp PRIVATE include/)

# --- Output the .pyd directly into the project root (Mazes/) ---
# On Windows pybind11 modules are DLLs, so RUNTIME governs the .pyd location.
set(OUTPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/..")

set_target_properties(robot_cpp PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY         "${OUTPUT_DIR}"
    LIBRARY_OUTPUT_DIRECTORY         "${OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG   "${OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${OUTPUT_DIR}"
    LIBRARY_OUTPUT_DIRECTORY_DEBUG   "${OUTPUT_DIR}"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE "${OUTPUT_DIR}"
)
