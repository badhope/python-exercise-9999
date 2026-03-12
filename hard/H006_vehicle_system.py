# -----------------------------
# 题目：车辆管理系统。
# 描述：实现车辆信息的登记、查询、状态管理。
# -----------------------------

class Vehicle:
    def __init__(self, plate_number, brand, color):
        self.plate_number = plate_number
        self.brand = brand
        self.color = color
        self.status = "正常"

class VehicleManager:
    def __init__(self):
        self.vehicles = {}
    
    def register(self, plate_number, brand, color):
        self.vehicles[plate_number] = Vehicle(plate_number, brand, color)
    
    def get_vehicle(self, plate_number):
        return self.vehicles.get(plate_number)
    
    def update_status(self, plate_number, status):
        if plate_number in self.vehicles:
            self.vehicles[plate_number].status = status
    
    def search_by_brand(self, brand):
        return [v for v in self.vehicles.values() if v.brand == brand]
    
    def get_all(self):
        return list(self.vehicles.values())

def main():
    manager = VehicleManager()
    manager.register("京A12345", "宝马", "黑色")
    manager.register("京B67890", "奥迪", "白色")
    vehicle = manager.get_vehicle("京A12345")
    print(f"车牌: {vehicle.plate_number}, 品牌: {vehicle.brand}, 颜色: {vehicle.color}")


if __name__ == "__main__":
    main()
