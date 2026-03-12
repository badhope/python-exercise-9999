# -----------------------------
# 题目：外观模式实现家庭影院系统。
# -----------------------------

class TV:
    def on(self):
        return "电视已开启"
    
    def off(self):
        return "电视已关闭"
    
    def set_channel(self, channel):
        return f"切换到频道 {channel}"

class AudioSystem:
    def on(self):
        return "音响已开启"
    
    def off(self):
        return "音响已关闭"
    
    def set_volume(self, level):
        return f"音量设为 {level}"

class DVDPlayer:
    def on(self):
        return "DVD播放器已开启"
    
    def off(self):
        return "DVD播放器已关闭"
    
    def play(self, movie):
        return f"播放电影: {movie}"

class Projector:
    def on(self):
        return "投影仪已开启"
    
    def off(self):
        return "投影仪已关闭"
    
    def set_mode(self, mode):
        return f"投影模式: {mode}"

class Lights:
    def dim(self, level):
        return f"灯光调暗到 {level}%"
    
    def on(self):
        return "灯光已开启"

class HomeTheaterFacade:
    def __init__(self):
        self.tv = TV()
        self.audio = AudioSystem()
        self.dvd = DVDPlayer()
        self.projector = Projector()
        self.lights = Lights()
    
    def watch_movie(self, movie):
        results = []
        results.append("=== 准备观影 ===")
        results.append(self.lights.dim(10))
        results.append(self.tv.on())
        results.append(self.audio.on())
        results.append(self.audio.set_volume(50))
        results.append(self.dvd.on())
        results.append(self.dvd.play(movie))
        return "\n".join(results)
    
    def watch_tv(self, channel):
        results = []
        results.append("=== 准备看电视 ===")
        results.append(self.lights.dim(30))
        results.append(self.tv.on())
        results.append(self.tv.set_channel(channel))
        results.append(self.audio.on())
        results.append(self.audio.set_volume(30))
        return "\n".join(results)
    
    def use_projector(self, movie):
        results = []
        results.append("=== 准备投影 ===")
        results.append(self.lights.dim(5))
        results.append(self.projector.on())
        results.append(self.projector.set_mode("影院模式"))
        results.append(self.audio.on())
        results.append(self.audio.set_volume(60))
        results.append(self.dvd.on())
        results.append(self.dvd.play(movie))
        return "\n".join(results)
    
    def end_session(self):
        results = []
        results.append("=== 结束观影 ===")
        results.append(self.dvd.off())
        results.append(self.audio.off())
        results.append(self.tv.off())
        results.append(self.projector.off())
        results.append(self.lights.on())
        return "\n".join(results)

def main():
    home_theater = HomeTheaterFacade()
    
    print(home_theater.watch_movie("阿凡达"))
    print("\n" + home_theater.end_session())
    
    print("\n" + home_theater.watch_tv("CCTV-5"))
    print("\n" + home_theater.end_session())
    
    print("\n" + home_theater.use_projector("星际穿越"))
    print("\n" + home_theater.end_session())


if __name__ == "__main__":
    main()
