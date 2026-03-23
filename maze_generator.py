import random

DIRS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}

OPPOSITE = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
}

class Cell:
    def __init__(self):
        self.walls = {"N": True, "S": True, "E": True, "W": True}
        self.visited = False


def make_grid(width, height):
    return [[Cell() for _ in range(width)] for _ in range(height)]


def dfs(grid, x, y):
    grid[y][x].visited = True

    directions = list(DIRS.keys())
    random.shuffle(directions)

    for d in directions:
        dx, dy = DIRS[d]
        nx, ny = x + dx, y + dy

        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            if not grid[ny][nx].visited:
                # Knock down walls
                grid[y][x].walls[d] = False
                grid[ny][nx].walls[OPPOSITE[d]] = False

                dfs(grid, nx, ny)


def add_start_end(grid):
    height = len(grid)
    width = len(grid[0])

    # Start at top-left: open north wall
    grid[0][0].walls["N"] = False

    # End at bottom-right: open east wall
    grid[height-1][width-1].walls["E"] = False

    return (0, 0), (width-1, height-1)


def render(grid, start=None, end=None, path=None):
    width = len(grid[0])
    height = len(grid)

    # Convert path to a set for O(1) lookup
    path_set = set(path) if path else set()

    # Render the north walls of the first row
    row = "+"
    for x in range(width):
        cell = grid[0][x]
        row += "---+" if cell.walls["N"] else "   +"
    print(row)

    for y in range(height):
        # Row with vertical walls
        row = ""
        for x in range(width):
            cell = grid[y][x]

            # West wall for the first cell in the row
            if x == 0:
                row += "|" if cell.walls["W"] else " "

            # Choose interior content
            if start == (x, y):
                interior = " S "
            elif end == (x, y):
                interior = " E "
            elif (x, y) in path_set:
                interior = " * "
            else:
                interior = "   "

            row += interior

            # East wall
            row += "|" if cell.walls["E"] else " "
        print(row)

        # Row with horizontal walls (south walls)
        row = "+"
        for x in range(width):
            cell = grid[y][x]
            row += "---+" if cell.walls["S"] else "   +"
        print(row)


def generate_maze(width, height):
    grid = make_grid(width, height)
    dfs(grid, 0, 0)
    start, end = add_start_end(grid)
    return grid, start, end

def get_neighbours(grid, x, y):
    height = len(grid)
    width = len(grid[0])
    cell = grid[y][x]

    for d, (dx, dy) in DIRS.items():
        if not cell.walls[d]:  # passage exists
            nx, ny = x + dx, y + dy

            # Bounds check — essential!
            if 0 <= nx < width and 0 <= ny < height:
                yield (nx, ny)
