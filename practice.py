def trap(height: List[int]) -> int:
    n = len(height)
    if n == 0:
        return 0

    lmax = [0] * n
    rmax = [0] * n

    lamx[0] = height[0]
    rmax[n-1] = height[n-1]

    for i in range(1, n):
        lmax[i] = max(lmax[i-1], height[i])

    for i in range(n-2, -1, -1):
        rmax[i] = max(rmax[i+1], height[i])

    sum = 0 
    for i in range()