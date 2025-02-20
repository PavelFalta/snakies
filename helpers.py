import heapq
from collections import deque
from functools import lru_cache

lru_cache(maxsize=None)
def heuristic(a, b, board_size):
    """
    wrap-around Manh'ttan distance on a toroidal board
    """
    return (
        min(abs(a[0] - b[0]), board_size - abs(a[0] - b[0])) +
        min(abs(a[1] - b[1]), board_size - abs(a[1] - b[1]))
    )

def fruit_score(fruit_pos, board_size, board):
    """
    scans a 5x5 area around target pos
    """
    score = 0
    fx, fy = fruit_pos
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            nx = (fx + dx) % board_size
            ny = (fy + dy) % board_size
            if dx == 0 and dy == 0:
                continue
            val = board[nx][ny]
            if val == 2:  # fruit
                score += 3
            elif val != 0:  # anything else => obstacle
                score -= 5
    return score

def get_neighbors(pos, allow_path, board_size, board):
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []
    for dx, dy in offsets:
        nx = (pos[0] + dx) % board_size
        ny = (pos[1] + dy) % board_size
        allowed = [0, 2] if not allow_path else [0, 2, 4]
        if board[nx][ny] in allowed:
            neighbors.append((nx, ny))
    return neighbors

def find_path(goal, x, y, board_size, board, allow_path=False):
    """
    A* implem
    """
    start = (x, y)
    open_heap = []
    start_h = heuristic(start, goal, board_size)
    heapq.heappush(open_heap, (start_h, 0, start))
    
    came_from = {}
    g_score = {start: 0}

    while open_heap:
        current_f, current_g, current = heapq.heappop(open_heap)
        if current == goal:

            path = deque()
            while current in came_from:
                path.appendleft(current)
                current = came_from[current]
            return path

        for neighbor in get_neighbors(current, allow_path, board_size, board):
            tentative_g_score = current_g + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal, board_size)
                heapq.heappush(open_heap, (f_score, tentative_g_score, neighbor))
    
    return None

def is_passable(x, y, head, board):
    """
    [0,2,4] passable
    """
    if (x, y) == head:
        return True
    val = board[x][y]
    return val in [0, 2, 4]

def unvisited_neighbors(cx, cy, w, region, used):
    offsets = [(-1,0), (1,0), (0,-1), (0,1)]
    result = []
    for dx, dy in offsets:
        nx = (cx + dx) % w
        ny = (cy + dy) % w
        if (nx, ny) in region and (nx, ny) not in used:
            result.append((nx, ny))
    return result

def bfs_is_passable(x, y, region):
    return (x, y) in region
