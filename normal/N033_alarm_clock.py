# -----------------------------
# 题目：实现简单的闹钟。
# 描述：支持设置闹钟时间和提醒功能。
# -----------------------------

import time
import threading
from datetime import datetime, timedelta

class Alarm:
    def __init__(self, alarm_id, time_str, message="", repeat=False):
        self.alarm_id = alarm_id
        self.time_str = time_str
        self.message = message
        self.repeat = repeat
        self.active = True
        self.triggered = False
    
    def get_alarm_time(self):
        now = datetime.now()
        alarm_time = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {self.time_str}", "%Y-%m-%d %H:%M")
        if alarm_time < now:
            alarm_time += timedelta(days=1)
        return alarm_time

class AlarmClock:
    def __init__(self):
        self.alarms = []
        self.running = False
        self._thread = None
        self._callbacks = []
    
    def add_alarm(self, time_str, message="", repeat=False):
        alarm_id = len(self.alarms) + 1
        alarm = Alarm(alarm_id, time_str, message, repeat)
        self.alarms.append(alarm)
        return alarm_id
    
    def remove_alarm(self, alarm_id):
        self.alarms = [a for a in self.alarms if a.alarm_id != alarm_id]
    
    def toggle_alarm(self, alarm_id, active):
        for alarm in self.alarms:
            if alarm.alarm_id == alarm_id:
                alarm.active = active
                break
    
    def add_callback(self, callback):
        self._callbacks.append(callback)
    
    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._check_alarms, daemon=True)
            self._thread.start()
    
    def stop(self):
        self.running = False
    
    def _check_alarms(self):
        while self.running:
            now = datetime.now()
            for alarm in self.alarms:
                if alarm.active and not alarm.triggered:
                    alarm_time = alarm.get_alarm_time()
                    if now >= alarm_time:
                        self._trigger_alarm(alarm)
            time.sleep(1)
    
    def _trigger_alarm(self, alarm):
        alarm.triggered = True
        for callback in self._callbacks:
            callback(alarm)
        
        if alarm.repeat:
            alarm.triggered = False
    
    def get_next_alarm(self):
        active_alarms = [a for a in self.alarms if a.active and not a.triggered]
        if not active_alarms:
            return None
        return min(active_alarms, key=lambda a: a.get_alarm_time())
    
    def list_alarms(self):
        return [(a.alarm_id, a.time_str, a.message, a.active, a.repeat) for a in self.alarms]

def main():
    alarm_clock = AlarmClock()
    
    def on_alarm(alarm):
        print(f"\n闹钟响了! {alarm.message}")
    
    alarm_clock.add_callback(on_alarm)
    
    now = datetime.now()
    alarm_time = (now + timedelta(seconds=2)).strftime("%H:%M:%S")
    alarm_clock.add_alarm(alarm_time, "测试闹钟")
    
    print(f"闹钟已设置: {alarm_time}")
    print("等待闹钟...")
    
    alarm_clock.start()
    time.sleep(5)
    alarm_clock.stop()


if __name__ == "__main__":
    main()
