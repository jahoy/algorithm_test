# https://leetcode.com/problems/remove-duplicates-from-sorted-list/
# https://www.youtube.com/watch?v=wc65TTSQeL0&ab_channel=TechZoo

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        curr = head
        while curr and curr.next:
            if curr.val == curr.next.val:
                curr.next = curr.next.next
            else:
                curr = curr.next
        return head
        