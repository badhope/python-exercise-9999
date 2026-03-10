# -----------------------------
# 题目：天数计算。
# 描述：计算某年某月有多少天。
# -----------------------------

def days_in_month(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 29 if is_leap_year(year) else 28

def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def main():
    print(f"2024年2月: {days_in_month(2024, 2)}天")


if __name__ == "__main__":
    main()
