# -----------------------------
# 题目：组合总和。
# 描述：找出和为目标值的组合。
# -----------------------------

def combination_sum(candidates, target):
    result = []
    def backtrack(start, target, path):
        if target == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > target:
                continue
            path.append(candidates[i])
            backtrack(i, target - candidates[i], path)
            path.pop()
    backtrack(0, target, [])
    return result

def main():
    print(f"组合: {combination_sum([2,3,6,7], 7)}")


if __name__ == "__main__":
    main()
