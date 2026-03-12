# -----------------------------
# 题目：实现简单的音乐播放器。
# 描述：管理歌曲、播放列表、播放控制等。
# -----------------------------

from datetime import datetime

class Song:
    def __init__(self, song_id, title, artist, album, duration, file_path):
        self.id = song_id
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.file_path = file_path
        self.play_count = 0
        self.is_favorite = False
    
    def play(self):
        self.play_count += 1
    
    def get_duration_str(self):
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

class Playlist:
    def __init__(self, playlist_id, name, creator):
        self.id = playlist_id
        self.name = name
        self.creator = creator
        self.songs = []
        self.created_at = datetime.now()
    
    def add_song(self, song_id):
        if song_id not in self.songs:
            self.songs.append(song_id)
            return True
        return False
    
    def remove_song(self, song_id):
        if song_id in self.songs:
            self.songs.remove(song_id)
            return True
        return False
    
    def get_total_duration(self):
        return sum(s.duration for s in self.songs if isinstance(s, Song))

class Player:
    def __init__(self):
        self.current_song = None
        self.current_playlist = None
        self.current_index = 0
        self.is_playing = False
        self.volume = 80
        self.play_mode = "sequence"
        self.position = 0
    
    def play(self, song=None):
        if song:
            self.current_song = song
            self.position = 0
        self.is_playing = True
        if self.current_song:
            self.current_song.play()
    
    def pause(self):
        self.is_playing = False
    
    def stop(self):
        self.is_playing = False
        self.position = 0
    
    def next(self, playlist_songs):
        if self.current_playlist and playlist_songs:
            if self.play_mode == "random":
                import random
                self.current_index = random.randint(0, len(playlist_songs) - 1)
            else:
                self.current_index = (self.current_index + 1) % len(playlist_songs)
            return playlist_songs[self.current_index]
        return None
    
    def previous(self, playlist_songs):
        if self.current_playlist and playlist_songs:
            self.current_index = (self.current_index - 1) % len(playlist_songs)
            return playlist_songs[self.current_index]
        return None
    
    def set_volume(self, volume):
        self.volume = max(0, min(100, volume))
    
    def seek(self, position):
        if self.current_song:
            self.position = max(0, min(position, self.current_song.duration))

class MusicPlayer:
    def __init__(self):
        self.songs = {}
        self.playlists = {}
        self.player = Player()
        self.next_song_id = 1
        self.next_playlist_id = 1
    
    def add_song(self, title, artist, album, duration, file_path):
        song = Song(self.next_song_id, title, artist, album, duration, file_path)
        self.songs[self.next_song_id] = song
        self.next_song_id += 1
        return song.id
    
    def create_playlist(self, name, creator):
        playlist = Playlist(self.next_playlist_id, name, creator)
        self.playlists[self.next_playlist_id] = playlist
        self.next_playlist_id += 1
        return playlist.id
    
    def add_to_playlist(self, playlist_id, song_id):
        playlist = self.playlists.get(playlist_id)
        if playlist and song_id in self.songs:
            return playlist.add_song(song_id)
        return False
    
    def play_song(self, song_id):
        song = self.songs.get(song_id)
        if song:
            self.player.play(song)
            return True
        return False
    
    def play_playlist(self, playlist_id):
        playlist = self.playlists.get(playlist_id)
        if playlist and playlist.songs:
            self.player.current_playlist = playlist_id
            self.player.current_index = 0
            first_song_id = playlist.songs[0]
            return self.play_song(first_song_id)
        return False
    
    def pause(self):
        self.player.pause()
    
    def resume(self):
        self.player.play()
    
    def next(self):
        playlist = self.playlists.get(self.player.current_playlist)
        if playlist:
            songs = [self.songs[sid] for sid in playlist.songs if sid in self.songs]
            next_song = self.player.next(songs)
            if next_song:
                self.player.play(next_song)
                return next_song.id
        return None
    
    def previous(self):
        playlist = self.playlists.get(self.player.current_playlist)
        if playlist:
            songs = [self.songs[sid] for sid in playlist.songs if sid in self.songs]
            prev_song = self.player.previous(songs)
            if prev_song:
                self.player.play(prev_song)
                return prev_song.id
        return None
    
    def get_recently_played(self, limit=10):
        songs = sorted(self.songs.values(), key=lambda s: s.play_count, reverse=True)
        return songs[:limit]
    
    def search_songs(self, keyword):
        keyword = keyword.lower()
        return [s for s in self.songs.values() 
                if keyword in s.title.lower() or keyword in s.artist.lower()]
    
    def get_stats(self):
        return {
            'songs': len(self.songs),
            'playlists': len(self.playlists),
            'total_plays': sum(s.play_count for s in self.songs.values())
        }

def main():
    player = MusicPlayer()
    
    s1 = player.add_song("晴天", "周杰伦", "叶惠美", 269, "/music/qingtian.mp3")
    s2 = player.add_song("稻香", "周杰伦", "魔杰座", 223, "/music/daoxiang.mp3")
    s3 = player.add_song("七里香", "周杰伦", "七里香", 299, "/music/qilixiang.mp3")
    
    pl1 = player.create_playlist("周杰伦精选", "用户A")
    player.add_to_playlist(pl1, s1)
    player.add_to_playlist(pl1, s2)
    player.add_to_playlist(pl1, s3)
    
    player.play_playlist(pl1)
    player.next()
    player.next()
    
    print("音乐播放器统计:")
    stats = player.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    if player.player.current_song:
        print(f"\n当前播放: {player.player.current_song.title}")
        print(f"播放状态: {'播放中' if player.player.is_playing else '暂停'}")


if __name__ == "__main__":
    main()
