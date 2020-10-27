import sys
from collections import deque
input = sys.stdin.readline


n, k = map(int, input().split())
MAX_SIZE = 100001
visited = [0] * MAX_SIZE

q = deque([n])

def move(next, cur):
    if (0 <= next < MAX_SIZE) and (visited[next] == 0 or visited[cur] + 1 < visited[next]):
        q.append(next)
        visited[next] = visited[cur] + 1

def solve():
    while q:
        cur = q.popleft()
        if cur == k:
            return visited[cur]
        move(cur - 1, cur)
        move(cur + 1, cur)
        move(cur * 2, cur)

print(solve())