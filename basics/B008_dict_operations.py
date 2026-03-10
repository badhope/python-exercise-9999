# -----------------------------
# 题目：字典基本操作。
# 描述：创建字典 person = {"name": "Alice", "age": 25}，添加"city": "Beijing"，修改age为26，删除后输出。
# -----------------------------

def main():
    person = {"name": "Alice", "age": 25}
    
    person["city"] = "Beijing"
    person["age"] = 26
    
    print(f"字典操作后: {person}")
    print(f"姓名: {person['name']}")
    print(f"所有键: {list(person.keys())}")
    print(f"所有值: {list(person.values())}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# 字典是键值对集合，通过键访问值
# 添加/修改：dict[key] = value
# keys()：返回所有键的视图
# values()：返回所有值的视图