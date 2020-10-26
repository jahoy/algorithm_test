from sys import stdin
from collections import deque


# 입력
n = int(input())
matrix = [list(map(int, list(stdin.readline().strip()))) for _ in range(n)]

# print(f'n: {n}')
# print(f'matrix: {matrix}')

# 방문 내역 저장용 visited
visited = [[0]*n for _ in range(n)]

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def bfs(x, y, group_id):
    q = deque()
    q.append((x, y))
    visited[x][y] = group_id
    cnt = 0
    while q:
        x, y = q.popleft()
        cnt += 1
        for i in range(4):
            nx = x + dx[i]
            ny = y + dy[i]
            # 공간을 벗어난 경우 무시
            if nx < 0 or nx >= n or ny < 0 or ny >=n:
                continue
            if matrix[nx][ny] == 1 and visited[nx][ny] == 0:
                q.append((nx, ny))
                visited[nx][ny] = group_id
    return cnt

result = []
group_id = 0
for i in range(n):
    for j in range(n):
        if matrix[i][j] == 1 and visited[i][j] == 0:
            group_id += 1 
            result.append(bfs(i, j, group_id))
            

# 단지수 출력
print(group_id)
result.sort()
for i in range(group_id):
    print(result[i])




