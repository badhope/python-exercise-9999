# -----------------------------
# 题目：桥接模式实现设备控制。
# 描述：使用桥接模式分离设备抽象和实现。
# -----------------------------

class Device:
    def turn_on(self):
        pass
    
    def turn_off(self):
        pass

class TV(Device):
    def turn_on(self):
        return "电视开机"
    
    def turn_off(self):
        return "电视关机"

class Radio(Device):
    def turn_on(self):
        return "收音机开机"
    
    def turn_off(self):
        return "收音机关机"

class RemoteControl:
    def __init__(self, device):
        self.device = device
    
    def power_on(self):
        return self.device.turn_on()
    
    def power_off(self):
        return self.device.turn_off()

def main():
    tv_remote = RemoteControl(TV())
    radio_remote = RemoteControl(Radio())
    print(tv_remote.power_on())
    print(radio_remote.power_on())


if __name__ == "__main__":
    main()
