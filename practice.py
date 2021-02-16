from collections import Counter
import heapq
class Solution:
    def minDeletions(self, s:str) -> int:
        heap = sorted(-x for x in Counter(s).values())
        heapq.heapify(heap)
        count = 0
        while len(heap) >= 2:
            max_ = heapq.heappop(heap)
            if max_ == heap[0]:
                count += 1
                if max_ + 1 != 0:
                    heapq.heappush(heap, max_+1)
        return count