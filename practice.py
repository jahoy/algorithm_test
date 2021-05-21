class Solution:
    def mergeTwoLists(self, l1:ListNode, l2: ListNode) -> ListNode:
        head = curr = ListNode(None)

        while l1 != None and l2 != None:
            if l1.val < l2.val:
                curr.next = l1
                l1 = l1.next
            else:
                curr.next = l2
                l2 = l2.next

            curr = curr.next
        curr.next = l1 or l2
        return head.next