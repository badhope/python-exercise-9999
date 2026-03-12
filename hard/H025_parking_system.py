# -----------------------------
# 题目：实现停车场管理系统。
# 描述：管理停车位、车辆进出、计费等功能。
# -----------------------------

from datetime import datetime, timedelta

class ParkingSpot:
    def __init__(self, spot_id, spot_type="regular"):
        self.id = spot_id
        self.type = spot_type
        self.is_occupied = False
        self.vehicle = None
        self.entry_time = None
    
    def park(self, vehicle_plate):
        if self.is_occupied:
            return False
        self.is_occupied = True
        self.vehicle = vehicle_plate
        self.entry_time = datetime.now()
        return True
    
    def leave(self):
        if not self.is_occupied:
            return None
        vehicle = self.vehicle
        entry = self.entry_time
        self.is_occupied = False
        self.vehicle = None
        self.entry_time = None
        return vehicle, entry

class Vehicle:
    def __init__(self, plate, vehicle_type="car"):
        self.plate = plate
        self.type = vehicle_type

class ParkingRecord:
    def __init__(self, record_id, plate, spot_id, entry_time, exit_time, fee):
        self.id = record_id
        self.plate = plate
        self.spot_id = spot_id
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.fee = fee

class ParkingLot:
    def __init__(self, name, regular_spots=50, vip_spots=10):
        self.name = name
        self.spots = {}
        self.records = []
        self.hourly_rate = {"regular": 5, "vip": 10}
        self.next_spot_id = 1
        self.next_record_id = 1
        
        for _ in range(regular_spots):
            spot = ParkingSpot(self.next_spot_id, "regular")
            self.spots[self.next_spot_id] = spot
            self.next_spot_id += 1
        
        for _ in range(vip_spots):
            spot = ParkingSpot(self.next_spot_id, "vip")
            self.spots[self.next_spot_id] = spot
            self.next_spot_id += 1
    
    def find_available_spot(self, spot_type="regular"):
        for spot in self.spots.values():
            if not spot.is_occupied and spot.type == spot_type:
                return spot
        return None
    
    def park_vehicle(self, plate, spot_type="regular"):
        spot = self.find_available_spot(spot_type)
        if not spot:
            return None, "没有可用车位"
        
        spot.park(plate)
        return spot.id, f"停车成功，车位号: {spot.id}"
    
    def remove_vehicle(self, spot_id):
        spot = self.spots.get(spot_id)
        if not spot:
            return None, "车位不存在"
        
        result = spot.leave()
        if not result:
            return None, "车位为空"
        
        vehicle, entry_time = result
        exit_time = datetime.now()
        fee = self._calculate_fee(entry_time, exit_time, spot.type)
        
        record = ParkingRecord(self.next_record_id, vehicle, spot_id, 
                              entry_time, exit_time, fee)
        self.records.append(record)
        self.next_record_id += 1
        
        return record.id, f"离场成功，停车费: {fee}元"
    
    def _calculate_fee(self, entry_time, exit_time, spot_type):
        duration = exit_time - entry_time
        hours = duration.total_seconds() / 3600
        hours = max(1, int(hours) + (1 if hours % 1 > 0 else 0))
        return hours * self.hourly_rate[spot_type]
    
    def get_occupied_spots(self):
        return [spot for spot in self.spots.values() if spot.is_occupied]
    
    def get_available_spots(self):
        return [spot for spot in self.spots.values() if not spot.is_occupied]
    
    def get_vehicle_spot(self, plate):
        for spot in self.spots.values():
            if spot.vehicle == plate:
                return spot
        return None
    
    def get_stats(self):
        total = len(self.spots)
        occupied = len(self.get_occupied_spots())
        regular_available = sum(1 for s in self.get_available_spots() if s.type == "regular")
        vip_available = sum(1 for s in self.get_available_spots() if s.type == "vip")
        
        return {
            'total_spots': total,
            'occupied_spots': occupied,
            'available_spots': total - occupied,
            'regular_available': regular_available,
            'vip_available': vip_available,
            'occupancy_rate': f"{occupied/total*100:.1f}%"
        }

def main():
    lot = ParkingLot("中心停车场", regular_spots=10, vip_spots=5)
    
    lot.park_vehicle("京A12345", "regular")
    lot.park_vehicle("京B67890", "regular")
    lot.park_vehicle("京C11111", "vip")
    
    print("停车场统计:")
    stats = lot.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n已占用车位:")
    for spot in lot.get_occupied_spots():
        print(f"  车位{spot.id}: {spot.vehicle} ({spot.type})")


if __name__ == "__main__":
    main()
