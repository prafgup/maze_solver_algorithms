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
    if row in range(n) and col+1 in range(n) and maze[row][col+1] == 0:
        return 1
    elif row+1 in range(n) and col in range(n) and maze[row+1][col] == 0:
        return 1
    elif row in range(n) and col-1 in range(n) and maze[row][col-1] == 0:
        return 1
    elif row-1 in range(n) and col in range(n) and maze[row-1][col] == 0:
        return 1
    return 0    

# As each step costs 3 for downward movement and 2 else 
# we can use the Down*3 + right*2 as the hurestic function
def h_manhattan(current, end, n):
    r1 = current//n
    r2 = end//n
    c1 = current%n
    c2 = end%n
    return (abs(r1-r2)*3 + abs(c1-c2)*2)

def h_diagonal(current, end, n):
    r1 = current//n
    r2 = end//n
    c1 = current%n
    c2 = end%n
    return (abs(r1-r2)**2 + abs(c1-c2)**2)**(0.5)


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

    from queue import PriorityQueue
    pos = start  
    delay = 0
    grid, rect, screen, wid = make_screen(n)
    queue = PriorityQueue()  # Priority queue for storing current nodes in search, stores (cost,time,position)
    maze[0][0] = -1
    total_cost = 0
    moves = []
    parent = [-1]*(n*n) # stores parent of every node
    g = [10**10]*(n*n)  # current cost to that node
    f = [10**10]*(n*n)  # g(x) + h(x)
    inside_queue = set() # stores if a element is inside the queue or not
    inside_queue.add(0)
    g[0] = 0
    f[0] = h_manhattan(0,end,n)
    queue.put((f[0],0,0)) # inserting removing takes log(size) time
    first_in_count = 0
    search_cost = 0

    while pos != end:
        curr_elem = queue.get()
        curr_cost = curr_elem[0]
        pos = curr_elem[2]
        inside_queue.remove(pos)
        row = pos//n
        col = pos%n
        expanded = False

        # trying to expand the nodes
        if (col + 1 < n) and (maze[row][col + 1] != 1):
            curr_pos = row*n + col + 1

            # if current path is is less than minimum path to that node we try to add it
            if g[pos] + 2 < g[curr_pos]:
                # updating costs
                parent[curr_pos] = pos
                g[curr_pos] = g[pos] + 2
                f[curr_pos] = g[curr_pos] + h_manhattan(curr_pos, end, n)
                # if current node is not inside priority queue add it to the queue
                if curr_pos not in inside_queue:
                    first_in_count+=1
                    queue.put((f[curr_pos],first_in_count,curr_pos))
                    inside_queue.add(curr_pos)
                    maze[curr_pos//n][curr_pos%n] = -1
                    expanded = True

        if (row + 1 < n) and (maze[row + 1][col] != 1) :
            curr_pos = (row + 1)*n + col
            if g[pos] + 3 < g[curr_pos]:
                parent[curr_pos] = pos
                g[curr_pos] = g[pos] + 3
                f[curr_pos] = g[curr_pos] + h_manhattan(curr_pos, end, n)
                if curr_pos not in inside_queue:
                    first_in_count+=1
                    queue.put((f[curr_pos],first_in_count,curr_pos))
                    inside_queue.add(curr_pos)
                    maze[curr_pos//n][curr_pos%n] = -1
                    expanded = True

        if (col - 1 >= 0) and (maze[row][col - 1] != 1) :
            curr_pos = row*n + col - 1
            if g[pos] + 2 < g[curr_pos]:
                parent[curr_pos] = pos
                g[curr_pos] = g[pos] + 2
                f[curr_pos] = g[curr_pos] + h_manhattan(curr_pos, end, n)
                if curr_pos not in inside_queue:
                    first_in_count+=1
                    queue.put((f[curr_pos],first_in_count,curr_pos))
                    inside_queue.add(curr_pos)
                    maze[curr_pos//n][curr_pos%n] = -1
                    expanded = True

        if (row - 1 >= 0) and (maze[row - 1][col] != 1) :
            curr_pos = (row - 1)*n + col
            if g[pos] + 2 < g[curr_pos]:
                parent[curr_pos] = pos
                g[curr_pos] = g[pos] + 2
                f[curr_pos] = g[curr_pos] + h_manhattan(curr_pos, end, n)
                if curr_pos not in inside_queue:
                    first_in_count+=1
                    queue.put((f[curr_pos],first_in_count,curr_pos))
                    inside_queue.add(curr_pos)
                    maze[curr_pos//n][curr_pos%n] = -1
                    expanded = True

        redraw_maze(grid, rect, screen, n, maze, pos, delay, wid, end)
        if expanded:
            search_cost +=2 
            if parent[pos] == pos - n:
                search_cost+=1 
    curr_node = end

    # printing the path from start to end
    while parent[curr_node] != -1 :
        maze[curr_node//n][curr_node%n] = 2
        if parent[curr_node] == curr_node - 1 :
            total_cost+=2
            moves.append("Right")
        elif parent[curr_node] == curr_node + 1 :
            total_cost+=2
            moves.append("Left")
        elif parent[curr_node] == curr_node + n :
            total_cost+=2
            moves.append("Up")
        elif parent[curr_node] == curr_node - n :
            total_cost+=3
            moves.append("Down")
        curr_node = parent[curr_node]
    moves = moves[::-1]
    maze[0][0] = 2
    redraw_maze(grid, rect, screen, n, maze, pos, delay, wid, end)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print("Total Search Time : {} seconds".format(end_time-start_time))
    print(f"Peak Memory usage was was {peak / 10**6}MB")
    print(f"Total Expanding Search Cost is {search_cost} Units")
    print(f"Best Path Total Cost is {total_cost} Units")
    tracemalloc.stop()

    print(moves)
    popup_win(str(total_cost), "Score", "./meat.png" , screen)



if __name__ == "__main__":
    n = 10 # size of maze

    #np.random.seed(1112)

    start, end = startend_postion(n)
    randno = randomize(n)
    maze = prepare_maze(n, randno, start, end)

    search_algo(n, maze, start, end)
    
    
