# https://leetcode.com/problems/trapping-rain-water/
# https://www.youtube.com/watch?v=86W0kLc2tc4&ab_channel=AIHolic

class Solution:
    def trap(self, height: List[int]) -> int:
        n = len(height)
        if n == 0:
            return 0
        lmax = [0] * n
        rmax = [0] * n
        
        lmax[0] = height[0]
        rmax[n-1] = height[n-1] 
        for i in range(1, n):
            lmax[i] = max(lmax[i-1], height[i])
            
        for i in range(n-2, -1, -1):
            rmax[i] = max(rmax[i+1], height[i])
        
        sum = 0
        for i in range(n):
            sum += min(lmax[i], rmax[i]) - height[i]
        
        return sum