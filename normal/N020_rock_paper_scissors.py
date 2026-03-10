# -----------------------------
# 题目：石头剪刀布游戏。
# 描述：实现石头剪刀布游戏，人机对战。
# -----------------------------

import random

def get_computer_choice():
    return random.choice(["石头", "剪刀", "布"])

def determine_winner(player, computer):
    if player == computer:
        return "平局"
    if (player == "石头" and computer == "剪刀") or \
       (player == "剪刀" and computer == "布") or \
       (player == "布" and computer == "石头"):
        return "玩家获胜"
    return "电脑获胜"

def main():
    choices = ["石头", "剪刀", "布"]
    player = "石头"
    computer = get_computer_choice()
    result = determine_winner(player, computer)
    print(f"玩家: {player}, 电脑: {computer}")
    print(f"结果: {result}")


if __name__ == "__main__":
    main()
