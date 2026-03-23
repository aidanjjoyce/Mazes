from maze_generator import generate_maze
from maze_solver import dijkstra
from maze_renderer import render

if __name__ == "__main__":
    maze = generate_maze(10, 10)
    path = dijkstra(maze)
    render(maze, path)
