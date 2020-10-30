import sys
sys.setrecursionlimit(100000)
input = sys.stdin.readline


dx = [-1, 1, 0, 0]
dy = [0, 0 , -1, 1]


def dfs(x, y, high):
    visit[y][x] = True
    for i in range(4):
        nx = x + dx[i]
        ny = y + dy[i]
        if 0 <= nx < n and 0 <= ny < n and not visit[ny][nx] and matrix[ny][nx] > high:
            dfs(nx, ny, high)

if __name__ == '__main__':
    n = int(input())
    matrix = [list(map(int, input().split())) for _ in range(n)]

    max_num = 0
    for high in range(0, 101):
        group_num = 0
        visit = [[False] * 100 for _ in range(100)]
        for y in range(n):
            for x in range(n):
                if matrix[y][x] > high and not visit[y][x]:
                    dfs(x, y, high)
                    group_num += 1
        if (group_num > max_num):
            max_num = group_num
    print(max_num)