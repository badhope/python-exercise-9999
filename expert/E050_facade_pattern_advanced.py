# -----------------------------
# 题目：实现外观模式高级版。
# -----------------------------

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

class CPU:
    def freeze(self) -> str:
        return "CPU冻结"
    
    def jump(self, position: int) -> str:
        return f"CPU跳转到位置 {position}"
    
    def execute(self) -> str:
        return "CPU执行"

class Memory:
    def load(self, position: int, data: str) -> str:
        return f"内存加载 '{data}' 到位置 {position}"
    
    def read(self, position: int) -> str:
        return f"内存读取位置 {position}"

class HardDrive:
    def read(self, sector: int, size: int) -> str:
        return f"硬盘读取扇区 {sector}, 大小 {size}"
    
    def write(self, sector: int, data: str) -> str:
        return f"硬盘写入 '{data}' 到扇区 {sector}"

class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()
    
    def start(self) -> List[str]:
        results = []
        results.append(self.cpu.freeze())
        results.append(self.memory.load(0, "BOOT_SECTOR"))
        results.append(self.cpu.jump(0))
        results.append(self.cpu.execute())
        return results
    
    def shutdown(self) -> str:
        return "计算机关闭"

class DatabaseSystem:
    def __init__(self):
        self.connection = None
    
    def connect(self, host: str) -> str:
        self.connection = host
        return f"连接数据库: {host}"
    
    def query(self, sql: str) -> str:
        return f"执行查询: {sql}"
    
    def disconnect(self) -> str:
        self.connection = None
        return "断开数据库连接"

class CacheSystem:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> str:
        self._cache[key] = value
        return f"缓存设置: {key}"
    
    def clear(self) -> str:
        self._cache.clear()
        return "缓存已清空"

class Logger:
    def log(self, message: str) -> str:
        return f"[LOG] {message}"
    
    def error(self, message: str) -> str:
        return f"[ERROR] {message}"

class DataServiceFacade:
    def __init__(self):
        self.database = DatabaseSystem()
        self.cache = CacheSystem()
        self.logger = Logger()
    
    def get_data(self, key: str) -> Any:
        cached = self.cache.get(key)
        if cached:
            self.logger.log(f"缓存命中: {key}")
            return cached
        
        self.logger.log(f"缓存未命中: {key}")
        self.database.connect("localhost")
        result = self.database.query(f"SELECT * FROM data WHERE key='{key}'")
        self.database.disconnect()
        
        self.cache.set(key, result)
        return result
    
    def clear_cache(self) -> str:
        result = self.cache.clear()
        self.logger.log("缓存已清空")
        return result

class AudioSystem:
    def set_volume(self, level: int) -> str:
        return f"音量设置为 {level}"
    
    def play(self, file: str) -> str:
        return f"播放音频: {file}"
    
    def stop(self) -> str:
        return "停止播放"

class VideoSystem:
    def set_resolution(self, width: int, height: int) -> str:
        return f"分辨率设置为 {width}x{height}"
    
    def play(self, file: str) -> str:
        return f"播放视频: {file}"
    
    def stop(self) -> str:
        return "停止播放"

class DisplaySystem:
    def turn_on(self) -> str:
        return "显示器开启"
    
    def turn_off(self) -> str:
        return "显示器关闭"
    
    def set_brightness(self, level: int) -> str:
        return f"亮度设置为 {level}"

class MultimediaFacade:
    def __init__(self):
        self.audio = AudioSystem()
        self.video = VideoSystem()
        self.display = DisplaySystem()
    
    def watch_movie(self, file: str) -> List[str]:
        results = []
        results.append(self.display.turn_on())
        results.append(self.display.set_brightness(80))
        results.append(self.video.set_resolution(1920, 1080))
        results.append(self.audio.set_volume(50))
        results.append(self.video.play(file))
        results.append(self.audio.play(file))
        return results
    
    def stop_all(self) -> List[str]:
        results = []
        results.append(self.video.stop())
        results.append(self.audio.stop())
        results.append(self.display.turn_off())
        return results

class NotificationSystem:
    def __init__(self):
        self._subscribers: List[str] = []
    
    def subscribe(self, email: str) -> str:
        self._subscribers.append(email)
        return f"订阅: {email}"
    
    def send(self, message: str) -> str:
        return f"发送通知给 {len(self._subscribers)} 人: {message}"

class PaymentSystem:
    def process(self, amount: float) -> str:
        return f"处理支付: ${amount}"
    
    def refund(self, amount: float) -> str:
        return f"退款: ${amount}"

class InventorySystem:
    def __init__(self):
        self._items: Dict[str, int] = {}
    
    def add(self, item: str, quantity: int) -> str:
        self._items[item] = self._items.get(item, 0) + quantity
        return f"库存添加: {item} x {quantity}"
    
    def remove(self, item: str, quantity: int) -> str:
        if item in self._items:
            self._items[item] -= quantity
        return f"库存减少: {item} x {quantity}"
    
    def check(self, item: str) -> int:
        return self._items.get(item, 0)

class OrderFacade:
    def __init__(self):
        self.inventory = InventorySystem()
        self.payment = PaymentSystem()
        self.notification = NotificationSystem()
    
    def place_order(self, item: str, quantity: int, price: float, email: str) -> List[str]:
        results = []
        
        stock = self.inventory.check(item)
        if stock < quantity:
            results.append(f"库存不足: {item}")
            return results
        
        results.append(self.inventory.remove(item, quantity))
        results.append(self.payment.process(price * quantity))
        results.append(self.notification.subscribe(email))
        results.append(self.notification.send(f"订单确认: {item} x {quantity}"))
        
        return results

def main():
    print("=== 计算机外观 ===")
    computer = ComputerFacade()
    for step in computer.start():
        print(f"  {step}")
    
    print("\n=== 数据服务外观 ===")
    data_service = DataServiceFacade()
    print(f"  {data_service.get_data('user:1')}")
    print(f"  {data_service.get_data('user:1')}")
    
    print("\n=== 多媒体外观 ===")
    multimedia = MultimediaFacade()
    print("播放电影:")
    for step in multimedia.watch_movie("movie.mp4"):
        print(f"  {step}")
    
    print("\n=== 订单外观 ===")
    order = OrderFacade()
    order.inventory.add("iPhone", 10)
    
    print("下单:")
    for step in order.place_order("iPhone", 2, 999, "user@example.com"):
        print(f"  {step}")


if __name__ == "__main__":
    main()
