import random
import pygame
from collections import deque
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

# helpers thumbs up
from helpers import (
    heuristic,
    fruit_score,
    find_path,
    unvisited_neighbors,
    is_passable
)


class Snake:
    def __init__(self, board_size, terrain_alpha):
        self.x = None
        self.y = None
        
        self.trail = deque()
        self.score = 0
        self.board_size = board_size
        self.terrain_alpha = terrain_alpha
        self.path = deque()
        self.delete = False
        self.biding_time = False

        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

        self.proposed = None
    
    def move(self, fruits, board):
        for move_cell in self.path:
            if board[move_cell[0]][move_cell[1]] not in [0, 2, 4]:
                self.path = deque()
                break
        
        if self.path:
            target_location = self.path[-1]
            body_count = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx = (target_location[0] + dx) % self.board_size
                    ny = (target_location[1] + dy) % self.board_size
                    if board[nx][ny] not in [0, 2, 4]:
                        body_count += 1
            if body_count >= 5 and not self.biding_time:
                self.path = deque()

        if not self.path:
            self.calculate_best_path(fruits, board)
        
        self.trail.append((self.x, self.y))
        if len(self.trail) >= self.score:
            self.trail.popleft()
        
        if self.path:
            move_cell = self.path.popleft()
            if board[move_cell[0]][move_cell[1]] in [1, 3]:  # occupied by snake body or another head
                self.delete = True
            self.proposed = move_cell

    def calculate_best_path(self, fruits, board):
        """
        which fruit da best using a fruit-scoring heuristic.
        """
        self.biding_time = False
        if not fruits:
            return
        
        def fruit_sort_key(fruit):
            dist = heuristic((self.x, self.y), (fruit.x, fruit.y), self.board_size)
            score = fruit_score((fruit.x, fruit.y), board_size=self.board_size, board=board)

            return dist - self.terrain_alpha  * score

        sorted_fruits = sorted(fruits.values(), key=fruit_sort_key)

        for fruit in sorted_fruits:
            path_found = find_path(
                goal=(fruit.x, fruit.y),
                x=self.x,
                y=self.y,
                board_size=self.board_size,
                board=board,
                allow_path=False
            )
            if path_found:
                self.path = path_found
                return
            
        for row_idx, row_val in enumerate(board):
            for col_idx, cell_val in enumerate(row_val):
                if cell_val == 4:
                    path_found = find_path(
                        goal=(col_idx, row_idx),
                        x=self.x,
                        y=self.y,
                        board_size=self.board_size,
                        board=board,
                        allow_path=True
                    )
                    if path_found:
                        self.path = path_found
                        return

        self.path = self.calculate_bide_time_path(board)
        if not self.path:
            self.delete = True

    def calculate_bide_time_path(self, board):
        board_size = self.board_size
        head = (self.x, self.y)

        visited = [[False] * board_size for _ in range(board_size)]
        distance_map = [[-1] * board_size for _ in range(board_size)]
        q = deque()

        sx, sy = head
        visited[sx][sy] = True
        distance_map[sx][sy] = 0
        q.append((sx, sy))

        while q:
            cx, cy = q.popleft()
            cd = distance_map[cx][cy]
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx = (cx + dx) % board_size
                ny = (cy + dy) % board_size
                if not visited[nx][ny] and is_passable(nx, ny, head, board):
                    visited[nx][ny] = True
                    distance_map[nx][ny] = cd + 1
                    q.append((nx, ny))

        region = {(x, y) for x in range(board_size) for y in range(board_size) if visited[x][y]}
        if len(region) <= 1:
            return deque()

        furthest_cell = max(region, key=lambda c: distance_map[c[0]][c[1]])

        route = []
        used = set()
        route.append(head)
        used.add(head)
        current = head

        while True:
            nbrs = unvisited_neighbors(current[0], current[1], board_size, region, used)
            if not nbrs:
                break

            best_nbr = None
            best_count = float('inf')
            for n in nbrs:
                n_nbrs = unvisited_neighbors(n[0], n[1], board_size, region, used)
                if len(n_nbrs) < best_count:
                    best_count = len(n_nbrs)
                    best_nbr = n
            route.append(best_nbr)
            used.add(best_nbr)
            current = best_nbr

        end_pos = current
        if end_pos != furthest_cell:
            maybe_path = self.bfs_path(end_pos, furthest_cell, region)
            if maybe_path:
                route.extend(maybe_path[1:])

        if len(route) <= 1:
            return deque()

        self.biding_time = True
        return deque(route[1:])

    def bfs_path(self, start, goal, region):
        if start == goal:
            return [start]

        board_size = self.board_size
        visited = [[False] * board_size for _ in range(board_size)]
        came_from = dict()

        sx, sy = start
        gx, gy = goal

        queue = deque()
        queue.append((sx, sy))
        visited[sx][sy] = True
        came_from[(sx, sy)] = None

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == (gx, gy):

                path = []
                cur = (gx, gy)
                while cur is not None:
                    path.append(cur)
                    cur = came_from[cur]
                path.reverse()
                return path

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx = (cx + dx) % board_size
                ny = (cy + dy) % board_size
                if not visited[nx][ny] and (nx, ny) in region:
                    visited[nx][ny] = True
                    came_from[(nx, ny)] = (cx, cy)
                    queue.append((nx, ny))

        return None


class Fruit:
    def __init__(self, board_size, x=None, y=None):
        if x is None or y is None:
            self.x = random.randint(0, board_size - 1)
            self.y = random.randint(0, board_size - 1)
        else:
            self.x = x
            self.y = y


