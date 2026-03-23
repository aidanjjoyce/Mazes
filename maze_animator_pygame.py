import pygame
import time
from maze_renderer_pygame import draw_maze, draw_cursor, CELL_SIZE


def _init_window(maze):
    pygame.init()
    width_px = maze.width * CELL_SIZE
    height_px = maze.height * CELL_SIZE
    screen = pygame.display.set_mode((width_px, height_px))
    pygame.display.set_caption("Maze Animation")
    return screen, pygame.time.Clock()


def _handle_quit_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return True
    return False


def _draw_frame(screen, maze, path_set, cursor):
    screen.fill((255, 255, 255))
    draw_maze(screen, maze, path_set)
    draw_cursor(screen, *cursor)
    pygame.display.flip()


def animate_path(maze, path, fps=10):
    screen, clock = _init_window(maze)
    path_set = set(path)

    for cursor in path:
        if _handle_quit_events():
            return

        _draw_frame(screen, maze, path_set, cursor)
        clock.tick(fps)

    time.sleep(1)
    pygame.quit()