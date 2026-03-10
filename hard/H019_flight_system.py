# -----------------------------
# 题目：航班信息系统。
# 描述：实现航班信息管理系统。
# -----------------------------

class Flight:
    def __init__(self, flight_number, origin, destination, price):
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.price = price
        self.available_seats = 100
    
    def book_seat(self):
        if self.available_seats > 0:
            self.available_seats -= 1
            return True
        return False
    
    def cancel_seat(self):
        if self.available_seats < 100:
            self.available_seats += 1
            return True
        return False
    
    def __str__(self):
        return f"{self.flight_number}: {self.origin} -> {self.destination}, 票价: {self.price}, 余票: {self.available_seats}"

def main():
    flight = Flight("CA1234", "北京", "上海", 850)
    print(flight)
    flight.book_seat()
    print(f"订票后余票: {flight.available_seats}")
    flight.cancel_seat()
    print(f"退票后余票: {flight.available_seats}")


if __name__ == "__main__":
    main()