class Board:
    def __init__(self, args):
        self.board_size = args.board_size
        self.num_fruits = args.fruits
        self.fruit_value = args.fruit_value
        self.display_path = args.display_path
        self.display_scores = args.display_scores
        self.verbose = args.verbose
        self.num_snakes = args.snakes
        self.terrain_alpha = args.terrain_alpha

        self.state = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        pygame.display.set_caption('Snake Game - BFS & Fruit Scoring')
        self.screen = pygame.display.set_mode((self.board_size * 10, self.board_size * 10))
        
        self.font = pygame.font.SysFont(None, 25, bold=True)

        self.fruits = {}
        self.snakes = [Snake(self.board_size, self.terrain_alpha) for _ in range(self.num_snakes)]
        
        self.c = 0
        self.best = 0

        for snake in self.snakes:
            sx, sy = self.get_random_free_cell()
            snake.x, snake.y = sx, sy
            self.state[sx][sy] = 3  # head

        while len(self.fruits) < self.num_fruits:
            self.c += 1
            fx, fy = self.get_random_free_cell()
            self.fruits[self.c] = Fruit(self.board_size, fx, fy)
            self.state[fx][fy] = 2

    def get_random_free_cell(self):
        # the best algorithm eva
        while True:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if self.state[x][y] == 0:
                return x, y

    def update(self):
        self.state = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

        fruit_mask = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

        for f_id, fruit in self.fruits.items():
            self.state[fruit.x][fruit.y] = 2
            fruit_mask[fruit.x][fruit.y] = 2

        eaten_fruits = []
        for f_id, fruit in self.fruits.items():
            for snake in self.snakes:
                if snake.x == fruit.x and snake.y == fruit.y:
                    eaten_fruits.append(f_id)
                    snake.score += self.fruit_value
                    break
        for f_id in eaten_fruits:
            del self.fruits[f_id]

        for snake in self.snakes:
            for (px, py) in snake.path:
                self.state[px][py] = 4

        for snake in self.snakes:
            for (bx, by) in snake.trail:
                self.state[bx][by] = snake.color
            self.state[snake.x][snake.y] = 3

        to_delete = []
        for i, snake in enumerate(self.snakes):
            snake.move(self.fruits, self.state)
            if snake.delete:
                to_delete.append(i)
        
        for i, snake in enumerate(self.snakes):
            for j, other_snake in enumerate(self.snakes):
                if i != j and snake.proposed and other_snake.proposed:
                    if other_snake.proposed == snake.proposed:
                        # Resolve tie by score
                        if snake.score > other_snake.score:
                            other_snake.delete = True
                        else:
                            snake.delete = True
                # ded :(
                if snake.proposed and self.state[snake.proposed[0]][snake.proposed[1]] not in [0, 2, 4]:
                    snake.delete = True

            if not snake.delete and snake.proposed:
                snake.x, snake.y = snake.proposed

        for idx in reversed(to_delete):
            dead_snake = self.snakes[idx]
            if dead_snake.score > self.best:
                self.best = dead_snake.score
                if self.verbose:
                    logging.info(f"New best score: {self.best}")
            self.snakes.pop(idx)
            if self.verbose:
                logging.info("Snake died.")
            
            # respw
            new_snake = Snake(self.board_size, self.terrain_alpha)
            sx, sy = self.get_random_free_cell()
            new_snake.x, new_snake.y = sx, sy
            self.snakes.append(new_snake)

        while len(self.fruits) < self.num_fruits:
            self.c += 1
            fx, fy = self.get_random_free_cell()
            self.fruits[self.c] = Fruit(self.board_size, fx, fy)
            self.state[fx][fy] = 2
        
        for i in range(self.board_size):
            for j in range(self.board_size):
                if fruit_mask[i][j] == 2:
                    self.state[i][j] = 2
            

    def draw(self):
        """
        Render the board. Also draw each snake's score above its head.
        """
        self.screen.fill((0, 0, 0))
        cell_size = 10
        
        for y, row in enumerate(self.state):
            for x, cell in enumerate(row):
                if cell == 2:  # fruit
                    color = (255, 0, 0)
                elif cell == 3:  # snake head
                    color = (0, 255, 0)
                elif cell == 4 and self.display_path:  # path
                    color = (255, 255, 255)
                elif isinstance(cell, tuple):  # snake body color
                    color = cell
                else:  # empty
                    color = (0, 0, 0)

                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                )

        if self.display_scores:
            for snake in self.snakes:

                score_surface = self.font.render(str(snake.score), True, (255, 255, 255))

                snake_head_x = snake.x * cell_size
                snake_head_y = snake.y * cell_size
                self.screen.blit(score_surface, (snake_head_y, snake_head_x - 20))

        pygame.display.flip()


def main():
    parser = argparse.ArgumentParser(description="fun lil' guys runnin' round.")
    parser.add_argument("--snakes", type=int, default=2, help="Number of snakes")
    parser.add_argument("--fruits", type=int, default=5, help="Number of fruits")
    parser.add_argument("--board_size", type=int, default=100, help="Board size (NxN)")
    parser.add_argument("--tick_rate", type=int, default=60, help="Game tick rate")
    parser.add_argument("--fruit_value", type=int, default=1, help="Score value of each fruit")
    parser.add_argument("--terrain_alpha", type=float, default=4, help="The higher this value, the more likely a snake will go for a safer rather than closer fruit. In theory")
    
    parser.add_argument("--display_path", action="store_true", help="Display path cells")
    parser.add_argument("--display_scores", action="store_true", help="Display scores above snake heads")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    args = parser.parse_args()

    pygame.init()
    clock = pygame.time.Clock()

    board = Board(args)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        board.update()
        board.draw()
        clock.tick(args.tick_rate)

    pygame.quit()


if __name__ == "__main__":
    main()
