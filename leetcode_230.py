# https://leetcode.com/problems/kth-smallest-element-in-a-bst/
# https://www.youtube.com/watch?v=duN4k6QPwBQ&ab_channel=TimothyHChang

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def kthSmallest(self, root: TreeNode, k: int) -> int:
        self.counter = 1
        self.k_smallest = None
        
        def inorder(node):
            if not node or self.k_smallest:
                return
            inorder(node.left)
            if self.counter == k:
                self.k_smallest = node.val
            self.counter += 1
            inorder(node.right)
        
        inorder(root)
        return self.k_smallest
                
        