import random
from enum import Enum

class Direction(Enum):
    N = (0, -1)
    S = (0, 1)
    E = (1, 0)
    W = (-1, 0)

    @property
    def dx(self):
        return self.value[0]

    @property
    def dy(self):
        return self.value[1]

    @property
    def opposite(self):
        return {
            Direction.N: Direction.S,
            Direction.S: Direction.N,
            Direction.E: Direction.W,
            Direction.W: Direction.E,
        }[self]

class Cell:
    def __init__(self):
        self.walls = {d: True for d in Direction}
        self.visited = False


def make_grid(width, height):
    return [[Cell() for _ in range(width)] for _ in range(height)]


def dfs(grid, x, y):
    grid[y][x].visited = True

    directions = list(Direction)
    random.shuffle(directions)

    for d in directions:
        nx = x + d.dx
        ny = y + d.dy

        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            if not grid[ny][nx].visited:
                # Knock down walls
                grid[y][x].walls[d] = False
                grid[ny][nx].walls[d.opposite] = False

                dfs(grid, nx, ny)


def add_start_end(grid):
    height = len(grid)
    width = len(grid[0])

    # Start at top-left: open north wall
    grid[0][0].walls[Direction.N] = False

    # End at bottom-right: open east wall
    grid[height-1][width-1].walls[Direction.E] = False

    return (0, 0), (width-1, height-1)

def generate_maze(width, height):
    grid = make_grid(width, height)
    dfs(grid, 0, 0)
    start, end = add_start_end(grid)
    return grid, start, end

def get_neighbours(grid, x, y):
    height = len(grid)
    width = len(grid[0])
    cell = grid[y][x]

    for d in Direction:
        if not cell.walls[d]:
            nx = x + d.dx
            ny = y + d.dy
            if 0 <= nx < width and 0 <= ny < height:
                yield nx, ny
