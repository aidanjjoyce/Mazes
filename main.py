from generation.maze_generator import generate_maze
from solving.solver_dijkstra import dijkstra
from animation.animator_pygame import animate_path

def main():
    maze = generate_maze(15, 15)
    path = dijkstra(maze)
    animate_path(maze, path, fps=10)

if __name__ == "__main__":
    main()
