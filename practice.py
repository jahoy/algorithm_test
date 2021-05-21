class Solution:
    def threeSum(self, nums:List[int])-> List[List[int]]:
        length = len(nums)
        output = []
        nums.sort()

        for pointer in range(length - 1):
            if pointer > 0 and nums[pointer] == nums[pointer -1]:
                continue

            left = pointer + 1
            right = length - 1

            while left < right:
                total = nums[pointer] + nums[left] + nums[right]

                if total < 0:
                    left += 1
                elif total > 0:
                    right -= 1
                elif total == 0:
                    output.append([nums[pointer], nums[left], nums[right]])
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    
                    left += 1
                    right -= 1
            return output