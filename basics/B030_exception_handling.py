# -----------------------------
# 题目：异常处理。
# 描述：使用 try-except-finally 处理各种异常，包括 ZeroDivisionError、ValueError、TypeError 等。
# -----------------------------

def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        return "Error: Division by zero!"
    except TypeError:
        return "Error: Invalid type!"


def main():
    print(f"safe_divide(10, 2) = {safe_divide(10, 2)}")
    print(f"safe_divide(10, 0) = {safe_divide(10, 0)}")
    print(f"safe_divide('10', 2) = {safe_divide('10', 2)}")
    
    try:
        value = int(input("请输入一个整数: "))
        print(f"你输入了: {value}")
    except ValueError:
        print("输入无效，请输入整数！")
    finally:
        print("程序结束。")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# try：可能抛出异常的代码块
# except：捕获并处理特定异常
# finally：无论是否异常都会执行的代码
# 可以同时捕获多种异常