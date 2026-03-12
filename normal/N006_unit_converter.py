# -----------------------------
# 题目：单位转换器。
# 描述：实现长度、重量等单位转换。
# -----------------------------

def km_to_miles(km):
    return km * 0.621371

def miles_to_km(miles):
    return miles / 0.621371

def kg_to_pounds(kg):
    return kg * 2.20462

def pounds_to_kg(pounds):
    return pounds / 2.20462

def celsius_to_fahrenheit(c):
    return c * 9/5 + 32

def fahrenheit_to_celsius(f):
    return (f - 32) * 5/9

def main():
    print(f"10公里 = {km_to_miles(10):.2f}英里")
    print(f"100公斤 = {kg_to_pounds(100):.2f}磅")
    print(f"25°C = {celsius_to_fahrenheit(25):.2f}°F")


if __name__ == "__main__":
    main()
