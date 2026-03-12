# -----------------------------
# 题目：简易记分牌。
# 描述：实现比赛记分功能。
# -----------------------------

class Scoreboard:
    def __init__(self, team1, team2):
        self.teams = {team1: 0, team2: 0}
    
    def add_score(self, team, points=1):
        if team in self.teams:
            self.teams[team] += points
    
    def get_score(self):
        return self.teams.copy()
    
    def get_winner(self):
        scores = list(self.teams.items())
        if scores[0][1] > scores[1][1]:
            return scores[0][0]
        elif scores[0][1] < scores[1][1]:
            return scores[1][0]
        return "平局"
    
    def reset(self):
        for team in self.teams:
            self.teams[team] = 0

def main():
    board = Scoreboard("红队", "蓝队")
    board.add_score("红队", 2)
    board.add_score("蓝队", 1)
    print(f"比分: {board.get_score()}")
    print(f"领先: {board.get_winner()}")


if __name__ == "__main__":
    main()
