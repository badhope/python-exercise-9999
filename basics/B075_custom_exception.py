# -----------------------------
# 题目：自定义异常类。
# 描述：创建自定义异常类。
# -----------------------------

class MyError(Exception):
    pass

def main():
    try:
        raise MyError("自定义错误")
    except MyError as e:
        print(f"捕获异常: {e}")


if __name__ == "__main__":
    main()
