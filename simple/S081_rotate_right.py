# -----------------------------
# 题目：数组元素右移。
# 描述：将数组元素向右移动k位。
# -----------------------------

def rotate_right(lst, k):
    if not lst:
        return lst
    k = k % len(lst)
    return lst[-k:] + lst[:-k]

def main():
    print(f"右移2位: {rotate_right([1,2,3,4,5], 2)}")


if __name__ == "__main__":
    main()
