# Snake Game - BFS & Fruit Scoring

A little simulation "game" with snake I made a while back, showcasing some basic path finding algos, heuristics, etc etc.
Had fun, learned smth.

https://github.com/user-attachments/assets/924129e1-718c-49e2-a7d1-ef18fced720d




## Table of Contents
- [Overview](#overview)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Cool Stuff(s)](#cool-stuffs)
  - [Snake Behaviors](#snake-behaviors)
  - [Fruit Class](#fruit-class)
  - [Board Class](#board-class)
- [helpers.py](#helperspy)
  - [Heuristic Function](#heuristic-function)
  - [Fruit Scoring Function](#fruit-scoring-function)
  - [A* Pathfinding (find_path)](#a-pathfinding-find_path)
  - [BFS & Other Helper Functions](#bfs--other-helper-functions)
- [SSSSnake Behaviorssss 🐍](#ssssnake-behaviorssss-)
  - [Movement & Decision-Making](#movement--decision-making)
  - [Path Calculation Strategies](#path-calculation-strategies)
  - [Fallback "Biding Time" Mode](#fallback-biding-time-mode)


---

## Overview

This repo contains a simulation "game" that uses a snake to demonstrate several pathfinding algos (A*, BFS) and heuristics.
The snake semi-intelligently (just intelligent enough to still make mistakes sometimes and die, which is on purpose) calculates 
paths toward fruits, handles collisions, and  switches to a fallback mode ("biding time") when no safe path is available. 
The simulation runs on a toroidal board, meaning the edges wrap around (wrap-around behavior), which makes the heuristics cool and stuff.

---

## Installation & Setup

1. **Clone the Repo:**
    ```bash
       git clone https://github.com/PavelFalta/snakies.git
       cd snakies
    ```

2.  **Set up a Virtual Env (optional ig):**
    
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    
3.  **Install Dependencies:**
    
    ```bash
    pip install -r requirements.txt
    ```
    

* * *

Usage
-----

To run the simulation, use the command below. Args are as below:

```bash
python snakies.py --snakes 2 --fruits 5 --board_size 100 --tick_rate 60 --fruit_value 1 --terrain_alpha 4 --verbose --display-path --display-scores --verbose
```

or just

```bash
python snakies.py
```

*   `--snakes`: Number of snake instances.
*   `--fruits`: Number of fruits on board.
*   `--board_size`: Size of the square board (NxN).
*   `--tick_rate`: FPS or simulation tick rate.
*   `--fruit_value`: Score value for each fruit.
*   `--terrain_alpha`: Influences the snake's decision to choose a safer fruit vs. a closer one.

**Flags**:
*   `--display-path`: Display path cells.
*   `--display-scores`: Display scores above snake heads.
*   `--verbose`: Toggles verbose logging for debugging.

* * *

Cool stuff(s)
--------------
#### Snake Behaviors

*   **Key Methods:**
    
    *   **`move(fruits, board)`**  
        Checks the current path for safety. If the path is obstructed or becomes invalid (like colliding with a snake body or head), the path is reset.
        It then either continues along the current path or recalculates it.
        
    *   **`calculate_best_path(fruits, board)`**  
        Decides the best route to a fruit using a heuristic that balances distance (via wrap-around Manhattan) and fruit score (evaluated using nearby obstacles and other fruits).
        If a valid path (using A\* via the helper `find_path`) is found, it’s set as the snake's current path.
        
    *   **`calculate_bide_time_path(board)`**  
        A last resort to preserve life at all costs, activated when no safe path to a fruit is available. This method employs a BFS (breadth-first search) to explore the safe
        region around the snake’s head, then constructs a route through less crowded cells.
        This mode is tagged as "biding time" where the snake essentially waits for a better opportunity.
        
    *   **`bfs_path(start, goal, region)`**  
        A simple BFS algorithm used to connect the current position to a target cell within a defined safe region.
        It backtracks to generate the final path if a connection exists.
        Still causes lag sometimes but meh that's BFS for ya.
        

#### Fruit Class

*   **Purpose:**  
    Yummy

#### Board Class

*   **Key Responsibilities:**
    
    *   Initializing the board as a 2D grid.
    *   Randomly assigning positions to snake heads and fruits.
    *   Updating the state on each tick: checking for eaten fruits, moving snakes, managing snake trails, and handling collisions.
    *   Rendering the board using Pygame, including drawing cells for snakes, fruits, and optionally the calculated path (if `--display_path` is enabled).
    *   Logging scores and snake deaths if verbose mode is on.

### helpers.py

This module contains the actual implementation of the algorithms, some math, distances etc.

#### Heuristic Function

*   **`heuristic(a, b, board_size)`**  
    Calculates the wrap-around Manhattan distance between two points. This is crucial for A\* since the board wraps around,
    so the distance calculation must account for that.

#### Fruit Scoring Function

*   **`fruit_score(fruit_pos, board_size, board)`**  
    Scans a 5x5 area around the fruit’s position. Increases the score if other fruits are nearby (+3) and penalizes if obstacles
    (or snake parts) are close (-5). This score is used to determine which fruit is "safer" or more attractive for the snake.
    It's still a WIP for now, experimenting.

#### A\* Pathfinding (find\_path)

*   **`find_path(goal, x, y, board_size, board, allow_path=False)`**  
    Implements the A\* algo for finding the shortest path from the snake’s current position to a target (fruit or a marked cell).
    *   Uses the heuristic to estimate the remaining distance.
    *   Maintains an open heap (priority queue) to always explore the most promising cell next.
    *   If a valid path is found, returns a deque representing the sequence of moves.

#### BFS & Other Helper Functions

*   **`get_neighbors(pos, allow_path, board_size, board)`**  
    Returns neighbor cells considering whether the snake is allowed to pass through cells marked as part of its calculated path (value `4`).
    
*   **`is_passable(x, y, head, board)`**  
    Checks if a cell is passable (values `[0, 2, 4]`). Special case: the snake’s own head is always considered passable.
    
*   **`unvisited_neighbors(cx, cy, w, region, used)`**  
    For a given cell, returns neighbor cells that haven’t been visited yet in a BFS search. This is used during the "biding time" mode to explore the region.
    
*   **`bfs_is_passable(x, y, region)`**  
    Utility to determine if a cell is within the safe region during BFS exploration.
    

* * *

SSSSnake Behaviorssss 🐍
------------------------

### Movement & Decision-Making

The snake’s movement is governed by a combination of precomputed paths and real-time decision making. Each tick (yeah yaeh i know...), the snake:

*   Checks if its current path is still valid (i.e., no new obstacles like other snake bodies have appeared).
*   Moves along the path if it remains safe.
*   Updates its trail (a record of past positions) to help in rendering and collision checking.
*   If the path becomes invalid (e.g., a collision is imminent or too many obstacles are detected around the target cell), the snake recalculates a new path.

The decision-making process involves checking adjacent cells and, if the snake is near a dangerous area (too many occupied cells), 
it will drop the current path and look for alternatives.

### Path Calculation Strategies

The snake uses a couple of strategies to find the optimal route:

*   **A\* Search (find\_path):**  
    The primary method for calculating the best path to a target fruit. It balances distance (via wrap-around Manhattan distance) and the fruit’s score (via the fruit scoring function).
    The calculated path is stored in a deque and used to drive the snake’s movement.
    
*   **Fruit Sorting & Selection:**  
    Fruits are sorted using a custom key that factors in both distance and safety (using the `terrain_alpha` multiplier).
    The snake picks the fruit with the lowest combined cost and attempts to generate a path toward it.
    

### Fallback "Biding Time" Mode

Lags me tf out sometimes.

When no safe path to any fruit is available, the snake switches into a fallback mode:

*   **Biding Time:**  
    Here, a BFS is initiated to map out the accessible region from the snake’s current head position.
*   **Safe Region Mapping:**  
    The algorithm marks all reachable cells, then identifies the furthest cell within that region.
*   **Route Construction:**  
    Using both a greedy neighbor selection (based on unvisited\_neighbors) and a BFS reconnection (via bfs\_path), the snake builds a new path that might allow it to “wait out” the dangerous state until a better fruit option appears.
*   **Activation Flag:**  
    A flag (`biding_time`) is set to indicate that the snake is in this waiting mode, affecting how future decisions are made.

* * *
