# -----------------------------
# 题目：实现健康检查系统。
# 描述：支持服务健康检测、告警通知、状态报告。
# -----------------------------

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthCheckConfig:
    interval: float = 30.0
    timeout: float = 5.0
    failure_threshold: int = 3
    success_threshold: int = 2

class HealthChecker:
    def __init__(
        self,
        name: str,
        check_func: Callable[[], bool],
        config: HealthCheckConfig = None
    ):
        self.name = name
        self.check_func = check_func
        self.config = config or HealthCheckConfig()
        self.status = HealthStatus.UNKNOWN
        self.last_result: Optional[HealthCheckResult] = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self._lock = threading.Lock()
    
    def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            is_healthy = self.check_func()
            duration = time.time() - start_time
            
            with self._lock:
                if is_healthy:
                    self.consecutive_successes += 1
                    self.consecutive_failures = 0
                    
                    if self.consecutive_successes >= self.config.success_threshold:
                        self.status = HealthStatus.HEALTHY
                else:
                    self.consecutive_failures += 1
                    self.consecutive_successes = 0
                    
                    if self.consecutive_failures >= self.config.failure_threshold:
                        self.status = HealthStatus.UNHEALTHY
                
                result = HealthCheckResult(
                    name=self.name,
                    status=self.status,
                    message="健康检查通过" if is_healthy else "健康检查失败",
                    duration=duration
                )
                
                self.last_result = result
                return result
        
        except Exception as e:
            with self._lock:
                self.consecutive_failures += 1
                self.consecutive_successes = 0
                
                if self.consecutive_failures >= self.config.failure_threshold:
                    self.status = HealthStatus.UNHEALTHY
                
                result = HealthCheckResult(
                    name=self.name,
                    status=self.status,
                    message=f"健康检查异常: {str(e)}",
                    duration=time.time() - start_time
                )
                
                self.last_result = result
                return result

class AlertManager:
    def __init__(self):
        self._handlers: List[Callable[[str, HealthCheckResult], None]] = []
        self._alert_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def add_handler(self, handler: Callable[[str, HealthCheckResult], None]):
        self._handlers.append(handler)
    
    def send_alert(self, checker_name: str, result: HealthCheckResult):
        with self._lock:
            alert = {
                'checker': checker_name,
                'status': result.status.value,
                'message': result.message,
                'timestamp': result.timestamp
            }
            self._alert_history.append(alert)
        
        for handler in self._handlers:
            try:
                handler(checker_name, result)
            except Exception:
                pass
    
    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            return self._alert_history[-limit:]

class HealthCheckSystem:
    def __init__(self):
        self._checkers: Dict[str, HealthChecker] = {}
        self._alert_manager = AlertManager()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._last_alert_status: Dict[str, HealthStatus] = {}
    
    def register(
        self,
        name: str,
        check_func: Callable[[], bool],
        config: HealthCheckConfig = None
    ):
        checker = HealthChecker(name, check_func, config)
        self._checkers[name] = checker
    
    def add_alert_handler(self, handler: Callable[[str, HealthCheckResult], None]):
        self._alert_manager.add_handler(handler)
    
    def start(self):
        self._running = True
        self._worker_thread = threading.Thread(target=self._check_loop)
        self._worker_thread.daemon = True
        self._worker_thread.start()
    
    def stop(self):
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
    
    def _check_loop(self):
        while self._running:
            self._run_all_checks()
            
            min_interval = min(
                (c.config.interval for c in self._checkers.values()),
                default=30.0
            )
            time.sleep(min_interval)
    
    def _run_all_checks(self):
        for name, checker in self._checkers.items():
            result = checker.check()
            
            last_status = self._last_alert_status.get(name)
            if result.status != last_status:
                if result.status == HealthStatus.UNHEALTHY:
                    self._alert_manager.send_alert(name, result)
                self._last_alert_status[name] = result.status
    
    def check_now(self, name: str = None) -> Dict[str, HealthCheckResult]:
        if name:
            checker = self._checkers.get(name)
            if checker:
                return {name: checker.check()}
            return {}
        
        return {
            name: checker.check()
            for name, checker in self._checkers.items()
        }
    
    def get_status(self) -> Dict[str, Any]:
        overall_status = HealthStatus.HEALTHY
        
        for checker in self._checkers.values():
            if checker.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif checker.status == HealthStatus.DEGRADED:
                overall_status = HealthStatus.DEGRADED
        
        return {
            'overall_status': overall_status.value,
            'timestamp': time.time(),
            'checks': {
                name: {
                    'status': checker.status.value,
                    'last_check': checker.last_result.to_dict() if checker.last_result else None
                }
                for name, checker in self._checkers.items()
            }
        }
    
    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._alert_manager.get_alerts(limit)

def main():
    health_system = HealthCheckSystem()
    
    def check_database():
        return True
    
    def check_cache():
        import random
        return random.random() > 0.3
    
    def check_api():
        return True
    
    health_system.register("database", check_database, HealthCheckConfig(interval=10.0))
    health_system.register("cache", check_cache, HealthCheckConfig(interval=5.0))
    health_system.register("api", check_api, HealthCheckConfig(interval=15.0))
    
    def alert_handler(name: str, result: HealthCheckResult):
        print(f"[告警] {name}: {result.status.value} - {result.message}")
    
    health_system.add_alert_handler(alert_handler)
    
    health_system.start()
    
    print("运行健康检查...")
    time.sleep(3)
    
    status = health_system.get_status()
    print(f"\n系统状态: {status['overall_status']}")
    print("各组件状态:")
    for name, info in status['checks'].items():
        print(f"  {name}: {info['status']}")
    
    print(f"\n告警历史: {len(health_system.get_alerts())} 条")
    
    health_system.stop()

if __name__ == "__main__":
    main()
