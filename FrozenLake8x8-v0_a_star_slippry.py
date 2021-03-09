


def startend_postion(n):
    start = 0
    end = n*n-1
    return start, end


def h_manhattan(current, end, n):
    r1 = current//n
    r2 = end//n
    c1 = current%n
    c2 = end%n
    return (abs(r1-r2)*1 + abs(c1-c2)*1)



def search_algo(n, maze, start, end):
    from queue import PriorityQueue
    pos = start  
    delay = 0.1

    queue = PriorityQueue()
    maze[0][0] = -1
    total_cost = 0
    moves = []
    parent = [-1]*(n*n)
    g = [10**10]*(n*n)
    f = [10**10]*(n*n)
    inside_queue = set()
    inside_queue.add(0)
    g[0] = 0
    f[0] = h_manhattan(0,end,n)
    queue.put((f[0],0,0))
    first_in_count = 0

    while pos != end:
        curr_elem = queue.get()
        curr_cost = curr_elem[0]
        pos = curr_elem[2]
        inside_queue.remove(pos)
        row = pos//n
        col = pos%n
        if (col + 1 < n) and (maze[row][col + 1] != 1):
            curr_pos = row*n + col + 1
            if g[pos] + 2 < g[curr_pos]:
                parent[curr_pos] = pos
                g[curr_pos] = g[pos] + 2
                f[curr_pos] = g[curr_pos] + h_manhattan(curr_pos, end, n)
                if curr_pos not in inside_queue:
                    first_in_count+=1
                    queue.put((f[curr_pos],first_in_count,curr_pos))
                    inside_queue.add(curr_pos)
                    maze[curr_pos//n][curr_pos%n] = -1

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

        
    curr_node = end
    while parent[curr_node] != -1 :
        maze[curr_node//n][curr_node%n] = 2
        if parent[curr_node] == curr_node - 1 :
            total_cost+=2
            moves.append(2)
        elif parent[curr_node] == curr_node + 1 :
            total_cost+=2
            moves.append(0)
        elif parent[curr_node] == curr_node + n :
            total_cost+=2
            moves.append(3)
        elif parent[curr_node] == curr_node - n :
            total_cost+=3
            moves.append(1)
        curr_node = parent[curr_node]
    moves = moves[::-1]
    maze[0][0] = 2
    return moves
    



## 0(Left) 1(Down) 2(Right) 3(Up) 

def prepare_maze(desc, start, end,n):
    maze = [[0 for i in range(n)] for j in range(n)]
    for i in range(8):
        for j in range(8):
            if str(desc[i][j])[2:-1] == 'H':
                maze[i][j] = 1
    maze[start//n][start%n] = 0
    maze[end//n][end%n] = 0
    return maze

import gym
env = gym.make('FrozenLake8x8-v0')

total_score = 0
misses = 0
start, end = startend_postion(8)
max_episodes = 1000

for episodes in range(max_episodes):
    obesrvation = env.reset()
    my_maze = prepare_maze(env.desc, start, end, 8)
    curr = 0
    while True:
        moves = search_algo(8, my_maze, curr, end)
        curr, reward, done, info = env.step(moves[0])
        #env.render()
        if done and reward == 1:
            total_score+=1
            break
        elif done and reward == 0:
            misses+=1
            break
    
print("Total Score = {} out of {}".format(total_score,max_episodes))
print("Misses = {}".format(misses))
env.close()