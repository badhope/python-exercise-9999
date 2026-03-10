# -----------------------------
# 题目：对称二叉树。
# 描述：判断二叉树是否对称。
# -----------------------------

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def is_symmetric(root):
    def mirror(left, right):
        if not left and not right:
            return True
        if not left or not right:
            return False
        return left.val == right.val and mirror(left.left, right.right) and mirror(left.right, right.left)
    return mirror(root, root)

def main():
    print("对称二叉树演示")


if __name__ == "__main__":
    main()
