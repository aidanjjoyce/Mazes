# Maze dimensions
# These would be fixed at compile time in real firmware
WIDTH = 15
HEIGHT = 15

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

# Wall bit flags
WALL_N = 0b0001
WALL_E = 0b0010
WALL_S = 0b0100
WALL_W = 0b1000

WALL_BITS = [WALL_N, WALL_E, WALL_S, WALL_W]

# Displacement when moving forward for each heading
DX = [0, 1, 0, -1]  # N, E, S, W
DY = [-1, 0, 1, 0]  # N, E, S, W


# Internal firmware model state
x = 0
y = 0
heading = NORTH

# One byte per cell. Lower 4 bits encode known walls.
# 0 means "no wall known"
# Unknown and absent are not distinguished yet.
walls = bytearray(WIDTH * HEIGHT)


def reset():
    global x, y, heading
    x = 0
    y = 0
    heading = NORTH
    for i in range(len(walls)):
        walls[i] = 0


def cell_index(cx, cy):
    return cy * WIDTH + cx


def mark_wall(cx, cy, absolute_direction):
    walls[cell_index(cx, cy)] |= WALL_BITS[absolute_direction]


def has_wall(cx, cy, absolute_direction):
    return bool(walls[cell_index(cx, cy)] & WALL_BITS[absolute_direction])


def relative_to_absolute(relative_offset):
    """
    Convert a sensor's relative direction to an absolute heading.
    relative_offset: -1 = left, 0 = front, +1 = right
    """
    return (heading + relative_offset) % 4