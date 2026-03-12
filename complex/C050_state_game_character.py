# -----------------------------
# 题目：状态模式实现游戏角色状态。
# -----------------------------

class CharacterState:
    def enter(self, character):
        pass
    
    def exit(self, character):
        pass
    
    def update(self, character):
        pass
    
    def handle_input(self, character, input_type):
        pass
    
    def get_name(self):
        pass

class IdleState(CharacterState):
    def enter(self, character):
        character.animation = "idle"
    
    def handle_input(self, character, input_type):
        if input_type == "move":
            return MoveState()
        elif input_type == "jump":
            return JumpState()
        elif input_type == "attack":
            return AttackState()
        return None
    
    def get_name(self):
        return "待机"

class MoveState(CharacterState):
    def enter(self, character):
        character.animation = "run"
    
    def update(self, character):
        character.x += character.speed
    
    def handle_input(self, character, input_type):
        if input_type == "stop":
            return IdleState()
        elif input_type == "jump":
            return JumpState()
        elif input_type == "attack":
            return AttackState()
        return None
    
    def get_name(self):
        return "移动"

class JumpState(CharacterState):
    def __init__(self):
        self.jump_time = 0
        self.max_jump_time = 10
    
    def enter(self, character):
        character.animation = "jump"
        self.jump_time = 0
    
    def update(self, character):
        self.jump_time += 1
        if self.jump_time < self.max_jump_time / 2:
            character.y += 5
        else:
            character.y -= 5
    
    def handle_input(self, character, input_type):
        if self.jump_time >= self.max_jump_time:
            return IdleState()
        if input_type == "attack":
            return AttackState()
        return None
    
    def get_name(self):
        return "跳跃"

class AttackState(CharacterState):
    def __init__(self):
        self.attack_time = 0
        self.attack_duration = 5
    
    def enter(self, character):
        character.animation = "attack"
        self.attack_time = 0
    
    def update(self, character):
        self.attack_time += 1
    
    def handle_input(self, character, input_type):
        if self.attack_time >= self.attack_duration:
            return IdleState()
        return None
    
    def get_name(self):
        return "攻击"

class HurtState(CharacterState):
    def __init__(self):
        self.hurt_time = 0
        self.recovery_time = 10
    
    def enter(self, character):
        character.animation = "hurt"
        self.hurt_time = 0
    
    def update(self, character):
        self.hurt_time += 1
    
    def handle_input(self, character, input_type):
        if self.hurt_time >= self.recovery_time:
            return IdleState()
        return None
    
    def get_name(self):
        return "受伤"

class DeadState(CharacterState):
    def enter(self, character):
        character.animation = "dead"
    
    def handle_input(self, character, input_type):
        if input_type == "respawn":
            character.health = character.max_health
            return IdleState()
        return None
    
    def get_name(self):
        return "死亡"

class Character:
    def __init__(self, name):
        self.name = name
        self.x = 0
        self.y = 0
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.animation = "idle"
        self.state = IdleState()
        self.state.enter(self)
    
    def change_state(self, new_state):
        if new_state:
            self.state.exit(self)
            self.state = new_state
            self.state.enter(self)
    
    def handle_input(self, input_type):
        if self.health <= 0:
            self.change_state(DeadState())
            return
        new_state = self.state.handle_input(self, input_type)
        self.change_state(new_state)
    
    def update(self):
        self.state.update(self)
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.change_state(DeadState())
        else:
            self.change_state(HurtState())
    
    def get_status(self):
        return {
            'name': self.name,
            'position': (self.x, self.y),
            'health': self.health,
            'state': self.state.get_name(),
            'animation': self.animation
        }

def main():
    hero = Character("勇者")
    
    print("=== 初始状态 ===")
    print(hero.get_status())
    
    print("\n=== 移动 ===")
    hero.handle_input("move")
    hero.update()
    print(hero.get_status())
    
    print("\n=== 跳跃 ===")
    hero.handle_input("jump")
    for _ in range(12):
        hero.update()
    print(hero.get_status())
    
    print("\n=== 攻击 ===")
    hero.handle_input("attack")
    for _ in range(6):
        hero.update()
    print(hero.get_status())
    
    print("\n=== 受伤 ===")
    hero.take_damage(30)
    print(hero.get_status())
    
    for _ in range(12):
        hero.update()
    print(f"恢复后: {hero.get_status()}")
    
    print("\n=== 致命伤害 ===")
    hero.take_damage(100)
    print(hero.get_status())
    
    print("\n=== 复活 ===")
    hero.handle_input("respawn")
    print(hero.get_status())


if __name__ == "__main__":
    main()
