# -----------------------------
# 题目：停车场管理系统。
# 描述：实现停车场管理系统，管理车位和车辆进出。
# -----------------------------

class Car:
    def __init__(self, plate_number, color, brand):
        self.plate_number = plate_number
        self.color = color
        self.brand = brand
    
    def __str__(self):
        return f"{self.plate_number} - {self.color} {self.brand}"

class ParkingLot:
    def __init__(self, total_spaces):
        self.total_spaces = total_spaces
        self.spaces = [None] * total_spaces
    
    def park(self, car):
        for i in range(self.total_spaces):
            if self.spaces[i] is None:
                self.spaces[i] = car
                return i + 1
        return -1
    
    def leave(self, plate_number):
        for i in range(self.total_spaces):
            if self.spaces[i] and self.spaces[i].plate_number == plate_number:
                self.spaces[i] = None
                return True
        return False
    
    def get_available_spaces(self):
        return self.spaces.count(None)
    
    def get_occupied_spaces(self):
        return self.total_spaces - self.get_available_spaces()

def main():
    lot = ParkingLot(10)
    lot.park(Car("京A12345", "黑色", "宝马"))
    lot.park(Car("京B67890", "白色", "奥迪"))
    print(f"可用车位: {lot.get_available_spaces()}")
    print(f"已用车位: {lot.get_occupied_spaces()}")
    lot.leave("京A12345")
    print(f"离开后可用车位: {lot.get_available_spaces()}")


if __name__ == "__main__":
    main()
