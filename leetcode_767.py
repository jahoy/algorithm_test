# https://leetcode.com/problems/reorganize-string/
# https://www.youtube.com/watch?v=ZO9n2PT9e8o&ab_channel=EileenMao
# https://leetcode.com/problems/reorganize-string/discuss/130825/Python-solution-with-detailed-explanation



from collections import Counter
import heapq

class Solution:
    def reorganizeString(self, S: str) -> str:
        
        max_heap = []
        for key, value in Counter(S).items():
            heapq.heappush(max_heap, (-1 * value, key))
            
        result = []
        previous_count = 0
        previous_letter = None
        
        while max_heap:
            value, key = heapq.heappop(max_heap)
            value = value + 1
            result.append(key)
            if previous_count != 0:
                heapq.heappush(max_heap, (previous_count, previous_letter))
            previous_count = value
            previous_letter = key
            
        res = "".join(result)
        return res if len(res) == len(S) else ""