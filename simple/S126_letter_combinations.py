# -----------------------------
# 题目：电话号码字母组合。
# 描述：根据数字键盘生成所有字母组合。
# -----------------------------

def letter_combinations(digits):
    if not digits:
        return []
    mapping = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    result = ['']
    for digit in digits:
        result = [p + q for p in result for q in mapping[digit]]
    return result

def main():
    print(f"组合: {letter_combinations('23')}")


if __name__ == "__main__":
    main()
