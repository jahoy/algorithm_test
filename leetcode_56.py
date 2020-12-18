# https://leetcode.com/problems/merge-intervals/
# https://www.youtube.com/watch?v=iT9_MU2L3H0&ab_channel=TimothyHChang

class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        if len(intervals) < 2:
            return intervals
        intervals.sort()
        
        output = [intervals[0]]
        for start, end in intervals[1:]:
            if output[-1][1] < start:
                output.append([start, end])
            elif start <= output[-1][1] < end:
                output[-1][1] = end
        return output