class Solution:
    def threeSumClosest(self, nums:List[int], target:int) -> int:
        length = len(nums)
        if length < 3:
            return
        nums.sort()

        result = float('inf')

        for pointer in range(length - 2):
            left = pointer + 1
            right = length - 1

            while left < right:
                total = nums[pointer] + nums[left] + nums[right]

                if abs(total - target) == 0:
                    return total
                
                if abs(total - target) < abs(result - target):
                    result = total
                
                if total < target:
                    left += 1 
                elif total > target:
                    right -= 1

        return result