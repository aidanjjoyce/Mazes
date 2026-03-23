import heapq

def dijkstra(maze):
    start = maze.start
    end = maze.end

    dist = {start: 0}
    prev = {}
    pq = [(0, start)]  # (distance, (x, y))

    while pq:
        d, (x, y) = heapq.heappop(pq)

        if (x, y) == end:
            break

        if d > dist[(x, y)]:
            continue

        for nx, ny in maze.neighbours(x, y):
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
