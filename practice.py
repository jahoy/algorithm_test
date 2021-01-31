class Solution:
    def max_product(self, nums:List[int])->int:
        largest_product = most_ps_product = most_neg_product = nums[0]

        for i in range(1, len(nums)):
            x = max(nums[i], most_ps_product * nums[i], most_neg_product * nums[i])
            y = min(nums[i], most_ps_product * nums[i], most_neg_product * nums[i])

            most_ps_product, most_neg_product = x, y
            largest_product = max(largest_product, most_ps_product)

        return largest_product