N, M = map(int, input().split())
visited = [False] * (N+1)
arr = []

def solve(depth, start, N, M):
    if depth == M:
        print(' '.join(map(str, arr)))
        return
    for i in range(start, N+1):
        if visited[i]:
            continue
        visited[i] = True
        arr.append(i)
        solve(depth+1, i, N, M)
        visited[i] = False # 백트래킹
        arr.pop() # 백트래킹

solve(0, 1, N, M)