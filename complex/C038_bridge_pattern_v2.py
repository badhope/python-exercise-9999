# -----------------------------
# 题目：桥接模式实现多平台消息发送。
# -----------------------------

class MessageSender:
    def send(self, message):
        pass

class EmailSender(MessageSender):
    def __init__(self, smtp_server):
        self.smtp_server = smtp_server
    
    def send(self, message):
        return f"[Email] 通过 {self.smtp_server} 发送: {message}"

class SMSSender(MessageSender):
    def __init__(self, api_key):
        self.api_key = api_key
    
    def send(self, message):
        return f"[SMS] API密钥 {self.api_key[:8]}... 发送: {message}"

class PushSender(MessageSender):
    def __init__(self, app_id):
        self.app_id = app_id
    
    def send(self, message):
        return f"[Push] 应用 {self.app_id} 推送: {message}"

class WechatSender(MessageSender):
    def __init__(self, appid):
        self.appid = appid
    
    def send(self, message):
        return f"[微信] AppID {self.appid} 发送: {message}"

class Message:
    def __init__(self, sender):
        self.sender = sender
    
    def send(self, content):
        return self.sender.send(content)

class TextMessage(Message):
    def send_text(self, text):
        return self.send(text)

class HTMLMessage(Message):
    def send_html(self, html):
        formatted = f"<html><body>{html}</body></html>"
        return self.send(formatted)

class MarkdownMessage(Message):
    def send_markdown(self, md):
        return self.send(f"```markdown\n{md}\n```")

class AlertMessage(Message):
    def __init__(self, sender, level="info"):
        super().__init__(sender)
        self.level = level
    
    def send_alert(self, title, content):
        formatted = f"[{self.level.upper()}] {title}: {content}"
        return self.send(formatted)

class NotificationSystem:
    def __init__(self):
        self.senders = {}
        self.messages = []
    
    def register_sender(self, name, sender):
        self.senders[name] = sender
    
    def send_notification(self, sender_name, content, msg_type="text"):
        sender = self.senders.get(sender_name)
        if not sender:
            return f"未找到发送器: {sender_name}"
        
        if msg_type == "text":
            msg = TextMessage(sender)
            result = msg.send_text(content)
        elif msg_type == "html":
            msg = HTMLMessage(sender)
            result = msg.send_html(content)
        elif msg_type == "alert":
            msg = AlertMessage(sender, "warning")
            result = msg.send_alert("系统通知", content)
        else:
            msg = Message(sender)
            result = msg.send(content)
        
        self.messages.append(result)
        return result

def main():
    system = NotificationSystem()
    
    system.register_sender("email", EmailSender("smtp.example.com"))
    system.register_sender("sms", SMSSender("sk_1234567890abcdef"))
    system.register_sender("push", PushSender("com.example.app"))
    system.register_sender("wechat", WechatSender("wx1234567890"))
    
    print("=== 发送文本消息 ===")
    print(system.send_notification("email", "Hello World", "text"))
    print(system.send_notification("sms", "验证码: 123456", "text"))
    
    print("\n=== 发送HTML消息 ===")
    print(system.send_notification("email", "<h1>重要通知</h1>", "html"))
    
    print("\n=== 发送警报消息 ===")
    print(system.send_notification("push", "服务器负载过高", "alert"))
    print(system.send_notification("wechat", "系统维护通知", "alert"))
    
    print(f"\n总共发送消息: {len(system.messages)} 条")


if __name__ == "__main__":
    main()
