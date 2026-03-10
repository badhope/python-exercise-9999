# -----------------------------
# 题目：整数反转。
# 描述：反转一个整数的数字顺序。
# -----------------------------

def reverse_integer(n):
    sign = -1 if n < 0 else 1
    n = abs(n)
    reversed_num = int(str(n)[::-1])
    return sign * reversed_num

def main():
    print(f"反转123: {reverse_integer(123)}")
    print(f"反转-456: {reverse_integer(-456)}")


if __name__ == "__main__":
    main()
