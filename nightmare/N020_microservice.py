# -----------------------------
# 题目：实现简单的微服务框架。
# -----------------------------

import json
import time
from collections import defaultdict

class ServiceRegistry:
    def __init__(self):
        self.services = {}
    
    def register(self, name, host, port):
        self.services[name] = {
            "host": host,
            "port": port,
            "status": "healthy",
            "last_heartbeat": time.time()
        }
    
    def discover(self, name):
        return self.services.get(name)
    
    def get_all_services(self):
        return list(self.services.keys())

class LoadBalancer:
    def __init__(self, registry):
        self.registry = registry
        self.counters = defaultdict(int)
    
    def get_endpoint(self, service_name):
        service = self.registry.discover(service_name)
        if not service:
            return None
        return f"http://{service['host']}:{service['port']}"

class RPCClient:
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer
    
    def call(self, service_name, method, params):
        endpoint = self.load_balancer.get_endpoint(service_name)
        if not endpoint:
            return {"error": "Service not found"}
        return {
            "service": service_name,
            "method": method,
            "params": params,
            "endpoint": endpoint,
            "status": "success"
        }

def main():
    registry = ServiceRegistry()
    registry.register("user-service", "localhost", 8001)
    registry.register("order-service", "localhost", 8002)
    lb = LoadBalancer(registry)
    client = RPCClient(lb)
    print("可用服务:", registry.get_all_services())
    result = client.call("user-service", "getUser", {"id": 1})
    print(f"RPC调用: {result}")


if __name__ == "__main__":
    main()
