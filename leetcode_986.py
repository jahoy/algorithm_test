# https://leetcode.com/problems/interval-list-intersections/
# https://www.youtube.com/watch?v=PVeDmre3rSc&ab_channel=TimothyHChang


class Solution:
    def intervalIntersection(self, A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
        a = 0
        b = 0
        N, M = len(A), len(B)
        
        output = []
        while a < N and b < M:
            start =  max(A[a][0], B[b][0])
            end = min(A[a][1], B[b][1])
            
            if start <= end:
                output.append([start, end])
            
            if A[a][1] < B[b][1]:
                a += 1
            else:
                b += 1
        return output
        