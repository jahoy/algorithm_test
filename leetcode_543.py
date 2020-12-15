# https://leetcode.com/problems/diameter-of-binary-tree/
# https://leetcode.com/problems/diameter-of-binary-tree/discuss/101145/Simple-Python
# https://www.youtube.com/watch?v=JjVUXmH5M2g&ab_channel=TechZoo


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def diameterOfBinaryTree(self, root: TreeNode) -> int:
        self.ans = 0
        def depth(node):
            if node is None:
                return 0
            left_depth = depth(node.left)
            right_depth = depth(node.right)
            self.ans = max(self.ans, left_depth + right_depth)
            return max(left_depth, right_depth) + 1
        depth(root)
        return self.ans
        