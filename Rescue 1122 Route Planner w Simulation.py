import pygame
from queue import PriorityQueue

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Rescue 1122: ROUTE MODE (Click to add Stops)")

# --- COLOR DEFINITIONS ---
RED = (255, 0, 0)       # Closed nodes (visited)
GREEN = (0, 255, 0)     # Open nodes (in queue)
YELLOW = (255, 255, 0)  # The final path
WHITE = (255, 255, 255) # Empty node
BLACK = (0, 0, 0)       # Barrier/Wall
ORANGE = (255, 165, 0)  # Start node
GREY = (128, 128, 128)  # Grid lines
TURQUOISE = (64, 224, 208) # End node
PURPLE = (128, 0, 128)  # [ADDTL FEATURE] Waypoints

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    # --- STATE CHECKS ---
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    # --- STATE SETTERS ---
    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        # Only change color if it isn't part of the permanent route
        if self.color != YELLOW and self.color != ORANGE and self.color != PURPLE and self.color != TURQUOISE:
            self.color = RED

    def make_open(self):
        # Only change color if it isn't part of the permanent route
        if self.color != YELLOW and self.color != ORANGE and self.color != PURPLE and self.color != TURQUOISE:
            self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Check DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Check UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Check RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Check LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path() # Turns the node YELLOW
        draw()

def A_star_algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end() 
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open() 

        draw()

        if current != start:
            current.make_closed() 

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = x // gap
    col = y // gap
    return row, col

def main(win, width):
    ROWS = 30
    grid = make_grid(ROWS, width)
    
    stops = [] 
    
    # [NEW FLAG] This determines if we are adding Routes or Walls
    drawing_walls = False 

    run = True
    while run:
        draw(win, grid, ROWS, width)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # --- LEFT MOUSE CLICK ---
            if pygame.mouse.get_pressed()[0]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                # MODE 1: DRAWING WALLS (If 'B' was pressed)
                if drawing_walls:
                    # You can only place a wall if it's not already a Stop/Start/End
                    if node not in stops:
                        node.make_barrier()

                # MODE 2: DRAWING ROUTE (Default)
                else:
                    if not node.is_barrier() and node not in stops:
                        stops.append(node) 
                        
                        # Color Logic
                        if len(stops) == 1:
                            node.make_start()   # First is Start (ORANGE)
                        else:
                            node.make_end()     # Newest is End (TURQUOISE)
                            
                            # If we have 3+ nodes, the one BEFORE the new End becomes a Waypoint (PURPLE)
                            if len(stops) > 2:
                                stops[-2].color = PURPLE
                            # If we have exactly 2 nodes, ensure Start is still Orange
                            if len(stops) == 2:
                                stops[0].make_start()

            # --- RIGHT MOUSE CLICK (Remove items) ---
            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                if node in stops:
                    stops.remove(node)
                    node.reset()
                    
                    # Re-color remaining stops
                    for i, stop_node in enumerate(stops):
                        if i == 0:
                            stop_node.make_start()
                        elif i == len(stops) - 1:
                            stop_node.make_end()
                        else:
                            stop_node.color = PURPLE
                else:
                    node.reset()

            # --- KEYBOARD CONTROLS ---
            if event.type == pygame.KEYDOWN:
                
                # [NEW FEATURE] Toggle Wall Mode with 'B'
                if event.key == pygame.K_b:
                    drawing_walls = not drawing_walls # Flip the switch
                    if drawing_walls:
                        pygame.display.set_caption("MODE: WALLS (Click to add Obstacles) - Press B to switch")
                    else:
                        pygame.display.set_caption("MODE: ROUTE (Click to add Stops) - Press B to switch")

                # Run Algorithm with SPACE
                if event.key == pygame.K_SPACE and len(stops) > 1:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    for i in range(len(stops) - 1):
                        start_node = stops[i]
                        end_node = stops[i+1]
                        
                        A_star_algorithm(lambda: draw(win, grid, ROWS, width), grid, start_node, end_node)
                        
                        # Cleanup colors after run
                        if i == 0:
                            start_node.make_start()
                        elif i != len(stops) - 2: # Keep the very last node Turquoise
                            start_node.color = PURPLE

                # Clear Board with C
                if event.key == pygame.K_c:
                    stops = []
                    grid = make_grid(ROWS, width)
                    drawing_walls = False # Reset to Route mode
                    pygame.display.set_caption("RESCUE 1122: ROUTE MODE (Click to add Stops)")

    pygame.quit()

main(WIN, WIDTH)