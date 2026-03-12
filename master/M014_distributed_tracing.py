# -----------------------------
# 题目：实现简单的分布式追踪。
# 描述：支持请求追踪、调用链分析。
# -----------------------------

import time
import uuid
from collections import defaultdict

class Span:
    def __init__(self, trace_id, span_id, parent_id, name):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.name = name
        self.start_time = time.time()
        self.end_time = None
        self.tags = {}
        self.logs = []
    
    def finish(self):
        self.end_time = time.time()
    
    def set_tag(self, key, value):
        self.tags[key] = value
    
    def log(self, message):
        self.logs.append({'time': time.time(), 'message': message})
    
    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

class Tracer:
    def __init__(self, service_name):
        self.service_name = service_name
        self.spans = []
        self._current_span = None
    
    def start_span(self, name, parent=None):
        trace_id = parent.trace_id if parent else str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        parent_id = parent.span_id if parent else None
        
        span = Span(trace_id, span_id, parent_id, name)
        span.set_tag('service', self.service_name)
        self.spans.append(span)
        return span
    
    def trace(self, name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                span = self.start_span(name, self._current_span)
                old_span = self._current_span
                self._current_span = span
                try:
                    result = func(*args, **kwargs)
                    span.set_tag('status', 'success')
                    return result
                except Exception as e:
                    span.set_tag('status', 'error')
                    span.set_tag('error', str(e))
                    raise
                finally:
                    span.finish()
                    self._current_span = old_span
            return wrapper
        return decorator
    
    def get_trace(self, trace_id):
        return [s for s in self.spans if s.trace_id == trace_id]

class TraceCollector:
    def __init__(self):
        self.traces = defaultdict(list)
    
    def collect(self, span):
        self.traces[span.trace_id].append({
            'span_id': span.span_id,
            'parent_id': span.parent_id,
            'name': span.name,
            'duration': span.duration,
            'tags': span.tags
        })
    
    def get_trace_graph(self, trace_id):
        spans = self.traces.get(trace_id, [])
        graph = {}
        for span in spans:
            graph[span['span_id']] = span
        return graph

def main():
    tracer = Tracer('order-service')
    
    @tracer.trace('process_order')
    def process_order(order_id):
        validate_order(order_id)
        save_order(order_id)
        return f"订单 {order_id} 处理完成"
    
    @tracer.trace('validate_order')
    def validate_order(order_id):
        time.sleep(0.01)
        return True
    
    @tracer.trace('save_order')
    def save_order(order_id):
        time.sleep(0.02)
        return True
    
    result = process_order(123)
    print(result)
    
    for span in tracer.spans:
        print(f"{span.name}: {span.duration*1000:.2f}ms")


if __name__ == "__main__":
    main()
