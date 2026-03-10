# -----------------------------
# 题目：扁平化嵌套列表。
# 描述：将嵌套列表展平为单一列表。
# -----------------------------

def flatten_list(nested):
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result

def main():
    print(f"扁平化: {flatten_list([1,[2,3],[4,[5,6]]])}")


if __name__ == "__main__":
    main()
