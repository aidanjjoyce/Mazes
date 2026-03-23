from generation.maze_generator import Direction

def _render_top_border(maze):
    row = "+"
    for x in range(maze.width):
        cell = maze.cell_at(x, 0)
        row += "---+" if cell.walls[Direction.N] else "   +"
    return row


def _render_west_wall(cell):
    return "|" if cell.walls[Direction.W] else " "


def _render_east_wall(cell):
    return "|" if cell.walls[Direction.E] else " "


def _render_west_wall_if_first_cell(x, cell):
    return _render_west_wall(cell) if x == 0 else ""


def _render_cell_interior(x, y, maze, path_set):
    if maze.start == (x, y):
        return " S "
    if maze.end == (x, y):
        return " E "
    if (x, y) in path_set:
        return " * "
    return "   "


def _render_cell_row(maze, y, path_set):
    row = ""
    for x in range(maze.width):
        cell = maze.cell_at(x, y)
        row += _render_west_wall_if_first_cell(x, cell)
        row += _render_cell_interior(x, y, maze, path_set)
        row += _render_east_wall(cell)
    return row


def _render_bottom_of_row(maze, y):
    row = "+"
    for x in range(maze.width):
        cell = maze.cell_at(x, y)
        row += "---+" if cell.walls[Direction.S] else "   +"
    return row


def render(maze, path=None):
    path_set = set(path) if path else set()

    print(_render_top_border(maze))

    for y in range(maze.height):
        print(_render_cell_row(maze, y, path_set))
        print(_render_bottom_of_row(maze, y))
