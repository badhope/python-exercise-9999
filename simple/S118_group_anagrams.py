# -----------------------------
# 题目：字母异位词分组。
# 描述：将字母异位词分组。
# -----------------------------

from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())

def main():
    print(f"分组: {group_anagrams(['eat','tea','tan','ate','nat','bat'])}")


if __name__ == "__main__":
    main()
