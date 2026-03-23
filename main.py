from maze_generator import generate_maze
from maze_solver import dijkstra
from maze_renderer import render

if __name__ == "__main__":
    maze, start, end = generate_maze(10, 10)
    path = dijkstra(maze, start, end)

    render(maze, start, end, path)
