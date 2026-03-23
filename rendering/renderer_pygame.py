import pygame
from generation.maze_generator import Direction

CELL_SIZE = 20
WALL_COLOR = (0, 0, 0)
CELL_COLOR = (240, 240, 240)
CURSOR_COLOR = (255, 0, 0)
START_COLOR = (0, 200, 0)
END_COLOR = (0, 0, 200)
PATH_COLOR = (200, 200, 0)


def _cell_pixel_coords(x, y):
    return x * CELL_SIZE, y * CELL_SIZE


def _draw_cell_background(screen, px, py):
    pygame.draw.rect(screen, CELL_COLOR, (px, py, CELL_SIZE, CELL_SIZE))


def _draw_cell_walls(screen, cell, px, py):
    if cell.walls[Direction.N]:
        pygame.draw.line(screen, WALL_COLOR, (px, py), (px + CELL_SIZE, py), 2)
    if cell.walls[Direction.S]:
        pygame.draw.line(screen, WALL_COLOR, (px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE), 2)
    if cell.walls[Direction.W]:
        pygame.draw.line(screen, WALL_COLOR, (px, py), (px, py + CELL_SIZE), 2)
    if cell.walls[Direction.E]:
        pygame.draw.line(screen, WALL_COLOR, (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE), 2)


def _draw_path_marker(screen, px, py):
    pygame.draw.rect(screen, PATH_COLOR, (px + 4, py + 4, CELL_SIZE - 8, CELL_SIZE - 8))


def _draw_start_marker(screen, px, py):
    pygame.draw.rect(screen, START_COLOR, (px + 4, py + 4, CELL_SIZE - 8, CELL_SIZE - 8))


def _draw_end_marker(screen, px, py):
    pygame.draw.rect(screen, END_COLOR, (px + 4, py + 4, CELL_SIZE - 8, CELL_SIZE - 8))


def draw_maze(screen, maze, path_set=None):
    if path_set is None:
        path_set = set()

    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.cell_at(x, y)
            px, py = _cell_pixel_coords(x, y)

            _draw_cell_background(screen, px, py)
            _draw_cell_walls(screen, cell, px, py)

            if (x, y) in path_set:
                _draw_path_marker(screen, px, py)

            if (x, y) == maze.start:
                _draw_start_marker(screen, px, py)

            if (x, y) == maze.end:
                _draw_end_marker(screen, px, py)


def draw_cursor(screen, x, y):
    px, py = _cell_pixel_coords(x, y)
    pygame.draw.rect(screen, CURSOR_COLOR, (px + 4, py + 4, CELL_SIZE - 8, CELL_SIZE - 8))