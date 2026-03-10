# -----------------------------
# 题目：文字版回合制 RPG 战斗游戏。
# 描述：玩家和敌人轮流攻击，直到一方血量归零。
#      功能：玩家可以攻击或使用药水回血，敌人自动攻击。
#      要求：包含血量判断、回合逻辑、胜负判定。
#
# 示例：
# [回合 1]
# 玩家 HP: 100 | 敌人 HP: 80
# 选择: 1.攻击 2.药水
# 输入：1
# 玩家攻击! 敌人损失 20 HP.
# 敌人反击! 玩家损失 15 HP.
# -----------------------------

# 制作提示：
# 1. 设计两个类：Player, Enemy。
# 2. 需要一个主循环 `while player.hp > 0 and enemy.hp > 0`。
# 3. 使用 `random.randint` 生成伤害波动值，增加随机性。
# 4. 处理输入，玩家回合和敌人回合交替进行。

# ========== 普通答案 ==========
import random
import time

class Player:
    def __init__(self):
        self.hp = 100
        self.attack_power = 20

    def attack(self, enemy):
        damage = random.randint(self.attack_power - 5, self.attack_power + 5)
        enemy.hp -= damage
        print(f"⚔️ 玩家发动攻击，造成 {damage} 点伤害！")
    
    def heal(self):
        heal_amount = random.randint(10, 20)
        self.hp += heal_amount
        print(f"💊 玩家喝了药水，恢复了 {heal_amount} HP！")

class Enemy:
    def __init__(self):
        self.hp = 80
        self.attack_power = 15

    def attack(self, player):
        damage = random.randint(self.attack_power - 3, self.attack_power + 3)
        player.hp -= damage
        print(f"👾 敌人反击，造成 {damage} 点伤害！")

def game_loop():
    p = Player()
    e = Enemy()
    turn = 1

    print("=== 游戏开始 ===")
    
    while p.hp > 0 and e.hp > 0:
        print(f"\n[回合 {turn}]")
        print(f"玩家 HP: {p.hp} | 敌人 HP: {e.hp}")
        
        # 玩家回合
        choice = input("行动 (1.攻击 2.药水): ")
        if choice == '1':
            p.attack(e)
        elif choice == '2':
            p.heal()
        else:
            print("犹豫了，浪费了一回合...")

        # 判断敌人死没死
        if e.hp <= 0:
            print("\n🎉 恭喜！你击败了敌人！")
            break

        # 敌人回合
        time.sleep(1) # 停顿一秒增加紧张感
        e.attack(p)

        # 判断玩家死没死
        if p.hp <= 0:
            print("\n💀 你被打败了...游戏结束。")
            break
            
        turn += 1

if __name__ == "__main__":
    game_loop()

# ========== 运行效果 ==========
# [回合 1]
# 玩家 HP: 100 | 敌人 HP: 80
# 行动 (1.攻击 2.药水): 1
# ⚔️ 玩家发动攻击，造成 22 点伤害！
# 👾 敌人反击，造成 14 点伤害！

# ========== 详细解析版 ==========
import random
import time

# 定义玩家类
class Player:
    def __init__(self):
        self.hp = 100
        self.attack_power = 20
    
    # 攻击方法，传入敌人对象
    def attack(self, enemy):
        # 伤害浮动，模拟暴击或未击中要害
        damage = random.randint(self.attack_power - 5, self.attack_power + 5)
        # 直接修改敌人的血量
        enemy.hp -= damage
        print(f"⚔️ 玩家发动攻击，造成 {damage} 点伤害！")
    
    # 回血方法
    def heal(self):
        heal_amount = random.randint(10, 20)
        self.hp += heal_amount
        print(f"💊 玩家喝了药水，恢复了 {heal_amount} HP！")

# 定义敌人类
class Enemy:
    def __init__(self):
        self.hp = 80
        self.attack_power = 15
        
    def attack(self, player):
        damage = random.randint(self.attack_power - 3, self.attack_power + 3)
        player.hp -= damage
        print(f"👾 敌人反击，造成 {damage} 点伤害！")

# 游戏主循环函数
def game_loop():
    # 实例化对象
    p = Player()
    e = Enemy()
    turn = 1

    print("=== 游戏开始 ===")
    
    # 只要双方都活着，就一直循环
    while p.hp > 0 and e.hp > 0:
        print(f"\n[回合 {turn}]")
        # 显示当前状态
        print(f"玩家 HP: {p.hp} | 敌人 HP: {e.hp}")
        
        # === 玩家回合 ===
        choice = input("行动 (1.攻击 2.药水): ")
        if choice == '1':
            p.attack(e)
        elif choice == '2':
            p.heal()
        else:
            print("犹豫了，浪费了一回合...")

        # 每次玩家行动后，都要检查敌人是否挂了
        if e.hp <= 0:
            print("\n🎉 恭喜！你击败了敌人！")
            # 跳出循环，游戏结束
            break

        # === 敌人回合 ===
        # 暂停1秒，让玩家看清楚发生了什么
        time.sleep(1)
        e.attack(p)

        # 敌人行动后，检查玩家是否挂了
        if p.hp <= 0:
            print("\n💀 你被打败了...游戏结束。")
            break
            
        turn += 1

# 启动游戏
if __name__ == "__main__":
    game_loop()

# ========== 大白话解释 ==========
# 这就是一个小型的战场模拟器。
# Player 和 Enemy 是两个战士，站在两边。
# while 循环是倒计时钟，叮咚一声就是一个回合。
# 你在回合里下指令（攻击或喝药），程序帮你算伤害扣血。
# 一旦谁的血条（HP）空了，循环就打破，游戏结束。
# 这里面包含了状态管理（HP变化）、逻辑判断（胜负）、交互，这就是做游戏最核心的骨架。

# ========== 扩展语句 ==========
# 扩展：给敌人加个“AI”，如果敌人血量低于20%，有50%概率选择防御而不是攻击。
# 或者增加“暴击”机制，有10%概率造成双倍伤害。
