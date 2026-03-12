# -----------------------------
# 题目：实现简单的视频点播系统。
# 描述：管理视频、分类、播放记录、收藏等。
# -----------------------------

from datetime import datetime

class Video:
    def __init__(self, video_id, title, description, duration, category, url):
        self.id = video_id
        self.title = title
        self.description = description
        self.duration = duration
        self.category = category
        self.url = url
        self.views = 0
        self.likes = 0
        self.created_at = datetime.now()
    
    def get_duration_str(self):
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

class Category:
    def __init__(self, category_id, name):
        self.id = category_id
        self.name = name
        self.videos = []

class WatchHistory:
    def __init__(self, history_id, user_id, video_id, progress):
        self.id = history_id
        self.user_id = user_id
        self.video_id = video_id
        self.progress = progress
        self.watched_at = datetime.now()

class Favorite:
    def __init__(self, favorite_id, user_id, video_id):
        self.id = favorite_id
        self.user_id = user_id
        self.video_id = video_id
        self.created_at = datetime.now()

class VideoSystem:
    def __init__(self):
        self.videos = {}
        self.categories = {}
        self.watch_history = []
        self.favorites = []
        self.next_video_id = 1
        self.next_category_id = 1
        self.next_history_id = 1
        self.next_favorite_id = 1
    
    def add_category(self, name):
        category = Category(self.next_category_id, name)
        self.categories[self.next_category_id] = category
        self.next_category_id += 1
        return category.id
    
    def add_video(self, title, description, duration, category_id, url):
        video = Video(self.next_video_id, title, description, duration, category_id, url)
        self.videos[self.next_video_id] = video
        
        if category_id in self.categories:
            self.categories[category_id].videos.append(video.id)
        
        self.next_video_id += 1
        return video.id
    
    def watch_video(self, user_id, video_id, progress=0):
        video = self.videos.get(video_id)
        if video:
            video.views += 1
            
            history = WatchHistory(self.next_history_id, user_id, video_id, progress)
            self.watch_history.append(history)
            self.next_history_id += 1
            
            return {
                'title': video.title,
                'url': video.url,
                'duration': video.duration,
                'progress': progress
            }
        return None
    
    def add_favorite(self, user_id, video_id):
        video = self.videos.get(video_id)
        if video:
            for fav in self.favorites:
                if fav.user_id == user_id and fav.video_id == video_id:
                    return False
            
            favorite = Favorite(self.next_favorite_id, user_id, video_id)
            self.favorites.append(favorite)
            video.likes += 1
            self.next_favorite_id += 1
            return True
        return False
    
    def remove_favorite(self, user_id, video_id):
        for i, fav in enumerate(self.favorites):
            if fav.user_id == user_id and fav.video_id == video_id:
                self.favorites.pop(i)
                video = self.videos.get(video_id)
                if video:
                    video.likes -= 1
                return True
        return False
    
    def get_user_favorites(self, user_id):
        fav_video_ids = [f.video_id for f in self.favorites if f.user_id == user_id]
        return [self.videos[vid] for vid in fav_video_ids if vid in self.videos]
    
    def get_user_history(self, user_id, limit=20):
        history = [h for h in self.watch_history if h.user_id == user_id]
        history.sort(key=lambda x: x.watched_at, reverse=True)
        return history[:limit]
    
    def get_videos_by_category(self, category_id):
        return [self.videos[vid] for vid in self.categories.get(category_id, Category(0, "")).videos 
                if vid in self.videos]
    
    def get_hot_videos(self, limit=10):
        videos = list(self.videos.values())
        videos.sort(key=lambda x: x.views, reverse=True)
        return videos[:limit]
    
    def get_latest_videos(self, limit=10):
        videos = list(self.videos.values())
        videos.sort(key=lambda x: x.created_at, reverse=True)
        return videos[:limit]
    
    def search_videos(self, keyword):
        keyword = keyword.lower()
        return [v for v in self.videos.values() 
                if keyword in v.title.lower() or keyword in v.description.lower()]
    
    def get_stats(self):
        return {
            'videos': len(self.videos),
            'categories': len(self.categories),
            'total_views': sum(v.views for v in self.videos.values()),
            'total_favorites': len(self.favorites)
        }

def main():
    system = VideoSystem()
    
    cat1 = system.add_category("电影")
    cat2 = system.add_category("电视剧")
    cat3 = system.add_category("综艺")
    
    v1 = system.add_video("流浪地球", "科幻电影", 7200, cat1, "/videos/liulangdiqiu.mp4")
    v2 = system.add_video("三体", "科幻电视剧", 2700, cat2, "/videos/santi.mp4")
    v3 = system.add_video("快乐大本营", "综艺节目", 5400, cat3, "/videos/kuailedabenying.mp4")
    
    system.watch_video("user001", v1, 3600)
    system.watch_video("user001", v2, 1800)
    system.watch_video("user002", v1, 7200)
    
    system.add_favorite("user001", v1)
    system.add_favorite("user001", v2)
    
    print("视频系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n热门视频:")
    for video in system.get_hot_videos():
        print(f"  {video.title} - {video.views}次播放")


if __name__ == "__main__":
    main()
