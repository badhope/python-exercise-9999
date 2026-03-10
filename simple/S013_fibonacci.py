# -----------------------------
# 题目：斐波那契数列。
# 描述：生成斐波那契数列的前n项。
# -----------------------------

def fibonacci(n):
    if n <= 1:
        return [0][:n]
    result = [0, 1]
    for _ in range(2, n):
        result.append(result[-1] + result[-2])
    return result

def main():
    print(f"前10项: {fibonacci(10)}")


if __name__ == "__main__":
    main()
