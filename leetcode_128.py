# https://leetcode.com/problems/longest-consecutive-sequence/
# https://leetcode.com/problems/longest-consecutive-sequence/discuss/41202/Python-O(n)-solution-using-sets


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        num_set = set(nums)
        max_len = 0
        while num_set:
            position = num_set.pop()
            
            # 첫번째 시작 포인트
            first = position
            while first - 1 in num_set:
                first -= 1
                num_set.remove(first)
                
            # 두번째 시작 포인트 
            last = position
            while last + 1 in num_set:
                last += 1
                num_set.remove(last)
                
            max_len = max(max_len, last - first + 1)
        return max_len
            
            
            

