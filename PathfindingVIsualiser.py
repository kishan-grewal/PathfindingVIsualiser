from os import path 
import pygame as pg 
from pygame.locals import * 
from math import exp, sqrt 
import heapq

N = 32

pg.init()
screen_width = 25*N
screen_height = 25*N
extra_height = 20 + 100 + 20
screen = pg.display.set_mode(size = (screen_width, screen_height+extra_height))
pg.display.set_caption("A* Pathfinder")
line_width = 3
font_obj = pg.font.Font('freesansbold.ttf', 32)

global walled_positions
walled_positions = []
global start_position
global end_position
# define start/end positions
start_position = (0, 0)
end_position = (31, 31)

def draw_grid(path):
    global walled_positions
    global start_position
    global end_position
    background = (250, 255, 250)
    screen.fill(background)
    for t in range(N+1):
        pg.draw.line(screen, (0,0,0), (0, 25*t), (screen_width, 25*t))#horizontal
        pg.draw.line(screen, (0,0,0), (25*t, 0), (25*t, screen_height))#vertical
    path_length = 2
    try:
        path_length = len(path)
    except:
        path_length = 2
        path = (start_position, end_position)
    for i in range(path_length):
        pos = path[i]
        current_box = pg.Rect(pos[0]*25, pos[1]*25, 25, 25)
        if i == 0 or i == len(path)-1:
            filled = (150, 50, 50) # normal
        else:
            filled = (50, 50, 100) # path
        pg.draw.rect(screen, filled, current_box)
    filled = (0, 0, 0)
    for pos in walled_positions:
        current_box = pg.Rect(pos[0]*25, pos[1]*25, 25, 25)
        pg.draw.rect(screen, filled, current_box)

class Node:
    def __init__(self, position):
        self.position = position
        self.g = float('inf')
        self.h = 0
        self.parent = None
    
    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)

def calculate_manhattan_distance(node, end_node):
    return abs(node.position[0] - end_node.position[0]) + abs(node.position[1] - end_node.position[1])
    #return sqrt((node.position[0] - end_node.position[0])**2 + (node.position[1] - end_node.position[1])**2)

def get_neighbors(node, grid_size):
    global walled_positions
    x, y = node.position
    neighbors = []
    if x > 0:
        neighbors.append(Node((x - 1, y)))
    if x < grid_size - 1:
        neighbors.append(Node((x + 1, y)))
    if y > 0:
        neighbors.append(Node((x, y - 1)))
    if y < grid_size - 1:
        neighbors.append(Node((x, y + 1)))

    return neighbors

def a_star(start_position, end_position, grid_size):
    global walled_positions
    open_set = []
    closed_set = set()
    
    start_node = Node(start_position)
    end_node = Node(end_position)
    
    start_node.g = 0
    start_node.h = calculate_manhattan_distance(start_node, end_node)
    
    heapq.heappush(open_set, start_node)
    
    while open_set:
        current_node = heapq.heappop(open_set)
        try:
            if current_node.parent.position in walled_positions:
                return None
        except:
            if current_node != start_node:
                return None
        
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        
        closed_set.add(current_node.position)
        
        for neighbor in get_neighbors(current_node, grid_size):
            if neighbor.position in closed_set:
                continue
            
            tentative_g = current_node.g + 1  # assuming each step has a cost of 1
            
            if tentative_g < neighbor.g:
                neighbor.parent = current_node
                neighbor.g = tentative_g
                if neighbor.position in walled_positions:
                    neighbor.h = float('infinity')
                else:
                    neighbor.h = calculate_manhattan_distance(neighbor, end_node)
                
                if neighbor not in open_set:
                    heapq.heappush(open_set, neighbor)

    return None  # no path found

def main():
    global walled_positions
    global start_position
    global end_position
    print("\nClick with any mouse button to add walls, and hold space during the click to remove walls\n"
    +"Press backspace at any time to remove all added walls\n"
    +"Any of these changes will remove any generated path")
    print("\nPlease wait a second after adding walls before generating the path!")

    # solve grid button
    sol_button = pg.Rect(50, 820, 300, 100)
    sol_surface = font_obj.render("Solve grid", True, (0, 0, 0))
    sol_rect = sol_surface.get_rect()
    sol_rect.center = (50 + 150, 820 + 50) 
    # set start,end button
    set_button = pg.Rect(400, 820, 300, 100)
    set_surface = font_obj.render("Set start, end", True, (0, 0, 0))
    set_rect = set_surface.get_rect()
    set_rect.center = (400 + 150, 820 + 50) 

    path = [start_position, end_position]
    mouse_down = False

    running = True
    while running:
        draw_grid(path)
        pg.draw.rect(screen, (0,0,0), sol_button, line_width)
        screen.blit(sol_surface, sol_rect)
        pg.draw.rect(screen, (0,0,0), set_button, line_width)
        screen.blit(set_surface, set_rect)

        mouse_position = (pg.mouse.get_pos()[0] // 25, pg.mouse.get_pos()[1] // 25)
        if pg.mouse.get_pos()[1] < 800:
            if mouse_down == True:
                if pg.key.get_pressed()[K_SPACE] == 0:
                    if mouse_position != start_position and mouse_position != end_position:
                        if mouse_position not in walled_positions:
                            walled_positions.append(mouse_position)
                            path = (start_position, end_position)
                else:
                    if mouse_position in walled_positions:
                        walled_positions.remove(mouse_position)
                        path = (start_position, end_position)

        pg.event.pump()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if pg.key.get_pressed()[K_BACKSPACE] == 1:
                    walled_positions = []
                    path = (start_position, end_position)
            if event.type == pg.MOUSEBUTTONDOWN:
                if pg.mouse.get_pos()[1] > 800:
                    if sol_button.collidepoint(event.pos):
                        # find the path using A* algorithm
                        path = a_star(start_position, end_position, N)

                        if path:
                            print("Path found")
                        else:
                            print("No path found")

                    if set_button.collidepoint(event.pos):
                        valid = False
                        while not valid:
                            x1 = input("Enter start node x: ")
                            y1 = input("Enter start node y: ")
                            x2 = input("Enter end node x: ")
                            y2 = input("Enter end node y: ")
                            
                            try:
                                x1 = int(x1)
                                y1 = int(y1)
                                x2 = int(x2)
                                y2 = int(y2)
                            except:
                                print("Values must be integers")
                                continue
                            
                            if not (0 <= x1 <= 31 and 0 <= x2 <= 31 and 0 <= y1 <= 31 and 0 <= y2 <= 31):
                                print("Values must be between 0 and 31 inclusive")
                                continue
                            
                            if (x1, y1) in walled_positions or (x2, y2) in walled_positions:
                                print("Values must not be walled off")
                                continue

                            valid = True

                        print("Start and end nodes have been set")
                        start_position = (x1, y1)
                        end_position = (x2, y2)
                        path = [start_position, end_position]
                        walled_positions = []
            
            if pg.mouse.get_pos()[1] < 800: # mouse down can only start on grid
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_down = True
            if event.type == pg.MOUSEBUTTONUP or pg.mouse.get_pos()[1] > 800: # mouse down ends if mouse moves off of grid
                mouse_down = False

                  
        
        pg.display.update()

    pg.quit()

main()