# -----------------------------
# 题目：实现简单的博客系统。
# 描述：管理用户、博客文章、评论、关注等。
# -----------------------------

from datetime import datetime

class BlogUser:
    def __init__(self, user_id, username, email, nickname):
        self.id = user_id
        self.username = username
        self.email = email
        self.nickname = nickname
        self.bio = ""
        self.posts = []
        self.followers = []
        self.following = []
        self.created_at = datetime.now()

class BlogPost:
    def __init__(self, post_id, author_id, title, content):
        self.id = post_id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.status = "draft"
        self.views = 0
        self.likes = []
        self.comments = []
        self.tags = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.published_at = None
    
    def publish(self):
        self.status = "published"
        self.published_at = datetime.now()
    
    def get_summary(self, length=200):
        return self.content[:length] + "..." if len(self.content) > length else self.content

class BlogComment:
    def __init__(self, comment_id, post_id, author_id, content):
        self.id = comment_id
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.created_at = datetime.now()

class BlogSystem:
    def __init__(self):
        self.users = {}
        self.posts = {}
        self.comments = {}
        self.next_user_id = 1
        self.next_post_id = 1
        self.next_comment_id = 1
    
    def register(self, username, email, nickname):
        user = BlogUser(self.next_user_id, username, email, nickname)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user.id
    
    def create_post(self, author_id, title, content):
        user = self.users.get(author_id)
        if user:
            post = BlogPost(self.next_post_id, author_id, title, content)
            self.posts[self.next_post_id] = post
            user.posts.append(post.id)
            self.next_post_id += 1
            return post.id
        return None
    
    def publish_post(self, post_id):
        post = self.posts.get(post_id)
        if post:
            post.publish()
            return True
        return False
    
    def update_post(self, post_id, title=None, content=None):
        post = self.posts.get(post_id)
        if post:
            if title:
                post.title = title
            if content:
                post.content = content
            post.updated_at = datetime.now()
            return True
        return False
    
    def delete_post(self, post_id):
        post = self.posts.get(post_id)
        if post:
            user = self.users.get(post.author_id)
            if user and post.id in user.posts:
                user.posts.remove(post.id)
            del self.posts[post_id]
            return True
        return False
    
    def add_comment(self, post_id, author_id, content):
        post = self.posts.get(post_id)
        user = self.users.get(author_id)
        if post and user and post.status == "published":
            comment = BlogComment(self.next_comment_id, post_id, author_id, content)
            self.comments[self.next_comment_id] = comment
            post.comments.append(comment.id)
            self.next_comment_id += 1
            return comment.id
        return None
    
    def like_post(self, post_id, user_id):
        post = self.posts.get(post_id)
        if post and user_id not in post.likes:
            post.likes.append(user_id)
            return True
        return False
    
    def follow_user(self, follower_id, following_id):
        follower = self.users.get(follower_id)
        following = self.users.get(following_id)
        if follower and following and follower_id != following_id:
            if following_id not in follower.following:
                follower.following.append(following_id)
                following.followers.append(follower_id)
                return True
        return False
    
    def get_user_posts(self, user_id):
        user = self.users.get(user_id)
        if user:
            return [self.posts[pid] for pid in user.posts if pid in self.posts]
        return []
    
    def get_feed(self, user_id):
        user = self.users.get(user_id)
        if user:
            feed_posts = []
            for following_id in user.following:
                following = self.users.get(following_id)
                if following:
                    for post_id in following.posts:
                        post = self.posts.get(post_id)
                        if post and post.status == "published":
                            feed_posts.append(post)
            feed_posts.sort(key=lambda x: x.published_at, reverse=True)
            return feed_posts
        return []
    
    def get_hot_posts(self, limit=10):
        posts = [p for p in self.posts.values() if p.status == "published"]
        posts.sort(key=lambda x: len(x.likes) + x.views, reverse=True)
        return posts[:limit]
    
    def search_posts(self, keyword):
        keyword = keyword.lower()
        return [p for p in self.posts.values() 
                if p.status == "published" and 
                (keyword in p.title.lower() or keyword in p.content.lower())]
    
    def get_stats(self):
        return {
            'users': len(self.users),
            'posts': len(self.posts),
            'published_posts': sum(1 for p in self.posts.values() if p.status == "published"),
            'comments': len(self.comments),
            'total_likes': sum(len(p.likes) for p in self.posts.values())
        }

def main():
    blog = BlogSystem()
    
    u1 = blog.register("zhangsan", "zhangsan@example.com", "张三")
    u2 = blog.register("lisi", "lisi@example.com", "李四")
    
    p1 = blog.create_post(u1, "我的第一篇博客", "这是我的第一篇博客文章...")
    p2 = blog.create_post(u1, "Python学习笔记", "Python是一门优秀的语言...")
    p3 = blog.create_post(u2, "技术分享", "今天分享一些技术心得...")
    
    blog.publish_post(p1)
    blog.publish_post(p2)
    blog.publish_post(p3)
    
    blog.follow_user(u1, u2)
    blog.add_comment(p3, u1, "写得很好！")
    blog.like_post(p1, u2)
    
    print("博客系统统计:")
    stats = blog.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n用户{u1}的文章:")
    for post in blog.get_user_posts(u1):
        print(f"  {post.title} - {post.views}次浏览")


if __name__ == "__main__":
    main()
