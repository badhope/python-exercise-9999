# -----------------------------
# 题目：身份证信息解析。
# 描述：从身份证号码中提取出生日期和性别。
# -----------------------------

def parse_id_card(id_card):
    if len(id_card) != 18:
        return None
    birth_year = int(id_card[6:10])
    birth_month = int(id_card[10:12])
    birth_day = int(id_card[12:14])
    gender = "女" if int(id_card[16]) % 2 == 0 else "男"
    birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    return birth_date, gender

def main():
    id_card = "110101199001011234"
    birth_date, gender = parse_id_card(id_card)
    print(f"身份证: {id_card}")
    print(f"出生日期: {birth_date}")
    print(f"性别: {gender}")


if __name__ == "__main__":
    main()
