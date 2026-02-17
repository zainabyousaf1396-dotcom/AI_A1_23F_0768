"""
AI Pathfinder
"""

import tkinter as tk
from tkinter import ttk
import random
import heapq
from collections import deque

# -----------------------
# SETTINGS
# -----------------------
ROWS = 20
CELL = 30
WIDTH = ROWS * CELL
DELAY = 30  # Faster animation
OBSTACLE_PROB = 0.015  # Reduced probability

# Colors
WHITE = "#FFFFFF"
BLACK = "#000000"
BLUE = "#4A90E2"
YELLOW = "#FFD700"
GREEN = "#50C878"
RED = "#E74C3C"
PURPLE = "#9B59B6"
GREY = "#CCCCCC"
ORANGE = "#FF8C00"

# Global variables
grid = None
start = None
end = None
running = False

# -----------------------
# NODE CLASS
# -----------------------
class Node:
    def __init__(self, r, c):
        self.row = r
        self.col = c
        self.color = WHITE
        self.is_dynamic = False

    def is_wall(self):
        return self.color == BLACK

    def __eq__(self, other):
        return isinstance(other, Node) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))
    
    def __lt__(self, other):
        return False


# -----------------------
# GRID FUNCTIONS
# -----------------------
def make_grid():
    return [[Node(r, c) for c in range(ROWS)] for r in range(ROWS)]


def reset_grid():
    global grid, start, end
    grid = make_grid()
    start = grid[0][0]
    end = grid[ROWS-1][ROWS-1]
    start.color = GREEN
    end.color = RED
    
    # Static wall
    for i in range(5, 15):
        grid[i][10].color = BLACK
    
    draw_grid("Click a button to start")


def draw_grid(title=""):
    canvas.delete("all")
    
    for row in grid:
        for node in row:
            x1 = node.col * CELL
            y1 = node.row * CELL
            x2 = x1 + CELL
            y2 = y1 + CELL
            canvas.create_rectangle(x1, y1, x2, y2, fill=node.color, outline=GREY)
    
    canvas.create_text(WIDTH//2, 15, text=title, font=("Arial", 12, "bold"))
    root.update()


def get_neighbors(node):
    directions = [
        (-1, 0), (0, 1), (1, 0), (1, 1),
        (0, -1), (-1, -1), (-1, 1), (1, -1)
    ]
    
    neighbors = []
    for dr, dc in directions:
        r = node.row + dr
        c = node.col + dc
        if 0 <= r < ROWS and 0 <= c < ROWS and not grid[r][c].is_wall():
            neighbors.append(grid[r][c])
    
    return neighbors


def add_dynamic():
    if random.random() < OBSTACLE_PROB:
        r = random.randint(0, ROWS-1)
        c = random.randint(0, ROWS-1)
        node = grid[r][c]
        if node != start and node != end and node.color == WHITE:
            node.color = BLACK
            node.is_dynamic = True


def reconstruct(parent, end_node, title):
    path = []
    current = end_node
    while current in parent:
        current = parent[current]
        if current != start:
            path.append(current)
    
    for node in reversed(path):
        node.color = PURPLE
        draw_grid(title)
        root.after(DELAY)
        root.update()


# -----------------------
# ALGORITHMS
# -----------------------
def bfs():
    status_label.config(text="Running BFS...", fg="blue")
    root.update()
    
    queue = deque([start])
    visited = {start}
    parent = {}

    while queue:
        root.after(DELAY)
        root.update()
        add_dynamic()

        current = queue.popleft()

        if current == end:
            reconstruct(parent, end, "BFS - Path Found!")
            status_label.config(text="BFS - Complete!", fg="green")
            return

        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
                if neighbor != end:
                    neighbor.color = BLUE

        if current != start and current != end:
            current.color = YELLOW

        draw_grid("BFS - Searching...")
    
    status_label.config(text="BFS - No path found", fg="red")


def dfs():
    status_label.config(text="Running DFS...", fg="blue")
    root.update()
    
    stack = [start]
    visited = {start}
    parent = {}

    while stack:
        root.after(DELAY)
        root.update()
        add_dynamic()

        current = stack.pop()

        if current == end:
            reconstruct(parent, end, "DFS - Path Found!")
            status_label.config(text="DFS - Complete!", fg="green")
            return

        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)
                if neighbor != end:
                    neighbor.color = BLUE

        if current != start and current != end:
            current.color = YELLOW

        draw_grid("DFS - Searching...")
    
    status_label.config(text="DFS - No path found", fg="red")


