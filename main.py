import pygame
from generation.maze_generator import generate_maze
from simulation.hal_sim import init
from robot import wall_follower
import robot.state as state
from rendering.renderer_pygame import (
    draw_maze, draw_known_map, draw_cursor, CELL_SIZE
)

FPS = 10
PANEL_GAP = 10  # pixels between the two panels


def main():
    maze = generate_maze(15, 15)

    pygame.init()
    panel_w = maze.width * CELL_SIZE
    panel_h = maze.height * CELL_SIZE
    screen = pygame.display.set_mode((panel_w * 2 + PANEL_GAP, panel_h))
    pygame.display.set_caption("Micromouse — ground truth  |  robot's known map")
    clock = pygame.time.Clock()

    right_offset = panel_w + PANEL_GAP

    def render():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        screen.fill((150, 150, 150))  # gap colour between panels

        draw_maze(screen, maze, offset_x=0)
        draw_cursor(screen, state.x, state.y, offset_x=0)

        draw_known_map(screen, state, maze, offset_x=right_offset)
        draw_cursor(screen, state.x, state.y, offset_x=right_offset)

        pygame.display.flip()
        clock.tick(FPS)

    init(maze, on_render=render)
    wall_follower.run()

    # Hold the window open after the robot finishes
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        clock.tick(FPS)


if __name__ == "__main__":
    main()