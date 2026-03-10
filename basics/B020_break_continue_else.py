# -----------------------------
# 题目：循环中的break、continue和else。
# 描述：遍历1到20的整数，跳过能被3整除的数，遇到10时停止，打印找到的非3倍数的数量。
# -----------------------------

def main():
    count = 0
    found_ten = False
    
    for i in range(1, 21):
        if i == 10:
            found_ten = True
            break
        if i % 3 == 0:
            continue
        count += 1
        print(i, end=" ")
    
    print(f"\n找到的非3倍数数量: {count}")
    print(f"是否遇到10: {found_ten}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# break：立即终止整个循环
# continue：跳过当前循环，继续下一次
# for-else：循环正常结束（未break）时执行else块