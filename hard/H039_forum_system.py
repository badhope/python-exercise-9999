# -----------------------------
# 题目：实现论坛系统。
# 描述：管理版块、帖子、回复、用户等。
# -----------------------------

from datetime import datetime

class ForumUser:
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email
        self.posts = []
        self.replies = []
        self.role = "member"
        self.created_at = datetime.now()

class Board:
    def __init__(self, board_id, name, description):
        self.id = board_id
        self.name = name
        self.description = description
        self.posts = []
        self.moderators = []

class Post:
    def __init__(self, post_id, title, content, author_id, board_id):
        self.id = post_id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.board_id = board_id
        self.replies = []
        self.views = 0
        self.is_pinned = False
        self.is_locked = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_reply_count(self):
        return len(self.replies)

class Reply:
    def __init__(self, reply_id, content, author_id, post_id):
        self.id = reply_id
        self.content = content
        self.author_id = author_id
        self.post_id = post_id
        self.created_at = datetime.now()

class ForumSystem:
    def __init__(self):
        self.users = {}
        self.boards = {}
        self.posts = {}
        self.replies = {}
        self.next_user_id = 1
        self.next_board_id = 1
        self.next_post_id = 1
        self.next_reply_id = 1
    
    def register_user(self, username, email):
        user = ForumUser(self.next_user_id, username, email)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user.id
    
    def create_board(self, name, description):
        board = Board(self.next_board_id, name, description)
        self.boards[self.next_board_id] = board
        self.next_board_id += 1
        return board.id
    
    def create_post(self, title, content, author_id, board_id):
        user = self.users.get(author_id)
        board = self.boards.get(board_id)
        
        if user and board:
            post = Post(self.next_post_id, title, content, author_id, board_id)
            self.posts[self.next_post_id] = post
            board.posts.append(post.id)
            user.posts.append(post.id)
            self.next_post_id += 1
            return post.id
        return None
    
    def create_reply(self, content, author_id, post_id):
        user = self.users.get(author_id)
        post = self.posts.get(post_id)
        
        if user and post and not post.is_locked:
            reply = Reply(self.next_reply_id, content, author_id, post_id)
            self.replies[self.next_reply_id] = reply
            post.replies.append(reply.id)
            user.replies.append(reply.id)
            self.next_reply_id += 1
            return reply.id
        return None
    
    def view_post(self, post_id):
        post = self.posts.get(post_id)
        if post:
            post.views += 1
            return {
                'title': post.title,
                'content': post.content,
                'author': self.users.get(post.author_id, ForumUser(0, "", "")).username,
                'views': post.views,
                'replies': len(post.replies),
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M')
            }
        return None
    
    def get_post_replies(self, post_id):
        post = self.posts.get(post_id)
        if post:
            return [
                {
                    'content': r.content,
                    'author': self.users.get(r.author_id, ForumUser(0, "", "")).username,
                    'time': r.created_at.strftime('%Y-%m-%d %H:%M')
                }
                for r in [self.replies[rid] for rid in post.replies if rid in self.replies]
            ]
        return []
    
    def pin_post(self, post_id):
        post = self.posts.get(post_id)
        if post:
            post.is_pinned = True
            return True
        return False
    
    def lock_post(self, post_id):
        post = self.posts.get(post_id)
        if post:
            post.is_locked = True
            return True
        return False
    
    def get_board_posts(self, board_id):
        board = self.boards.get(board_id)
        if board:
            posts = [self.posts[pid] for pid in board.posts if pid in self.posts]
            pinned = [p for p in posts if p.is_pinned]
            normal = [p for p in posts if not p.is_pinned]
            normal.sort(key=lambda x: x.updated_at, reverse=True)
            return pinned + normal
        return []
    
    def get_hot_posts(self, limit=10):
        posts = list(self.posts.values())
        posts.sort(key=lambda x: x.views + len(x.replies) * 5, reverse=True)
        return posts[:limit]
    
    def get_stats(self):
        return {
            'users': len(self.users),
            'boards': len(self.boards),
            'posts': len(self.posts),
            'replies': len(self.replies),
            'total_views': sum(p.views for p in self.posts.values())
        }

def main():
    forum = ForumSystem()
    
    u1 = forum.register_user("张三", "zhangsan@example.com")
    u2 = forum.register_user("李四", "lisi@example.com")
    
    b1 = forum.create_board("技术讨论", "讨论编程技术")
    b2 = forum.create_board("灌水区", "闲聊灌水")
    
    p1 = forum.create_post("Python学习心得", "分享一下Python学习经验...", u1, b1)
    p2 = forum.create_post("今天心情不错", "天气很好，心情也很好", u2, b2)
    
    forum.create_reply("写得很好，学习了！", u2, p1)
    forum.create_reply("谢谢分享！", u2, p1)
    
    forum.view_post(p1)
    forum.view_post(p1)
    
    print("论坛统计:")
    stats = forum.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n帖子'{forum.posts[p1].title}':")
    post_info = forum.view_post(p1)
    print(f"  浏览量: {post_info['views']}")
    print(f"  回复数: {len(forum.get_post_replies(p1))}")


if __name__ == "__main__":
    main()
