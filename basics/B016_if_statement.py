# -----------------------------
# 题目：if条件判断。
# 描述：给定成绩 score=85，判断等级：>=90 A, >=80 B, >=70 C, >=60 D, <60 E。
# -----------------------------

def main():
    score = 85
    
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "E"
    
    print(f"成绩 {score} 分，等级: {grade}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# if-elif-else：多条件分支判断
# 从上到下依次判断，满足条件后执行对应代码块并退出
# else 可选，当所有条件都不满足时执行