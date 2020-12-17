# https://leetcode.com/problems/linked-list-cycle/
# https://www.youtube.com/watch?v=kbNLEVkNT1g&ab_channel=SuboptimalEngineer


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def hasCycle(self, head: ListNode) -> bool:
        if head is None:
            return False
        
        ptr = head
        fast_ptr = head.next
        
        while ptr is not None and fast_ptr is not None and fast_ptr.next is not None:
            if ptr == fast_ptr:
                return True
            ptr = ptr.next
            fast_ptr = fast_ptr.next.next
        return False
        