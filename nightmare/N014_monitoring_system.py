# -----------------------------
# 题目：实现简单的分布式监控系统。
# 描述：支持指标收集、聚合、告警。
# -----------------------------

import time
import threading
from collections import defaultdict
from enum import Enum

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"

class Metric:
    def __init__(self, name, metric_type, labels=None):
        self.name = name
        self.metric_type = metric_type
        self.labels = labels or {}
        self.value = 0
        self.values = []
        self._lock = threading.Lock()
    
    def inc(self, amount=1):
        with self._lock:
            self.value += amount
    
    def dec(self, amount=1):
        with self._lock:
            self.value -= amount
    
    def set(self, value):
        with self._lock:
            self.value = value
    
    def observe(self, value):
        with self._lock:
            self.values.append(value)
    
    def get(self):
        with self._lock:
            if self.metric_type == MetricType.HISTOGRAM:
                if not self.values:
                    return {"count": 0, "sum": 0, "avg": 0}
                return {
                    "count": len(self.values),
                    "sum": sum(self.values),
                    "avg": sum(self.values) / len(self.values)
                }
            return self.value

class MetricRegistry:
    def __init__(self):
        self.metrics = {}
        self._lock = threading.Lock()
    
    def counter(self, name, labels=None):
        with self._lock:
            key = self._make_key(name, labels)
            if key not in self.metrics:
                self.metrics[key] = Metric(name, MetricType.COUNTER, labels)
            return self.metrics[key]
    
    def gauge(self, name, labels=None):
        with self._lock:
            key = self._make_key(name, labels)
            if key not in self.metrics:
                self.metrics[key] = Metric(name, MetricType.GAUGE, labels)
            return self.metrics[key]
    
    def histogram(self, name, labels=None):
        with self._lock:
            key = self._make_key(name, labels)
            if key not in self.metrics:
                self.metrics[key] = Metric(name, MetricType.HISTOGRAM, labels)
            return self.metrics[key]
    
    def _make_key(self, name, labels):
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name
    
    def get_all_metrics(self):
        with self._lock:
            return {k: v.get() for k, v in self.metrics.items()}

class AlertRule:
    def __init__(self, name, metric_name, condition, threshold, duration=60):
        self.name = name
        self.metric_name = metric_name
        self.condition = condition
        self.threshold = threshold
        self.duration = duration
        self.triggered_at = None
    
    def evaluate(self, value):
        if self.condition == "gt":
            return value > self.threshold
        elif self.condition == "lt":
            return value < self.threshold
        elif self.condition == "eq":
            return value == self.threshold
        return False

class AlertManager:
    def __init__(self):
        self.rules = []
        self.alerts = []
        self._lock = threading.Lock()
    
    def add_rule(self, rule):
        with self._lock:
            self.rules.append(rule)
    
    def check(self, metrics):
        with self._lock:
            for rule in self.rules:
                value = metrics.get(rule.metric_name)
                if value is not None:
                    if rule.evaluate(value):
                        if rule.triggered_at is None:
                            rule.triggered_at = time.time()
                        elif time.time() - rule.triggered_at >= rule.duration:
                            self.alerts.append({
                                "rule": rule.name,
                                "value": value,
                                "threshold": rule.threshold,
                                "time": time.time()
                            })
                    else:
                        rule.triggered_at = None
    
    def get_alerts(self):
        with self._lock:
            return self.alerts[:]

class MonitoringSystem:
    def __init__(self):
        self.registry = MetricRegistry()
        self.alert_manager = AlertManager()
    
    def collect(self, name, value, labels=None):
        metric = self.registry.gauge(name, labels)
        metric.set(value)
    
    def increment(self, name, labels=None):
        metric = self.registry.counter(name, labels)
        metric.inc()
    
    def observe(self, name, value, labels=None):
        metric = self.registry.histogram(name, labels)
        metric.observe(value)
    
    def add_alert_rule(self, name, metric_name, condition, threshold, duration=60):
        rule = AlertRule(name, metric_name, condition, threshold, duration)
        self.alert_manager.add_rule(rule)
    
    def check_alerts(self):
        metrics = self.registry.get_all_metrics()
        self.alert_manager.check(metrics)
        return self.alert_manager.get_alerts()

def main():
    monitor = MonitoringSystem()
    
    monitor.add_alert_rule("high_error_rate", "error_count", "gt", 10)
    
    for i in range(15):
        monitor.increment("request_count")
        if i % 3 == 0:
            monitor.increment("error_count")
    
    monitor.collect("cpu_usage", 75.5)
    monitor.observe("response_time", 0.1)
    monitor.observe("response_time", 0.2)
    monitor.observe("response_time", 0.15)
    
    print("指标数据:")
    for name, value in monitor.registry.get_all_metrics().items():
        print(f"  {name}: {value}")
    
    alerts = monitor.check_alerts()
    if alerts:
        print("\n告警:")
        for alert in alerts:
            print(f"  {alert['rule']}: {alert['value']} > {alert['threshold']}")


if __name__ == "__main__":
    main()
