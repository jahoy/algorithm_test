import sys
from collections import deque

# 입력받기
M, N = map(int, sys.stdin.readline().strip().split())

matrix = []
for i in range(N):
    matrix.append(list(map(int, sys.stdin.readline().split())))

# print(M, N)
# print(matrix)

dx = [0, 1, 0, -1]
dy = [1, 0, -1, 0]


def bfs(q, answer):
    count = answer
    while q:
        v = q.popleft()
        now_x = v[0]
        now_y = v[1]
        count = v[2]
        for i in range(4):
            new_x = now_x + dx[i]
            new_y = now_y + dy[i]
            if ( new_x < 0  or new_x >= N or new_y < 0 or new_y >= M ):
                continue
            if matrix[new_x][new_y] == 0 and matrix[new_x][new_y] != -1:
                matrix[new_x][new_y] = 1
                q.append([new_x, new_y, count + 1])
    return count

def check(answer, matrix):
    for i in range(N):
        for j in range(M):
            if matrix[i][j] == 0:
                return -1
    return answer

answer = 0
q = deque([])
for i in range(N):
    for j in range(M):
        if matrix[i][j] == 1:
            q.append([i, j, answer])
answer = bfs(q, answer)

print(check(answer, matrix))