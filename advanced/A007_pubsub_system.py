# -----------------------------
# 题目：实现简单的发布订阅系统。
# 描述：支持消息的发布和订阅。
# -----------------------------

class PubSub:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, topic, callback):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
    
    def unsubscribe(self, topic, callback):
        if topic in self.subscribers:
            self.subscribers[topic].remove(callback)
    
    def publish(self, topic, message):
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                callback(message)
    
    def get_topics(self):
        return list(self.subscribers.keys())
    
    def get_subscribers_count(self, topic):
        return len(self.subscribers.get(topic, []))

def main():
    pubsub = PubSub()
    
    def email_handler(message):
        print(f"[邮件] {message}")
    
    def sms_handler(message):
        print(f"[短信] {message}")
    
    pubsub.subscribe("notification", email_handler)
    pubsub.subscribe("notification", sms_handler)
    
    pubsub.publish("notification", "系统维护通知")
    print(f"订阅者数量: {pubsub.get_subscribers_count('notification')}")


if __name__ == "__main__":
    main()
