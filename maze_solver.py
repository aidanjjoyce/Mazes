import heapq
from maze_generator import DIRS, get_neighbours  # or redefine DIRS locally

def dijkstra(grid, start, end):
    width = len(grid[0])
    height = len(grid)

    dist = {start: 0}
    prev = {}
    pq = [(0, start)]  # (distance, (x, y))

    while pq:
        d, (x, y) = heapq.heappop(pq)

        if (x, y) == end:
            break

        if d > dist[(x, y)]:
            continue

        for nx, ny in get_neighbours(grid, x, y):
            nd = d + 1
            if (nx, ny) not in dist or nd < dist[(nx, ny)]:
                dist[(nx, ny)] = nd
                prev[(nx, ny)] = (x, y)
                heapq.heappush(pq, (nd, (nx, ny)))

    # Reconstruct path
    path = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()

    return path
