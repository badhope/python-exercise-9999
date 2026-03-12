# -----------------------------
# 题目：实现简单的通知系统。
# 描述：管理消息通知、推送、订阅等。
# -----------------------------

from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    SYSTEM = "系统通知"
    MESSAGE = "消息通知"
    ALERT = "警告通知"
    PROMOTION = "促销通知"

class Notification:
    def __init__(self, notification_id, title, content, notification_type, sender_id):
        self.id = notification_id
        self.title = title
        self.content = content
        self.type = notification_type
        self.sender_id = sender_id
        self.recipients = []
        self.created_at = datetime.now()
        self.is_read = {}
    
    def mark_read(self, user_id):
        self.is_read[user_id] = True
    
    def is_read_by(self, user_id):
        return self.is_read.get(user_id, False)

class Subscription:
    def __init__(self, subscription_id, user_id, notification_type):
        self.id = subscription_id
        self.user_id = user_id
        self.notification_type = notification_type
        self.is_active = True
        self.created_at = datetime.now()

class NotificationSystem:
    def __init__(self):
        self.notifications = {}
        self.subscriptions = []
        self.user_notifications = {}
        self.next_notification_id = 1
        self.next_subscription_id = 1
    
    def subscribe(self, user_id, notification_type):
        for sub in self.subscriptions:
            if sub.user_id == user_id and sub.notification_type == notification_type:
                sub.is_active = True
                return sub.id
        
        subscription = Subscription(self.next_subscription_id, user_id, notification_type)
        self.subscriptions.append(subscription)
        self.next_subscription_id += 1
        return subscription.id
    
    def unsubscribe(self, user_id, notification_type):
        for sub in self.subscriptions:
            if sub.user_id == user_id and sub.notification_type == notification_type:
                sub.is_active = False
                return True
        return False
    
    def send_notification(self, title, content, notification_type, sender_id, recipient_ids=None):
        notification = Notification(self.next_notification_id, title, content, 
                                   notification_type, sender_id)
        
        if recipient_ids:
            notification.recipients = recipient_ids
        else:
            for sub in self.subscriptions:
                if sub.notification_type == notification_type and sub.is_active:
                    if sub.user_id not in notification.recipients:
                        notification.recipients.append(sub.user_id)
        
        self.notifications[self.next_notification_id] = notification
        
        for user_id in notification.recipients:
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            self.user_notifications[user_id].append(notification.id)
        
        self.next_notification_id += 1
        return notification.id
    
    def send_to_user(self, user_id, title, content, notification_type, sender_id):
        return self.send_notification(title, content, notification_type, sender_id, [user_id])
    
    def mark_as_read(self, user_id, notification_id):
        notification = self.notifications.get(notification_id)
        if notification and user_id in notification.recipients:
            notification.mark_read(user_id)
            return True
        return False
    
    def mark_all_read(self, user_id):
        notification_ids = self.user_notifications.get(user_id, [])
        for nid in notification_ids:
            notification = self.notifications.get(nid)
            if notification:
                notification.mark_read(user_id)
        return len(notification_ids)
    
    def get_user_notifications(self, user_id, unread_only=False):
        notification_ids = self.user_notifications.get(user_id, [])
        notifications = [self.notifications[nid] for nid in notification_ids if nid in self.notifications]
        
        if unread_only:
            notifications = [n for n in notifications if not n.is_read_by(user_id)]
        
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        return notifications
    
    def get_unread_count(self, user_id):
        notifications = self.get_user_notifications(user_id, unread_only=True)
        return len(notifications)
    
    def delete_notification(self, user_id, notification_id):
        if user_id in self.user_notifications:
            if notification_id in self.user_notifications[user_id]:
                self.user_notifications[user_id].remove(notification_id)
                return True
        return False
    
    def get_user_subscriptions(self, user_id):
        return [sub for sub in self.subscriptions if sub.user_id == user_id and sub.is_active]
    
    def get_stats(self):
        total = len(self.notifications)
        read = sum(sum(1 for r in n.recipients if n.is_read_by(r)) for n in self.notifications.values())
        total_recipients = sum(len(n.recipients) for n in self.notifications.values())
        
        return {
            'total_notifications': total,
            'total_sent': total_recipients,
            'total_read': read,
            'unread_rate': f"{(total_recipients - read) / total_recipients * 100:.1f}%" if total_recipients > 0 else "0%",
            'subscriptions': len([s for s in self.subscriptions if s.is_active])
        }

def main():
    system = NotificationSystem()
    
    u1 = 1
    u2 = 2
    u3 = 3
    
    system.subscribe(u1, NotificationType.SYSTEM)
    system.subscribe(u1, NotificationType.MESSAGE)
    system.subscribe(u2, NotificationType.SYSTEM)
    system.subscribe(u2, NotificationType.ALERT)
    system.subscribe(u3, NotificationType.PROMOTION)
    
    system.send_notification("系统维护通知", "系统将于今晚维护", 
                            NotificationType.SYSTEM, 0)
    system.send_to_user(u1, "新消息", "您有一条新消息", 
                       NotificationType.MESSAGE, u2)
    system.send_notification("限时促销", "全场5折优惠", 
                            NotificationType.PROMOTION, 0)
    
    system.mark_as_read(u1, 1)
    
    print("通知系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n用户{u1}的通知:")
    for notification in system.get_user_notifications(u1):
        status = "已读" if notification.is_read_by(u1) else "未读"
        print(f"  [{status}] {notification.title}: {notification.content}")


if __name__ == "__main__":
    main()
