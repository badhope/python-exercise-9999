# -----------------------------
# 题目：温度转换器。
# 描述：将摄氏温度转换为华氏温度，以及华氏转摄氏。
# -----------------------------

def celsius_to_fahrenheit(c):
    return c * 9/5 + 32

def fahrenheit_to_celsius(f):
    return (f - 32) * 5/9

def main():
    print("=== 温度转换器 ===")
    c = 25
    f = 77
    print(f"{c}°C = {celsius_to_fahrenheit(c):.2f}°F")
    print(f"{f}°F = {fahrenheit_to_celsius(f):.2f}°C")


if __name__ == "__main__":
    main()
