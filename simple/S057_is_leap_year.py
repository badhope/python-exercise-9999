# -----------------------------
# 题目：判断闰年。
# 描述：判断一年是否为闰年。
# -----------------------------

def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def main():
    for year in [2000, 2024, 2023, 1900]:
        print(f"{year}: {'是闰年' if is_leap_year(year) else '不是闰年'}")


if __name__ == "__main__":
    main()
