# -----------------------------
# 题目：实现内容管理系统。
# 描述：管理文章、分类、标签、评论等。
# -----------------------------

from datetime import datetime

class Category:
    def __init__(self, category_id, name, parent_id=None):
        self.id = category_id
        self.name = name
        self.parent_id = parent_id
        self.articles = []

class Tag:
    def __init__(self, tag_id, name):
        self.id = tag_id
        self.name = name
        self.article_count = 0

class Article:
    def __init__(self, article_id, title, content, author, category_id):
        self.id = article_id
        self.title = title
        self.content = content
        self.author = author
        self.category_id = category_id
        self.tags = []
        self.status = "draft"
        self.views = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.published_at = None
    
    def publish(self):
        self.status = "published"
        self.published_at = datetime.now()
    
    def get_summary(self, length=100):
        return self.content[:length] + "..." if len(self.content) > length else self.content

class Comment:
    def __init__(self, comment_id, article_id, user_name, content):
        self.id = comment_id
        self.article_id = article_id
        self.user_name = user_name
        self.content = content
        self.status = "pending"
        self.created_at = datetime.now()

class ContentSystem:
    def __init__(self):
        self.categories = {}
        self.tags = {}
        self.articles = {}
        self.comments = {}
        self.next_category_id = 1
        self.next_tag_id = 1
        self.next_article_id = 1
        self.next_comment_id = 1
    
    def add_category(self, name, parent_id=None):
        category = Category(self.next_category_id, name, parent_id)
        self.categories[self.next_category_id] = category
        self.next_category_id += 1
        return category.id
    
    def add_tag(self, name):
        tag = Tag(self.next_tag_id, name)
        self.tags[self.next_tag_id] = tag
        self.next_tag_id += 1
        return tag.id
    
    def create_article(self, title, content, author, category_id):
        article = Article(self.next_article_id, title, content, author, category_id)
        self.articles[self.next_article_id] = article
        
        if category_id in self.categories:
            self.categories[category_id].articles.append(article.id)
        
        self.next_article_id += 1
        return article.id
    
    def add_tag_to_article(self, article_id, tag_id):
        article = self.articles.get(article_id)
        tag = self.tags.get(tag_id)
        if article and tag:
            if tag_id not in article.tags:
                article.tags.append(tag_id)
                tag.article_count += 1
            return True
        return False
    
    def publish_article(self, article_id):
        article = self.articles.get(article_id)
        if article:
            article.publish()
            return True
        return False
    
    def add_comment(self, article_id, user_name, content):
        article = self.articles.get(article_id)
        if article:
            comment = Comment(self.next_comment_id, article_id, user_name, content)
            self.comments[self.next_comment_id] = comment
            self.next_comment_id += 1
            return comment.id
        return None
    
    def approve_comment(self, comment_id):
        comment = self.comments.get(comment_id)
        if comment:
            comment.status = "approved"
            return True
        return False
    
    def get_article_comments(self, article_id):
        return [c for c in self.comments.values() 
                if c.article_id == article_id and c.status == "approved"]
    
    def view_article(self, article_id):
        article = self.articles.get(article_id)
        if article:
            article.views += 1
            return {
                'title': article.title,
                'content': article.content,
                'author': article.author,
                'views': article.views,
                'tags': [self.tags[tid].name for tid in article.tags if tid in self.tags],
                'comments_count': len(self.get_article_comments(article_id))
            }
        return None
    
    def get_articles_by_category(self, category_id):
        return [a for a in self.articles.values() 
                if a.category_id == category_id and a.status == "published"]
    
    def get_articles_by_tag(self, tag_id):
        return [a for a in self.articles.values() 
                if tag_id in a.tags and a.status == "published"]
    
    def get_recent_articles(self, limit=10):
        articles = [a for a in self.articles.values() if a.status == "published"]
        articles.sort(key=lambda x: x.published_at, reverse=True)
        return articles[:limit]
    
    def get_popular_articles(self, limit=10):
        articles = [a for a in self.articles.values() if a.status == "published"]
        articles.sort(key=lambda x: x.views, reverse=True)
        return articles[:limit]
    
    def get_stats(self):
        return {
            'categories': len(self.categories),
            'tags': len(self.tags),
            'articles': len(self.articles),
            'published': sum(1 for a in self.articles.values() if a.status == "published"),
            'comments': len(self.comments),
            'total_views': sum(a.views for a in self.articles.values())
        }

def main():
    cms = ContentSystem()
    
    cat1 = cms.add_category("技术")
    cat2 = cms.add_category("生活")
    
    tag1 = cms.add_tag("Python")
    tag2 = cms.add_tag("教程")
    
    a1 = cms.create_article("Python入门教程", "Python是一门优秀的编程语言...", "张三", cat1)
    a2 = cms.create_article("我的生活记录", "今天天气很好...", "李四", cat2)
    
    cms.add_tag_to_article(a1, tag1)
    cms.add_tag_to_article(a1, tag2)
    
    cms.publish_article(a1)
    cms.publish_article(a2)
    
    cms.view_article(a1)
    cms.view_article(a1)
    
    cms.add_comment(a1, "王五", "写得很好！")
    
    print("内容系统统计:")
    stats = cms.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
