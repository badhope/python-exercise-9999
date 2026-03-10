# -----------------------------
# 题目：二叉树最大深度。
# 描述：计算二叉树的最大深度。
# -----------------------------

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def main():
    print("二叉树深度计算演示")


if __name__ == "__main__":
    main()
