# -----------------------------
# 题目：实现分布式追踪。
# -----------------------------

import time
import threading
import uuid
from collections import defaultdict

class Span:
    def __init__(self, name, trace_id=None, parent_id=None):
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = trace_id or str(uuid.uuid4())
        self.parent_id = parent_id
        self.name = name
        self.start_time = time.time()
        self.end_time = None
        self.tags = {}
        self.status = "ok"
    
    def finish(self):
        self.end_time = time.time()
    
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def set_tag(self, key, value):
        self.tags[key] = value
    
    def error(self, message):
        self.status = "error"
        self.tags["error"] = message

class Trace:
    def __init__(self, trace_id):
        self.trace_id = trace_id
        self.spans = []
    
    def add_span(self, span):
        self.spans.append(span)
    
    def duration(self):
        if not self.spans:
            return 0
        return max(s.end_time or time.time() for s in self.spans) - min(s.start_time for s in self.spans)

class DistributedTracer:
    def __init__(self):
        self.traces = {}
        self.lock = threading.Lock()
    
    def start_span(self, name, trace_id=None, parent_id=None):
        span = Span(name, trace_id, parent_id)
        return span
    
    def finish_span(self, span):
        span.finish()
        with self.lock:
            if span.trace_id not in self.traces:
                self.traces[span.trace_id] = Trace(span.trace_id)
            self.traces[span.trace_id].add_span(span)
    
    def get_trace(self, trace_id):
        return self.traces.get(trace_id)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

if __name__ == "__main__":
    tracer = DistributedTracer()
    
    parent = tracer.start_span("http_request")
    with tracer:
        child1 = tracer.start_span("db_query", parent.trace_id, parent.span_id)
        time.sleep(0.1)
        tracer.finish_span(child1)
        
        child2 = tracer.start_span("cache_lookup", parent.trace_id, parent.span_id)
        time.sleep(0.05)
        tracer.finish_span(child2)
    
    tracer.finish_span(parent)
    
    trace = tracer.get_trace(parent.trace_id)
    print(f"Trace ID: {trace.trace_id}")
    print(f"Total spans: {len(trace.spans)}")
    print(f"Duration: {trace.duration():.3f}s")
