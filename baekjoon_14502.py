# https://www.acmicpc.net/problem/14502
# 조합 + dfs
import copy
import sys
input = sys.stdin.readline

virus_list = []
arr = [] # map
dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]
max_value = 0 # max 값

# 안전구역 넓이 구하기
def get_safe_area(copyed_arr):
    safe = 0
    for i in range(N):
        for j in range(M):
            if copyed_arr[i][j] == 0:
                safe += 1
    return safe

# DFS로 바이러스 퍼트리기
def spread_virus(x, y, copyed_arr):
    for i in range(4):
        nx = x + dx[i]
        ny = y + dy[i]

        if 0 <= nx and nx < M and 0 <= ny and ny < N:
            if copyed_arr[ny][nx] == 0:
                copyed_arr[ny][nx] = 2
                spread_virus(nx, ny, copyed_arr)

# 조합으로 벽 3개 놓는 모든 경우 구하기
def set_wall(start, depth):
    global max_value

    if depth == 3:
        copyed_arr = copy.deepcopy(arr)
        length = len (virus_list)
        for i in range(length):
            virus_x, virus_y = virus_list[i]
            spread_virus(virus_x, virus_y, copyed_arr)
        max_value = max(max_value, get_safe_area(copyed_arr))
        return


    for i in range(start, N*M):
        x = i % N
        y = i // N
        
        if arr[x][y] == 0:
            arr[x][y] = 1
            set_wall(i + 1, depth + 1)
            arr[x][y] = 0

if __name__ == '__main__':
    global N, M
    N, M = map(int, input().split())
    for i in range(N):
        arr.append(list(map(int, input().split())))
    for y in range(N):
        for x in range(M):
            if arr[y][x] == 2:
                virus_list.append((x, y))
    
    set_wall(0, 0)
    print(max_value)