# -----------------------------
# 题目：移除元素。
# 描述：移除数组中所有等于val的元素。
# -----------------------------

def remove_element(nums, val):
    count = 0
    for i in range(len(nums)):
        if nums[i] != val:
            nums[count] = nums[i]
            count += 1
    return count

def main():
    nums = [3,2,2,3]
    new_len = remove_element(nums, 3)
    print(f"新长度: {new_len}")


if __name__ == "__main__":
    main()
