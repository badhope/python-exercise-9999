# -----------------------------
# 题目：实现简单的分布式链路追踪。
# 描述：支持追踪采集、分析、可视化。
# -----------------------------

import time
import uuid
import threading
from collections import defaultdict

class Span:
    def __init__(self, trace_id, span_id, parent_span_id, operation_name):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.operation_name = operation_name
        self.start_time = time.time()
        self.end_time = None
        self.tags = {}
        self.logs = []
        self.status = "OK"
    
    def finish(self):
        self.end_time = time.time()
    
    def set_tag(self, key, value):
        self.tags[key] = value
    
    def log(self, event, **kwargs):
        self.logs.append({
            "timestamp": time.time(),
            "event": event,
            **kwargs
        })
    
    @property
    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None
    
    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration,
            "tags": self.tags,
            "status": self.status
        }

class Tracer:
    def __init__(self, service_name):
        self.service_name = service_name
        self._current_span = threading.local()
    
    def start_span(self, operation_name, parent=None):
        trace_id = parent.trace_id if parent else str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        parent_span_id = parent.span_id if parent else None
        
        span = Span(trace_id, span_id, parent_span_id, operation_name)
        span.set_tag("service", self.service_name)
        
        return span
    
    def trace(self, operation_name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                parent = getattr(self._current_span, 'span', None)
                span = self.start_span(operation_name, parent)
                self._current_span.span = span
                
                try:
                    result = func(*args, **kwargs)
                    span.status = "OK"
                    return result
                except Exception as e:
                    span.status = "ERROR"
                    span.set_tag("error", str(e))
                    raise
                finally:
                    span.finish()
                    self._current_span.span = parent
                    TraceCollector.collect(span)
            return wrapper
        return decorator

class TraceCollector:
    traces = defaultdict(list)
    _lock = threading.Lock()
    
    @classmethod
    def collect(cls, span):
        with cls._lock:
            cls.traces[span.trace_id].append(span)
    
    @classmethod
    def get_trace(cls, trace_id):
        with cls._lock:
            return [s.to_dict() for s in cls.traces.get(trace_id, [])]
    
    @classmethod
    def get_all_traces(cls):
        with cls._lock:
            return {tid: [s.to_dict() for s in spans] for tid, spans in cls.traces.items()}

class TraceAnalyzer:
    def __init__(self):
        self.collector = TraceCollector
    
    def get_trace_tree(self, trace_id):
        spans = self.collector.get_trace(trace_id)
        if not spans:
            return None
        
        span_map = {s['span_id']: s for s in spans}
        root = None
        
        for span in spans:
            parent_id = span['parent_span_id']
            if parent_id is None:
                root = span
            else:
                parent = span_map.get(parent_id)
                if parent:
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(span)
        
        return root
    
    def get_slow_spans(self, threshold_ms=100):
        slow = []
        for trace_id, spans in self.collector.get_all_traces().items():
            for span in spans:
                if span['duration_ms'] and span['duration_ms'] > threshold_ms:
                    slow.append(span)
        return sorted(slow, key=lambda x: x['duration_ms'], reverse=True)
    
    def get_error_traces(self):
        errors = []
        for trace_id, spans in self.collector.get_all_traces().items():
            for span in spans:
                if span['status'] == 'ERROR':
                    errors.append({'trace_id': trace_id, 'span': span})
        return errors

def main():
    tracer = Tracer("order-service")
    analyzer = TraceAnalyzer()
    
    @tracer.trace("process_order")
    def process_order(order_id):
        validate_order(order_id)
        save_order(order_id)
        send_notification(order_id)
        return f"订单 {order_id} 处理完成"
    
    @tracer.trace("validate_order")
    def validate_order(order_id):
        time.sleep(0.01)
        return True
    
    @tracer.trace("save_order")
    def save_order(order_id):
        time.sleep(0.02)
        return True
    
    @tracer.trace("send_notification")
    def send_notification(order_id):
        time.sleep(0.01)
        return True
    
    result = process_order(123)
    print(result)
    
    trace_id = list(TraceCollector.traces.keys())[0]
    tree = analyzer.get_trace_tree(trace_id)
    
    def print_tree(node, indent=0):
        if node:
            print("  " * indent + f"└─ {node['operation_name']} ({node['duration_ms']:.2f}ms)")
            for child in node.get('children', []):
                print_tree(child, indent + 1)
    
    print("\n追踪树:")
    print_tree(tree)


if __name__ == "__main__":
    main()
