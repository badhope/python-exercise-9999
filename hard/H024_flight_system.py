# -----------------------------
# 题目：实现航班预订系统。
# 描述：管理航班查询、预订、取消等功能。
# -----------------------------

from datetime import datetime, date

class Flight:
    def __init__(self, flight_id, flight_no, origin, destination, departure_time, arrival_time, price, capacity):
        self.id = flight_id
        self.flight_no = flight_no
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.price = price
        self.capacity = capacity
        self.booked_seats = 0
    
    def get_available_seats(self):
        return self.capacity - self.booked_seats
    
    def book_seat(self, count=1):
        if self.booked_seats + count <= self.capacity:
            self.booked_seats += count
            return True
        return False
    
    def cancel_seat(self, count=1):
        if self.booked_seats >= count:
            self.booked_seats -= count
            return True
        return False

class Passenger:
    def __init__(self, passenger_id, name, id_card):
        self.id = passenger_id
        self.name = name
        self.id_card = id_card

class Ticket:
    def __init__(self, ticket_id, flight_id, passenger_id, seat_no):
        self.id = ticket_id
        self.flight_id = flight_id
        self.passenger_id = passenger_id
        self.seat_no = seat_no
        self.status = "confirmed"
        self.created_at = datetime.now()

class FlightBookingSystem:
    def __init__(self):
        self.flights = {}
        self.passengers = {}
        self.tickets = {}
        self.next_flight_id = 1
        self.next_passenger_id = 1
        self.next_ticket_id = 1
    
    def add_flight(self, flight_no, origin, destination, departure_time, arrival_time, price, capacity):
        flight = Flight(self.next_flight_id, flight_no, origin, destination, 
                       departure_time, arrival_time, price, capacity)
        self.flights[self.next_flight_id] = flight
        self.next_flight_id += 1
        return flight.id
    
    def add_passenger(self, name, id_card):
        passenger = Passenger(self.next_passenger_id, name, id_card)
        self.passengers[self.next_passenger_id] = passenger
        self.next_passenger_id += 1
        return passenger.id
    
    def search_flights(self, origin, destination, date=None):
        results = []
        for flight in self.flights.values():
            if flight.origin == origin and flight.destination == destination:
                if date is None or flight.departure_time.date() == date:
                    results.append(flight)
        return results
    
    def book_ticket(self, flight_id, passenger_id):
        flight = self.flights.get(flight_id)
        passenger = self.passengers.get(passenger_id)
        
        if not flight or not passenger:
            return None, "航班或乘客不存在"
        
        if not flight.book_seat():
            return None, "航班已满"
        
        seat_no = f"{flight.booked_seats:03d}"
        ticket = Ticket(self.next_ticket_id, flight_id, passenger_id, seat_no)
        self.tickets[self.next_ticket_id] = ticket
        self.next_ticket_id += 1
        
        return ticket.id, f"预订成功，座位号: {seat_no}，票价: {flight.price}元"
    
    def cancel_ticket(self, ticket_id):
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False, "票不存在"
        
        if ticket.status != "confirmed":
            return False, "票已取消或已使用"
        
        flight = self.flights.get(ticket.flight_id)
        if flight:
            flight.cancel_seat()
        
        ticket.status = "cancelled"
        return True, "取消成功"
    
    def get_passenger_tickets(self, passenger_id):
        return [t for t in self.tickets.values() if t.passenger_id == passenger_id]
    
    def get_flight_info(self, flight_id):
        flight = self.flights.get(flight_id)
        if flight:
            return {
                'flight_no': flight.flight_no,
                'route': f"{flight.origin} -> {flight.destination}",
                'departure': flight.departure_time.strftime('%Y-%m-%d %H:%M'),
                'arrival': flight.arrival_time.strftime('%Y-%m-%d %H:%M'),
                'price': flight.price,
                'available_seats': flight.get_available_seats()
            }
        return None
    
    def get_stats(self):
        return {
            'total_flights': len(self.flights),
            'total_passengers': len(self.passengers),
            'total_tickets': len(self.tickets),
            'active_tickets': sum(1 for t in self.tickets.values() if t.status == "confirmed")
        }

def main():
    system = FlightBookingSystem()
    
    f1 = system.add_flight("CA1234", "北京", "上海", 
                          datetime(2024, 1, 15, 8, 0), 
                          datetime(2024, 1, 15, 10, 30), 800, 180)
    f2 = system.add_flight("MU5678", "北京", "广州",
                          datetime(2024, 1, 15, 14, 0),
                          datetime(2024, 1, 15, 17, 0), 1200, 150)
    
    p1 = system.add_passenger("张三", "110101199001011234")
    p2 = system.add_passenger("李四", "110101199002021234")
    
    t1, _ = system.book_ticket(f1, p1)
    t2, _ = system.book_ticket(f1, p2)
    
    print("系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n搜索航班(北京->上海):")
    flights = system.search_flights("北京", "上海")
    for flight in flights:
        print(f"  {flight.flight_no}: {flight.origin}->{flight.destination}, "
              f"剩余座位: {flight.get_available_seats()}")


if __name__ == "__main__":
    main()