def ucs():
    status_label.config(text="Running UCS...", fg="blue")
    root.update()
    
    pq = [(0, id(start), start)]
    parent = {}
    cost = {start: 0}

    while pq:
        root.after(DELAY)
        root.update()
        add_dynamic()

        current_cost, _, current = heapq.heappop(pq)

        if current == end:
            reconstruct(parent, end, "UCS - Path Found!")
            status_label.config(text="UCS - Complete!", fg="green")
            return

        for neighbor in get_neighbors(current):
            if abs(neighbor.row - current.row) == 1 and abs(neighbor.col - current.col) == 1:
                step_cost = 1.414
            else:
                step_cost = 1.0

            new_cost = current_cost + step_cost

            if neighbor not in cost or new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                parent[neighbor] = current
                heapq.heappush(pq, (new_cost, id(neighbor), neighbor))
                if neighbor != end:
                    neighbor.color = BLUE

        if current != start and current != end:
            current.color = YELLOW

        draw_grid("UCS - Searching...")
    
    status_label.config(text="UCS - No path found", fg="red")


def dls():
    status_label.config(text="Running DLS...", fg="blue")
    root.update()
    
    limit = 15
    stack = [(start, 0)]
    parent = {}
    visited = {start}

    while stack:
        root.after(DELAY)
        root.update()
        add_dynamic()

        current, depth = stack.pop()

        if current == end:
            reconstruct(parent, end, "DLS - Path Found!")
            status_label.config(text="DLS - Complete!", fg="green")
            return

        if depth < limit:
            for neighbor in get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    stack.append((neighbor, depth + 1))
                    if neighbor != end:
                        neighbor.color = BLUE

        if current != start and current != end:
            current.color = YELLOW

        draw_grid(f"DLS - Searching (Limit: {limit})...")
    
    status_label.config(text="DLS - No path found", fg="red")


def iddfs():
    status_label.config(text="Running IDDFS...", fg="blue")
    root.update()
    
    for depth in range(1, 16):
        reset_grid()
        stack = [(start, 0)]
        parent = {}
        visited = {start}

        while stack:
            root.after(DELAY)
            root.update()
            add_dynamic()

            current, d = stack.pop()

            if current == end:
                reconstruct(parent, end, f"IDDFS - Path Found (Depth {depth})!")
                status_label.config(text=f"IDDFS - Complete (Depth {depth})!", fg="green")
                return

            if d < depth:
                for neighbor in get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        parent[neighbor] = current
                        stack.append((neighbor, d + 1))
                        if neighbor != end:
                            neighbor.color = BLUE

            if current != start and current != end:
                current.color = YELLOW

            draw_grid(f"IDDFS - Depth {depth}...")
    
    status_label.config(text="IDDFS - No path found", fg="red")


