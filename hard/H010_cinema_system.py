# -----------------------------
# 题目：电影院售票系统。
# 描述：实现电影排片、座位管理、售票功能。
# -----------------------------

class Movie:
    def __init__(self, movie_id, title, duration):
        self.movie_id = movie_id
        self.title = title
        self.duration = duration

class Screening:
    def __init__(self, screening_id, movie, start_time, hall):
        self.screening_id = screening_id
        self.movie = movie
        self.start_time = start_time
        self.hall = hall
        self.seats = [[False] * 10 for _ in range(8)]
    
    def book_seat(self, row, col):
        if not self.seats[row][col]:
            self.seats[row][col] = True
            return True
        return False
    
    def get_available_seats(self):
        count = 0
        for row in self.seats:
            count += row.count(False)
        return count

class CinemaSystem:
    def __init__(self):
        self.movies = {}
        self.screenings = {}
    
    def add_movie(self, movie_id, title, duration):
        self.movies[movie_id] = Movie(movie_id, title, duration)
    
    def add_screening(self, screening_id, movie_id, start_time, hall):
        if movie_id in self.movies:
            self.screenings[screening_id] = Screening(screening_id, self.movies[movie_id], start_time, hall)
    
    def book_ticket(self, screening_id, row, col):
        if screening_id in self.screenings:
            return self.screenings[screening_id].book_seat(row, col)
        return False

def main():
    cinema = CinemaSystem()
    cinema.add_movie("M001", "流浪地球", 120)
    cinema.add_screening("S001", "M001", "14:00", "1号厅")
    cinema.book_ticket("S001", 0, 0)
    screening = cinema.screenings["S001"]
    print(f"{screening.movie.title} {screening.start_time} 剩余座位: {screening.get_available_seats()}")


if __name__ == "__main__":
    main()
