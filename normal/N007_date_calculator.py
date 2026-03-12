# -----------------------------
# 题目：日期计算器。
# 描述：计算两个日期之间的天数差。
# -----------------------------

from datetime import datetime

def days_between(date1, date2):
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def add_days(date, days):
    d = datetime.strptime(date, "%Y-%m-%d")
    result = d + __import__("datetime").timedelta(days=days)
    return result.strftime("%Y-%m-%d")

def main():
    print(f"2024-01-01 到 2024-12-31 相隔 {days_between('2024-01-01', '2024-12-31')} 天")
    print(f"2024-01-01 加100天 = {add_days('2024-01-01', 100)}")


if __name__ == "__main__":
    main()
