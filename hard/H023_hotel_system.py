# -----------------------------
# 题目：实现酒店预订系统。
# 描述：管理房间预订、入住、退房等功能。
# -----------------------------

from datetime import datetime, date, timedelta

class Room:
    def __init__(self, room_id, room_type, price):
        self.id = room_id
        self.type = room_type
        self.price = price
        self.status = "available"
        self.current_guest = None
    
    def is_available(self, check_in, check_out, bookings):
        for booking in bookings:
            if booking.room_id == self.id:
                if not (check_out <= booking.check_in or check_in >= booking.check_out):
                    return False
        return True

class Booking:
    def __init__(self, booking_id, room_id, guest_name, check_in, check_out):
        self.id = booking_id
        self.room_id = room_id
        self.guest_name = guest_name
        self.check_in = check_in
        self.check_out = check_out
        self.status = "confirmed"
        self.created_at = datetime.now()
    
    def get_nights(self):
        return (self.check_out - self.check_in).days
    
    def get_total_price(self, room_price):
        return self.get_nights() * room_price

class HotelSystem:
    def __init__(self):
        self.rooms = {}
        self.bookings = []
        self.next_room_id = 101
        self.next_booking_id = 1
    
    def add_room(self, room_type, price):
        room = Room(self.next_room_id, room_type, price)
        self.rooms[self.next_room_id] = room
        self.next_room_id += 1
        return room.id
    
    def search_available_rooms(self, check_in, check_out, room_type=None):
        available = []
        for room in self.rooms.values():
            if room_type and room.type != room_type:
                continue
            if room.is_available(check_in, check_out, self.bookings):
                available.append(room)
        return available
    
    def book_room(self, room_id, guest_name, check_in, check_out):
        room = self.rooms.get(room_id)
        if not room:
            return None, "房间不存在"
        
        if not room.is_available(check_in, check_out, self.bookings):
            return None, "房间已被预订"
        
        booking = Booking(self.next_booking_id, room_id, guest_name, check_in, check_out)
        self.bookings.append(booking)
        self.next_booking_id += 1
        
        return booking.id, f"预订成功，总价: {booking.get_total_price(room.price)}元"
    
    def cancel_booking(self, booking_id):
        for booking in self.bookings:
            if booking.id == booking_id and booking.status == "confirmed":
                booking.status = "cancelled"
                return True, "取消成功"
        return False, "预订不存在或已取消"
    
    def check_in(self, booking_id):
        for booking in self.bookings:
            if booking.id == booking_id and booking.status == "confirmed":
                room = self.rooms.get(booking.room_id)
                if room:
                    room.status = "occupied"
                    room.current_guest = booking.guest_name
                    booking.status = "checked_in"
                    return True, "入住成功"
        return False, "预订不存在或状态不符"
    
    def check_out(self, booking_id):
        for booking in self.bookings:
            if booking.id == booking_id and booking.status == "checked_in":
                room = self.rooms.get(booking.room_id)
                if room:
                    room.status = "available"
                    room.current_guest = None
                    booking.status = "checked_out"
                    return True, "退房成功"
        return False, "预订不存在或状态不符"
    
    def get_guest_bookings(self, guest_name):
        return [b for b in self.bookings if b.guest_name == guest_name]
    
    def get_stats(self):
        total_rooms = len(self.rooms)
        occupied = sum(1 for r in self.rooms.values() if r.status == "occupied")
        
        return {
            'total_rooms': total_rooms,
            'available_rooms': total_rooms - occupied,
            'occupied_rooms': occupied,
            'total_bookings': len(self.bookings),
            'active_bookings': sum(1 for b in self.bookings if b.status == "confirmed")
        }

def main():
    hotel = HotelSystem()
    
    hotel.add_room("标准间", 200)
    hotel.add_room("标准间", 200)
    hotel.add_room("豪华间", 400)
    hotel.add_room("套房", 800)
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    b1, _ = hotel.book_room(101, "张三", today, tomorrow)
    b2, _ = hotel.book_room(103, "李四", today, next_week)
    
    print("酒店统计:")
    stats = hotel.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n搜索可用房间({today} - {tomorrow}):")
    available = hotel.search_available_rooms(today, tomorrow)
    for room in available:
        print(f"  {room.id}号房 - {room.type} - {room.price}元/晚")


if __name__ == "__main__":
    main()
