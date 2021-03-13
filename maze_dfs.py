import sys
import time
import numpy as np
import tkinter as Mazegame
from termcolor import colored
from PIL import ImageTk, Image
from tkinter import ttk, Canvas, Label
import tracemalloc
import time

#This function initializes lion and meat positions
def startend_postion(n):
    start = 0
    end = n*n-1
    return start, end

#This function randomly create walls in maze
def randomize(n):
    limit = np.random.randint(n*n/4,n*n/2)
    checklist = list()

    for i in range(limit):
        hold = np.random.randint(n*n-1)
        chk = 0
        for j in range(len(checklist)):
            if checklist[j] == hold or hold == 0:
                chk = 1
        if chk == 0:
            checklist.append(hold)
    return checklist

#This function prepares full maze layout
def prepare_maze(n, checklist, start, end):
    maze = [[0 for i in range(n)] for j in range(n)]
    for i in range(len(checklist)):
        maze[checklist[i]//n][checklist[i]%n] = 1

    maze[start//n][start%n] = 0
    maze[end//n][end%n] = 0

    return maze

#
def display_maze(n, maze, pos):
    print("")
    for i in range(n):
        for j in range(n):
            if pos == i*n+j:
                print(colored("[8]", "blue"), end="")
            elif maze[i][j] == 0:
                print(colored("[0]", "green"), end="")
            elif maze[i][j] == 1:
                print(colored("[1]", "red"), end="")
            elif maze[i][j] == -1:
                print(colored("[3]", "yellow"), end="")
            elif maze[i][j] == 2:
                print(colored("[3]", "cyan"), end="")
        print("")

def make_screen(n):
    if n in range(2,9):
       size = 300
    elif n in range(9,43):
       size = 640
    elif n in range(43, 75):
       size = 750
    else:
        print("Invalid Maze size")
        sys.exit()

    cell_width = int(size/n)
    cell_height = int(size/n)

    screen = Mazegame.Tk()
    screen.title("Will lion find meat??")
    grid = Canvas(screen, width = cell_width*n, height = cell_height*n, highlightthickness=0)
    grid.pack(side="top", fill="both", expand="true")

    rect = {}
    for col in range(n):
        for row in range(n):
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            rect[row, col] = grid.create_rectangle(x1,y1,x2,y2, fill="red", tags="rect")
    return grid, rect, screen, cell_width

def load_img(size, path, end):
    xcod = end//n
    ycod = end%n
    load = Image.open(path)
    load = load.resize((size, size), Image.ANTIALIAS)
    render = ImageTk.PhotoImage(load)
    img = Label(image=render)
    img.image = render
    img.place(x = ycod*size, y = xcod*size)
    return img

# This function redraws maze and updates the maze according to the traversal at 'delay' time interval
def redraw_maze(grid, rect, screen, n, maze, pos, delay, size, end):
    grid.itemconfig("rect", fill="green")
    path2 = "./meat.png"
    for i in range(n):
        for j in range(n):
            item_id = rect[i,j]
            if pos == i*n+j:
                grid.itemconfig(item_id, fill="blue")
            elif maze[i][j] == 0:                       # positions where lion can move
                grid.itemconfig(item_id, fill="salmon")
            elif maze[i][j] == 1:                       # blocked positions/walls
                grid.itemconfig(item_id, fill="black")
            elif maze[i][j] == -1:                      # positions visited    
                grid.itemconfig(item_id, fill="DeepSkyBlue2")
            elif maze[i][j] == 2:
                grid.itemconfig(item_id, fill="SpringGreen2")

    load_img(size, path2, end)
    screen.update_idletasks()
    screen.update()
    time.sleep(delay)
    return

def button(text, win, window):
    b = ttk.Button(window, text=text, command = win.destroy)
    b.pack()

def popup_win(msg, title, path ,screen):
    popup = Mazegame.Tk()
    popup.wm_title(title)
    label = ttk.Label(popup, text = msg, font=("Times", 20))
    label.pack(side="top", fill="x", pady=50, padx=50)
    button("Close Maze", screen, popup)
    button("Close popup", popup, popup)
    popup.mainloop()

#This functions check neighbours of current position i.e. current row and col    
def check_pos(row, col, n, maze):
    # can be impplemented in O(1)
    if row in range(n) and col+1 in range(n) and maze[row][col+1] == 0:
        return 1
    elif row+1 in range(n) and col in range(n) and maze[row+1][col] == 0:
        return 1
    elif row in range(n) and col-1 in range(n) and maze[row][col-1] == 0:
        return 1
    elif row-1 in range(n) and col in range(n) and maze[row-1][col] == 0:
        return 1
    return 0    

# This function will contain all your search algorithms
# maze[row][col] should be used to refer to any position of maze
# pos is the starting position of maze and end is ending position
# pos//n will give row index and pos%n will give col index
# you can use list as stack or any other data structure to traverse the positions of the maze.
def search_algo(n, maze, start, end):
    tracemalloc.start()
    start_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage before search {current / 10**6}MB")


    pos = start  
    delay = 0.0
    grid, rect, screen, wid = make_screen(n)
    stack = [0] # current path dfs stack
    row = 0
    col = 0
    maze[row][col] = -1
    step_cost = 3
    moves = []
    search_cost = 0
    while pos != end:
        expanded = True
        row = pos//n
        col = pos%n

        # expanding nodes if not already visited and node exists
        if (col + 1 < n) and (maze[row][col + 1] not in [-1,1,2]) :
            stack.append(row*n + col + 1)
            maze[row][col+1] = -1
            pos = stack[-1]
            moves.append("Right")
            expanded = True
        elif (row + 1 < n) and (maze[row + 1][col] not in [-1,1,2]) :
            stack.append((row + 1)*n + col)
            maze[row+1][col] = -1
            pos = stack[-1]
            moves.append("Down")
            expanded = True
        elif (col - 1 >= 0) and (maze[row][col - 1] not in [-1,1,2]) :
            stack.append(row*n + col - 1)
            maze[row][col-1] = -1
            pos = stack[-1]
            moves.append("Left")
            expanded = True
        elif (row - 1 >= 0) and (maze[row - 1][col] not in [-1,1,2]) :
            stack.append((row - 1)*n + col)
            maze[row-1][col] = -1
            pos = stack[-1]
            moves.append("Up")
            expanded = True
        else : #Retracing Back Cant go any further so poping elements from dfs sack
            maze[row][col] = 2 
            pos = stack.pop()
            moves.pop()
            redraw_maze(grid, rect, screen, n, maze, pos, delay, wid, end)
            
            # poping until there is a node that can be explored even more
            while check_pos(pos//n,pos%n,n,maze) == 0:
                maze[pos//n][pos%n] = 2
                pos = stack.pop()
                last_move = moves.pop()
                if check_pos(pos//n,pos%n,n,maze):
                        stack.append(pos)
                        moves.append(last_move)
                #redraw_maze(grid, rect, screen, n, maze, pos, delay, wid, end)
        redraw_maze(grid, rect, screen, n, maze, pos, delay, wid, end)
        if expanded:
            search_cost+=step_cost
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print("Total Search Time : {} seconds".format(end_time-start_time))
    print(f"Peak Memory usage was was {peak / 10**6}MB")
    print(f"Total Expanding Search Cost is {search_cost} Units")
    print(f"Best Path Total Cost is {len(moves)*step_cost} Units")
    tracemalloc.stop()
    
    print(moves)
    popup_win(str(len(moves)*step_cost), "Best Path Score", "./final.png" , screen)



if __name__ == "__main__":
    n = 10 # size of maze

    #np.random.seed(1112)


    start, end = startend_postion(n)
    randno = randomize(n)
    maze = prepare_maze(n, randno, start, end)

    search_algo(n, maze, start, end)

