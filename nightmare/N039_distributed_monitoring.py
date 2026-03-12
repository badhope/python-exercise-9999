# -----------------------------
# 题目：实现分布式监控系统。
# 描述：支持指标收集、告警规则、可视化展示。
# -----------------------------

import time
import threading
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"

@dataclass
class Metric:
    name: str
    metric_type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'tags': self.tags
        }

@dataclass
class AlertRule:
    rule_id: str
    name: str
    metric_name: str
    condition: str
    threshold: float
    duration: float
    severity: str = "warning"
    enabled: bool = True

@dataclass
class Alert:
    alert_id: str
    rule_id: str
    rule_name: str
    metric_name: str
    value: float
    threshold: float
    severity: str
    timestamp: float
    status: str = "firing"

class MetricStore:
    def __init__(self, retention: int = 3600):
        self.retention = retention
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.Lock()
    
    def record(self, metric: Metric):
        with self._lock:
            key = self._make_key(metric.name, metric.tags)
            self.metrics[key].append(metric)
    
    def query(
        self,
        metric_name: str,
        tags: Dict[str, str] = None,
        start_time: float = None,
        end_time: float = None
    ) -> List[Metric]:
        with self._lock:
            key = self._make_key(metric_name, tags or {})
            
            if key in self.metrics:
                metrics = list(self.metrics[key])
                
                if start_time:
                    metrics = [m for m in metrics if m.timestamp >= start_time]
                if end_time:
                    metrics = [m for m in metrics if m.timestamp <= end_time]
                
                return metrics
            
            return []
    
    def get_latest(self, metric_name: str, tags: Dict[str, str] = None) -> Optional[Metric]:
        with self._lock:
            key = self._make_key(metric_name, tags or {})
            
            if key in self.metrics and self.metrics[key]:
                return self.metrics[key][-1]
            
            return None
    
    def _make_key(self, name: str, tags: Dict[str, str]) -> str:
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}:{tag_str}" if tag_str else name

class AlertEngine:
    def __init__(self, store: MetricStore):
        self.store = store
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self._alert_counter = 0
        self._lock = threading.Lock()
        self._handlers: List[Callable[[Alert], None]] = []
    
    def add_rule(self, rule: AlertRule):
        with self._lock:
            self.rules[rule.rule_id] = rule
    
    def add_handler(self, handler: Callable[[Alert], None]):
        self._handlers.append(handler)
    
    def evaluate(self):
        with self._lock:
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                
                metric = self.store.get_latest(rule.metric_name)
                if not metric:
                    continue
                
                is_firing = self._check_condition(metric.value, rule.condition, rule.threshold)
                
                if is_firing:
                    self._fire_alert(rule, metric)
    
    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        return False
    
    def _fire_alert(self, rule: AlertRule, metric: Metric):
        self._alert_counter += 1
        alert_id = f"alert-{int(time.time())}-{self._alert_counter}"
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            rule_name=rule.name,
            metric_name=rule.metric_name,
            value=metric.value,
            threshold=rule.threshold,
            severity=rule.severity,
            timestamp=time.time()
        )
        
        self.alerts.append(alert)
        
        for handler in self._handlers:
            try:
                handler(alert)
            except:
                pass

class MonitorAgent:
    def __init__(self, store: MetricStore):
        self.store = store
        self._collectors: List[Callable[[], List[Metric]]] = []
    
    def add_collector(self, collector: Callable[[], List[Metric]]):
        self._collectors.append(collector)
    
    def collect(self):
        for collector in self._collectors:
            try:
                metrics = collector()
                for metric in metrics:
                    self.store.record(metric)
            except:
                pass
    
    def record(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE, tags: Dict = None):
        metric = Metric(
            name=name,
            metric_type=metric_type,
            value=value,
            tags=tags or {}
        )
        self.store.record(metric)

class DistributedMonitor:
    def __init__(self):
        self.store = MetricStore()
        self.alert_engine = AlertEngine(self.store)
        self.agents: Dict[str, MonitorAgent] = {}
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def register_agent(self, agent_id: str) -> MonitorAgent:
        agent = MonitorAgent(self.store)
        self.agents[agent_id] = agent
        return agent
    
    def add_alert_rule(self, rule: AlertRule):
        self.alert_engine.add_rule(rule)
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        self.alert_engine.add_handler(handler)
    
    def start(self, interval: float = 5.0):
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def stop(self):
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
    
    def _monitor_loop(self, interval: float):
        while self._running:
            for agent in self.agents.values():
                agent.collect()
            
            self.alert_engine.evaluate()
            time.sleep(interval)
    
    def get_metric(self, name: str, tags: Dict = None) -> Optional[Metric]:
        return self.store.get_latest(name, tags)
    
    def query_metrics(
        self,
        name: str,
        tags: Dict = None,
        start_time: float = None,
        end_time: float = None
    ) -> List[Metric]:
        return self.store.query(name, tags, start_time, end_time)
    
    def get_alerts(self) -> List[Alert]:
        return self.alert_engine.alerts
    
    def get_dashboard(self) -> Dict[str, Any]:
        return {
            'metrics': {
                name: list(self.store.metrics[name])[-1].to_dict() if self.store.metrics[name] else None
                for name in list(self.store.metrics.keys())[:10]
            },
            'alerts': [
                {
                    'rule_name': a.rule_name,
                    'value': a.value,
                    'threshold': a.threshold,
                    'severity': a.severity
                }
                for a in self.alerts[-5:]
            ]
        }

def main():
    monitor = DistributedMonitor()
    
    agent = monitor.register_agent("server-1")
    
    def collect_system_metrics():
        return [
            Metric("cpu.usage", MetricType.GAUGE, random.uniform(20, 90)),
            Metric("memory.usage", MetricType.GAUGE, random.uniform(40, 80)),
            Metric("disk.usage", MetricType.GAUGE, random.uniform(30, 70))
        ]
    
    agent.add_collector(collect_system_metrics)
    
    monitor.add_alert_rule(AlertRule(
        rule_id="cpu-high",
        name="CPU使用率过高",
        metric_name="cpu.usage",
        condition=">",
        threshold=80,
        duration=60,
        severity="critical"
    ))
    
    def on_alert(alert: Alert):
        print(f"[告警] {alert.rule_name}: {alert.value:.1f} > {alert.threshold}")
    
    monitor.add_alert_handler(on_alert)
    
    monitor.start(interval=1.0)
    
    print("监控运行中...")
    time.sleep(5)
    
    print("\n指标数据:")
    for name in ["cpu.usage", "memory.usage", "disk.usage"]:
        metric = monitor.get_metric(name)
        if metric:
            print(f"  {name}: {metric.value:.1f}%")
    
    print("\n仪表盘:")
    dashboard = monitor.get_dashboard()
    print(f"  指标数: {len(dashboard['metrics'])}")
    print(f"  告警数: {len(dashboard['alerts'])}")
    
    monitor.stop()

if __name__ == "__main__":
    main()
