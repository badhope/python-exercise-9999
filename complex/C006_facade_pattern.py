# -----------------------------
# 题目：外观模式实现系统简化。
# 描述：使用外观模式简化复杂子系统的调用。
# -----------------------------

class CPU:
    def freeze(self):
        return "CPU冻结"
    
    def jump(self, position):
        return f"CPU跳转到 {position}"
    
    def execute(self):
        return "CPU执行"

class Memory:
    def load(self, position, data):
        return f"内存加载 {data} 到 {position}"

class HardDrive:
    def read(self, lba, size):
        return f"硬盘读取 LBA={lba}, 大小={size}"

class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()
    
    def start(self):
        results = []
        results.append(self.cpu.freeze())
        results.append(self.memory.load(0, "BOOT_SECTOR"))
        results.append(self.hard_drive.read(0, 1024))
        results.append(self.cpu.jump(0))
        results.append(self.cpu.execute())
        return results

def main():
    computer = ComputerFacade()
    for result in computer.start():
        print(result)


if __name__ == "__main__":
    main()
