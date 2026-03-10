# -----------------------------
# 题目：判断有效括号。
# 描述：判断括号字符串是否有效。
# -----------------------------

def is_valid_parentheses(s):
    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in mapping:
            if not stack or stack.pop() != mapping[c]:
                return False
        else:
            stack.append(c)
    return len(stack) == 0

def main():
    print(f"()[]{{}}: {is_valid_parentheses('()[]{}')}")
    print(f"(]: {is_valid_parentheses('(]')}")


if __name__ == "__main__":
    main()
