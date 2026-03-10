# -----------------------------
# 题目：数组元素左移。
# 描述：将数组元素向左移动k位。
# -----------------------------

def rotate_left(lst, k):
    if not lst:
        return lst
    k = k % len(lst)
    return lst[k:] + lst[:k]

def main():
    print(f"左移2位: {rotate_left([1,2,3,4,5], 2)}")


if __name__ == "__main__":
    main()
