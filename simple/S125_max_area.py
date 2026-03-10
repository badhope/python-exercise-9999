# -----------------------------
# 题目：盛最多水的容器。
# 描述：找出能盛最多水的两个柱子。
# -----------------------------

def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        width = right - left
        max_water = max(max_water, width * min(height[left], height[right]))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water

def main():
    print(f"最大水量: {max_area([1,8,6,2,5,4,8,3,7])}")


if __name__ == "__main__":
    main()
