class Solution:
    def longestConsecutive(self, nums:List[int])->int:
        num_set = set(nums)
        max_len = 0
        while num_set:
            position = num_set.pop()

            first = position
            while first - 1 in num_set:
                first -= 1
                num_set.remove(first)

            last = position
            while last + 1 in num_set:
                last += 1
                num_set.remove(last)

            max_len = max(max_len, last - first + 1)

        return max_len