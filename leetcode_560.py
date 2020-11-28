class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        n = len(nums)
        if n == 1:
            if nums[0] == k:
                return 1
            else:
                return 0
        
        left = 0
        right = 0
        count = 0
        current_sum = nums[0]
        while left < n and right < n:
            if k > current_sum and right + 1 < n:
                right += 1
                current_sum += nums[right]
            elif k < current_sum:
                current_sum -= nums[left]
                left += 1
            elif k == current_sum:
                count += 1
                right += 1
        return count


