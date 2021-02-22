# https://leetcode.com/problems/palindrome-linked-list/
# https://www.youtube.com/watch?v=fDOBOBYVV0A&ab_channel=AIHolic
# https://inspirit941.tistory.com/entry/Python-LeetCode-234-Palindrome-Linked-List


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def isPalindrome(self, head: ListNode) -> bool:
        rev = None
        slow = fast = head
        while fast and fast.next:
            fast = fast.next.next
            rev, rev.next, slow = slow, rev, slow.next
        if fast:
            slow = slow.next
        while rev and rev.val == slow.val:
            slow = slow.next
            rev = rev.next
        return not rev