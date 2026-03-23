from maze_generator import Direction

def _render_top_border(grid):
    width = len(grid[0])
    row = "+"
    for x in range(width):
        cell = grid[0][x]
        row += "---+" if cell.walls[Direction.N] else "   +"
    return row


def _render_west_wall(cell):
    return "|" if cell.walls[Direction.W] else " "


def _render_cell_interior(x, y, start, end, path_set):
    if start == (x, y):
        return " S "
    if end == (x, y):
        return " E "
    if (x, y) in path_set:
        return " * "
    return "   "


def _render_east_wall(cell):
    return "|" if cell.walls[Direction.E] else " "


def _render_west_wall_if_first_cell(x, cell):
    if x == 0:
        return _render_west_wall(cell)
    return ""


def _render_cell_row(grid, y, start, end, path_set):
    width = len(grid[0])
    row = ""

    for x in range(width):
        cell = grid[y][x]

        row += _render_west_wall_if_first_cell(x, cell)
        row += _render_cell_interior(x, y, start, end, path_set)
        row += _render_east_wall(cell)

    return row


def _render_bottom_of_row(grid, y):
    width = len(grid[0])
    row = "+"
    for x in range(width):
        cell = grid[y][x]
        row += "---+" if cell.walls[Direction.S] else "   +"
    return row


def render(grid, start=None, end=None, path=None):
    height = len(grid)
    path_set = set(path) if path else set()

    print(_render_top_border(grid))

    for y in range(height):
        print(_render_cell_row(grid, y, start, end, path_set))
        print(_render_bottom_of_row(grid, y))
