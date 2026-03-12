# -----------------------------
# 题目：实现电影院售票系统。
# 描述：管理电影、场次、座位、售票等功能。
# -----------------------------

from datetime import datetime, date

class Movie:
    def __init__(self, movie_id, title, duration, genre, rating):
        self.id = movie_id
        self.title = title
        self.duration = duration
        self.genre = genre
        self.rating = rating

class Hall:
    def __init__(self, hall_id, name, rows, cols):
        self.id = hall_id
        self.name = name
        self.rows = rows
        self.cols = cols
    
    def get_total_seats(self):
        return self.rows * self.cols

class Screening:
    def __init__(self, screening_id, movie_id, hall_id, start_time, price):
        self.id = screening_id
        self.movie_id = movie_id
        self.hall_id = hall_id
        self.start_time = start_time
        self.price = price
        self.seats = {}
    
    def init_seats(self, rows, cols):
        for row in range(1, rows + 1):
            for col in range(1, cols + 1):
                seat_no = f"{row}-{col}"
                self.seats[seat_no] = {"status": "available", "user": None}
    
    def book_seat(self, seat_no, user_id):
        if seat_no in self.seats and self.seats[seat_no]["status"] == "available":
            self.seats[seat_no]["status"] = "booked"
            self.seats[seat_no]["user"] = user_id
            return True
        return False
    
    def cancel_seat(self, seat_no):
        if seat_no in self.seats and self.seats[seat_no]["status"] == "booked":
            self.seats[seat_no]["status"] = "available"
            self.seats[seat_no]["user"] = None
            return True
        return False
    
    def get_available_seats(self):
        return [seat for seat, info in self.seats.items() 
                if info["status"] == "available"]
    
    def get_booked_seats(self):
        return [seat for seat, info in self.seats.items() 
                if info["status"] == "booked"]

class Ticket:
    def __init__(self, ticket_id, screening_id, seat_no, user_id, price):
        self.id = ticket_id
        self.screening_id = screening_id
        self.seat_no = seat_no
        self.user_id = user_id
        self.price = price
        self.status = "valid"
        self.created_at = datetime.now()

class CinemaSystem:
    def __init__(self):
        self.movies = {}
        self.halls = {}
        self.screenings = {}
        self.tickets = {}
        self.next_movie_id = 1
        self.next_hall_id = 1
        self.next_screening_id = 1
        self.next_ticket_id = 1
    
    def add_movie(self, title, duration, genre, rating):
        movie = Movie(self.next_movie_id, title, duration, genre, rating)
        self.movies[self.next_movie_id] = movie
        self.next_movie_id += 1
        return movie.id
    
    def add_hall(self, name, rows, cols):
        hall = Hall(self.next_hall_id, name, rows, cols)
        self.halls[self.next_hall_id] = hall
        self.next_hall_id += 1
        return hall.id
    
    def add_screening(self, movie_id, hall_id, start_time, price):
        screening = Screening(self.next_screening_id, movie_id, hall_id, 
                             start_time, price)
        hall = self.halls.get(hall_id)
        if hall:
            screening.init_seats(hall.rows, hall.cols)
        
        self.screenings[self.next_screening_id] = screening
        self.next_screening_id += 1
        return screening.id
    
    def get_screenings_by_movie(self, movie_id, schedule_date=None):
        result = []
        for screening in self.screenings.values():
            if screening.movie_id == movie_id:
                if schedule_date is None or screening.start_time.date() == schedule_date:
                    result.append(screening)
        return result
    
    def book_tickets(self, screening_id, seat_list, user_id):
        screening = self.screenings.get(screening_id)
        if not screening:
            return [], "场次不存在"
        
        booked = []
        for seat_no in seat_list:
            if screening.book_seat(seat_no, user_id):
                ticket = Ticket(self.next_ticket_id, screening_id, seat_no, 
                               user_id, screening.price)
                self.tickets[self.next_ticket_id] = ticket
                booked.append(ticket)
                self.next_ticket_id += 1
        
        if booked:
            return booked, f"成功预订{len(booked)}张票"
        return [], "预订失败"
    
    def cancel_ticket(self, ticket_id):
        ticket = self.tickets.get(ticket_id)
        if not ticket or ticket.status != "valid":
            return False, "票不存在或已失效"
        
        screening = self.screenings.get(ticket.screening_id)
        if screening:
            screening.cancel_seat(ticket.seat_no)
        
        ticket.status = "cancelled"
        return True, "退票成功"
    
    def get_user_tickets(self, user_id):
        return [t for t in self.tickets.values() 
                if t.user_id == user_id and t.status == "valid"]
    
    def get_screening_info(self, screening_id):
        screening = self.screenings.get(screening_id)
        movie = self.movies.get(screening.movie_id) if screening else None
        hall = self.halls.get(screening.hall_id) if screening else None
        
        if screening and movie and hall:
            return {
                'movie': movie.title,
                'hall': hall.name,
                'time': screening.start_time.strftime('%Y-%m-%d %H:%M'),
                'price': screening.price,
                'available': len(screening.get_available_seats()),
                'total': hall.get_total_seats()
            }
        return None
    
    def get_stats(self):
        return {
            'movies': len(self.movies),
            'halls': len(self.halls),
            'screenings': len(self.screenings),
            'tickets_sold': sum(1 for t in self.tickets.values() if t.status == "valid")
        }

def main():
    cinema = CinemaSystem()
    
    m1 = cinema.add_movie("流浪地球", 125, "科幻", 8.5)
    m2 = cinema.add_movie("满江红", 159, "剧情", 7.8)
    
    h1 = cinema.add_hall("1号厅", 8, 10)
    h2 = cinema.add_hall("2号厅", 10, 12)
    
    today = date.today()
    s1 = cinema.add_screening(m1, h1, datetime(today.year, today.month, today.day, 14, 0), 45)
    s2 = cinema.add_screening(m1, h2, datetime(today.year, today.month, today.day, 18, 0), 50)
    
    tickets, _ = cinema.book_tickets(s1, ["3-5", "3-6"], "user001")
    
    print("影院统计:")
    stats = cinema.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n电影'{cinema.movies[m1].title}'场次:")
    for screening in cinema.get_screenings_by_movie(m1):
        info = cinema.get_screening_info(screening.id)
        print(f"  {info['hall']} - {info['time']} - 剩余{info['available']}座")


if __name__ == "__main__":
    main()
