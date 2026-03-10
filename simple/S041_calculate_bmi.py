# -----------------------------
# 题目：计算BMI。
# 描述：根据身高体重计算BMI指数。
# -----------------------------

def calculate_bmi(weight, height):
    bmi = weight / (height ** 2)
    if bmi < 18.5:
        return "偏瘦"
    elif bmi < 24:
        return "正常"
    elif bmi < 28:
        return "偏胖"
    return "肥胖"

def main():
    print(f"BMI(70, 1.75): {calculate_bmi(70, 1.75)}")


if __name__ == "__main__":
    main()
