# https://leetcode.com/problems/middle-of-the-linked-list/
# https://leetcode.com/explore/challenge/card/30-day-leetcoding-challenge/529/week-2/3290/discuss/569063/Rabbit-and-Turtle-pointers-(Python-3)-with-explanation

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def middleNode(self, head: ListNode) -> ListNode:
        rabbit, turtle = head, head
        
        while rabbit and rabbit.next:
            turtle = turtle.next
            rabbit = rabbit.next.next
        return turtle
            
        