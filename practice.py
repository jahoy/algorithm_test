class Solution(object):
    def subarraySum(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: int
        """
        running_sum = 0
        hash_table = collections.defaultdict(lambda:0)
        total = 0
        for x in nums:
            running_sum += x
            sum = running_sum - k
            if sum in hash_table:
                total += hash_table[sum]
            if running_sum == k:
                total += 1
            hash_table[running_sum] += 1
        return total