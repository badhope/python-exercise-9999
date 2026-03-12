# -----------------------------
# 题目：实现健康检查。
# -----------------------------

import time
import threading
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    def __init__(self, name, check_func, critical=False):
        self.name = name
        self.check_func = check_func
        self.critical = critical
        self.last_check = None
        self.last_status = None
    
    def check(self):
        try:
            result = self.check_func()
            self.last_status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
        except Exception as e:
            self.last_status = HealthStatus.UNHEALTHY
        
        self.last_check = time.time()
        return self.last_status

class HealthCheckRegistry:
    def __init__(self):
        self.checks = []
        self.lock = threading.Lock()
    
    def register(self, check):
        with self.lock:
            self.checks.append(check)
    
    def check_all(self):
        results = {"status": HealthStatus.HEALTHY, "checks": []}
        
        with self.lock:
            for check in self.checks:
                status = check.check()
                results["checks"].append({
                    "name": check.name,
                    "status": status.value,
                    "critical": check.critical
                })
                
                if check.critical and status == HealthStatus.UNHEALTHY:
                    results["status"] = HealthStatus.UNHEALTHY
                elif results["status"] != HealthStatus.UNHEALTHY and status == HealthStatus.DEGRADED:
                    results["status"] = HealthStatus.DEGRADED
        
        return results

def db_check():
    return True

def cache_check():
    return True

def external_api_check():
    return False

if __name__ == "__main__":
    registry = HealthCheckRegistry()
    
    registry.register(HealthCheck("database", db_check, critical=True))
    registry.register(HealthCheck("cache", cache_check))
    registry.register(HealthCheck("external_api", external_api_check))
    
    results = registry.check_all()
    print(f"Overall status: {results['status'].value}")
    for check in results['checks']:
        print(f"  {check['name']}: {check['status']}")
