# https://leetcode.com/problems/merge-k-sorted-lists/
# https://www.youtube.com/watch?v=2xJrXZg3j8M&feature=youtu.be&ab_channel=AIHolic


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

import heapq
class Solution:
    def mergeKLists(self, lists: List[ListNode]) -> ListNode:
        
        dummy = ListNode(None)
        current = dummy
        
        array = []
        for node in lists:
            while node:
                heapq.heappush(array, node.val)
                node = node.next
        
        while array:
            val = heapq.heappop(array)
            current.next = ListNode(val)
            current = current.next
        
        return dummy.next