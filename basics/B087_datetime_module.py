# -----------------------------
# 题目：datetime模块。
# 描述：使用datetime模块进行日期时间操作。
# -----------------------------

from datetime import datetime, timedelta

def main():
    now = datetime.now()
    print(f"当前时间: {now}")
    print(f"格式化: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"3天后: {now + timedelta(days=3)}")


if __name__ == "__main__":
    main()
