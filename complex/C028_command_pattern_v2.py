# -----------------------------
# 题目：命令模式实现智能家居控制。
# -----------------------------

class Device:
    def __init__(self, name):
        self.name = name
        self.status = False
    
    def on(self):
        self.status = True
        return f"{self.name}已开启"
    
    def off(self):
        self.status = False
        return f"{self.name}已关闭"

class Light(Device):
    def __init__(self, name):
        super().__init__(name)
        self.brightness = 100
    
    def set_brightness(self, level):
        self.brightness = max(0, min(100, level))
        return f"{self.name}亮度设为{self.brightness}%"

class AirConditioner(Device):
    def __init__(self, name):
        super().__init__(name)
        self.temperature = 26
    
    def set_temperature(self, temp):
        self.temperature = temp
        return f"{self.name}温度设为{temp}°C"

class Command:
    def execute(self):
        pass
    
    def undo(self):
        pass

class TurnOnCommand(Command):
    def __init__(self, device):
        self.device = device
    
    def execute(self):
        return self.device.on()
    
    def undo(self):
        return self.device.off()

class TurnOffCommand(Command):
    def __init__(self, device):
        self.device = device
    
    def execute(self):
        return self.device.off()
    
    def undo(self):
        return self.device.on()

class SetBrightnessCommand(Command):
    def __init__(self, light, brightness):
        self.light = light
        self.brightness = brightness
        self.old_brightness = light.brightness
    
    def execute(self):
        return self.light.set_brightness(self.brightness)
    
    def undo(self):
        return self.light.set_brightness(self.old_brightness)

class SetTemperatureCommand(Command):
    def __init__(self, ac, temperature):
        self.ac = ac
        self.temperature = temperature
        self.old_temperature = ac.temperature
    
    def execute(self):
        return self.ac.set_temperature(self.temperature)
    
    def undo(self):
        return self.ac.set_temperature(self.old_temperature)

class RemoteControl:
    def __init__(self):
        self.commands = {}
        self.history = []
    
    def set_command(self, slot, command):
        self.commands[slot] = command
    
    def press(self, slot):
        if slot in self.commands:
            result = self.commands[slot].execute()
            self.history.append(self.commands[slot])
            return result
        return "无此命令"
    
    def undo(self):
        if self.history:
            command = self.history.pop()
            return command.undo()
        return "无操作可撤销"

class MacroCommand(Command):
    def __init__(self, commands):
        self.commands = commands
    
    def execute(self):
        results = []
        for cmd in self.commands:
            results.append(cmd.execute())
        return "\n".join(results)
    
    def undo(self):
        results = []
        for cmd in reversed(self.commands):
            results.append(cmd.undo())
        return "\n".join(results)

def main():
    light = Light("客厅灯")
    ac = AirConditioner("客厅空调")
    
    remote = RemoteControl()
    remote.set_command(1, TurnOnCommand(light))
    remote.set_command(2, TurnOnCommand(ac))
    remote.set_command(3, SetBrightnessCommand(light, 50))
    remote.set_command(4, SetTemperatureCommand(ac, 24))
    
    print("=== 执行命令 ===")
    print(remote.press(1))
    print(remote.press(2))
    print(remote.press(3))
    print(remote.press(4))
    
    print("\n=== 撤销操作 ===")
    print(remote.undo())
    print(remote.undo())
    
    print("\n=== 宏命令：回家模式 ===")
    home_command = MacroCommand([
        TurnOnCommand(light),
        SetBrightnessCommand(light, 80),
        TurnOnCommand(ac),
        SetTemperatureCommand(ac, 26)
    ])
    remote.set_command(5, home_command)
    print(remote.press(5))


if __name__ == "__main__":
    main()
