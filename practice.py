class Solution:
    def middleNode(self, head:ListNode) -> ListNode:
        rabbit, turtle = head, head

        while rabbit and rabbit.next:
            turtle = turtle.next
            rabbit = rabbit.next.next
        return turtle