def bidirectional():
    status_label.config(text="Running Bidirectional...", fg="blue")
    root.update()
    
    q1, q2 = deque([start]), deque([end])
    parent1, parent2 = {}, {}
    visited1, visited2 = {start}, {end}

    while q1 and q2:
        root.after(DELAY)
        root.update()
        add_dynamic()

        if q1:
            current1 = q1.popleft()
            if current1 in visited2:
                # Path found
                path1 = []
                current = current1
                while current in parent1:
                    current = parent1[current]
                    if current != start:
                        path1.append(current)
                
                path2 = []
                current = current1
                while current in parent2:
                    current = parent2[current]
                    if current != end:
                        path2.append(current)
                
                for node in reversed(path1):
                    node.color = PURPLE
                    draw_grid("Bidirectional - Path Found!")
                    root.after(DELAY)
                    root.update()
                
                if current1 != start and current1 != end:
                    current1.color = PURPLE
                    draw_grid("Bidirectional - Path Found!")
                    root.after(DELAY)
                    root.update()
                
                for node in path2:
                    node.color = PURPLE
                    draw_grid("Bidirectional - Path Found!")
                    root.after(DELAY)
                    root.update()
                
                status_label.config(text="Bidirectional - Complete!", fg="green")
                return
            
            for neighbor in get_neighbors(current1):
                if neighbor not in visited1:
                    visited1.add(neighbor)
                    parent1[neighbor] = current1
                    q1.append(neighbor)
                    if neighbor != end and neighbor not in visited2:
                        neighbor.color = BLUE

            if current1 != start and current1 != end:
                current1.color = YELLOW

        if q2:
            current2 = q2.popleft()
            if current2 in visited1:
                status_label.config(text="Bidirectional - Complete!", fg="green")
                return
            
            for neighbor in get_neighbors(current2):
                if neighbor not in visited2:
                    visited2.add(neighbor)
                    parent2[neighbor] = current2
                    q2.append(neighbor)
                    if neighbor != start and neighbor not in visited1:
                        neighbor.color = ORANGE

            if current2 != start and current2 != end:
                current2.color = YELLOW

        draw_grid("Bidirectional - Searching...")
    
    status_label.config(text="Bidirectional - No path found", fg="red")


# -----------------------
# BUTTON HANDLERS
# -----------------------
def run_algorithm(algo_func):
    reset_grid()
    root.after(100, algo_func)


# -----------------------
# GUI SETUP
# -----------------------
root = tk.Tk()
root.title("PathFinder")
root.resizable(False, False)

# Main frame
main_frame = tk.Frame(root, bg="white")
main_frame.pack(padx=10, pady=10)

# Canvas
canvas = tk.Canvas(main_frame, width=WIDTH, height=WIDTH, bg="white")
canvas.pack()

# Status label
status_label = tk.Label(main_frame, text="Ready - Click a button to start", 
                        font=("Arial", 11), fg="blue", bg="white")
status_label.pack(pady=5)

# Button frame
button_frame = tk.Frame(root, bg="lightgray")
button_frame.pack(fill="x", padx=10, pady=5)

# Create buttons
buttons = [
    ("BFS", bfs, "#4A90E2"),
    ("DFS", dfs, "#E74C3C"),
    ("UCS", ucs, "#50C878"),
    ("DLS", dls, "#9B59B6"),
    ("IDDFS", iddfs, "#FF8C00"),
    ("Bidirectional", bidirectional, "#E91E63"),
    ("RESET", reset_grid, "#607D8B")
]

for text, command, color in buttons:
    if text == "RESET":
        btn = tk.Button(button_frame, text=text, command=command,
                       bg=color, fg="white", font=("Arial", 10, "bold"),
                       width=12, height=2, relief="raised")
    else:
        btn = tk.Button(button_frame, text=text, 
                       command=lambda cmd=command: run_algorithm(cmd),
                       bg=color, fg="white", font=("Arial", 10, "bold"),
                       width=12, height=2, relief="raised")
    btn.pack(side="left", padx=3)

# Legend
legend_frame = tk.Frame(root, bg="white")
legend_frame.pack(pady=5)

legend_items = [
    ("Start", GREEN), ("End", RED), ("Wall", BLACK),
    ("Frontier", BLUE), ("Explored", YELLOW), ("Path", PURPLE)
]

for text, color in legend_items:
    frame = tk.Frame(legend_frame, bg="white")
    frame.pack(side="left", padx=8)
    
    box = tk.Canvas(frame, width=20, height=20, bg="white", highlightthickness=0)
    box.create_rectangle(2, 2, 18, 18, fill=color, outline="gray")
    box.pack(side="left")
    
    label = tk.Label(frame, text=text, font=("Arial", 9), bg="white")
    label.pack(side="left", padx=3)

# Initialize
reset_grid()

# Start
root.mainloop()