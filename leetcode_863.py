# https://leetcode.com/problems/all-nodes-distance-k-in-binary-tree/
# https://leetcode.com/problems/all-nodes-distance-k-in-binary-tree/discuss/360110/Python-Basically-Let's-build-a-graph

from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None


class Solution:
    def distanceK(self, root: TreeNode, target: TreeNode, K: int) -> List[int]:
        def build_parant_map(node, parent, parent_map):
            if node is None:
                return
            parent_map[node] = parent
            build_parant_map(node.left, node, parent_map)
            build_parant_map(node.right, node, parent_map)
            
        parent_map = {}
        build_parant_map(root, None, parent_map)
        
        visited = set()
        ans = []
        q = deque([])
        q.append((target, 0 ))
        visited.add(target)
        while q:
            node, distance = q.popleft()
            if distance == K:
                ans.append(node.val)
            elif distance < K:
                for n in [node.left, node.right, parent_map[node]]:
                    if n not in visited and n is not None:
                        q.append((n, distance + 1))
                        visited.add(n)
                            
        return ans
            
            
            
            
            
            
            
        
        
        