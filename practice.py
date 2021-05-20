class Solution:
    def merge(self, intervals:List[List[int]]) -> List[List[int]]:
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