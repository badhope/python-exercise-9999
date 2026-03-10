# -----------------------------
# 题目：酒店房间管理。
# 描述：实现酒店房间预订系统。
# -----------------------------

class Room:
    def __init__(self, room_number, room_type, price):
        self.room_number = room_number
        self.room_type = room_type
        self.price = price
        self.is_available = True
    
    def __str__(self):
        status = "可预订" if self.is_available else "已预订"
        return f"房间{self.room_number} ({self.room_type}) - {self.price}元/晚 - {status}"

class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
    
    def add_room(self, room):
        self.rooms.append(room)
    
    def book_room(self, room_number):
        for room in self.rooms:
            if room.room_number == room_number and room.is_available:
                room.is_available = False
                return True
        return False
    
    def available_rooms(self):
        return [room for room in self.rooms if room.is_available]

def main():
    hotel = Hotel("豪华大酒店")
    hotel.add_room(Room(101, "单人间", 200))
    hotel.add_room(Room(102, "双人间", 350))
    hotel.add_room(Room(103, "套房", 600))
    print("可预订房间:")
    for room in hotel.available_rooms():
        print(room)
    hotel.book_room(101)
    print("预订后:")
    print(hotel.available_rooms()[0])


if __name__ == "__main__":
    main()
