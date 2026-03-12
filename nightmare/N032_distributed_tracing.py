# -----------------------------
# 题目：实现分布式追踪系统。
# 描述：支持链路追踪、Span管理、上下文传播。
# -----------------------------

import time
import threading
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class SpanKind(Enum):
    CLIENT = "CLIENT"
    SERVER = "SERVER"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"

@dataclass
class SpanContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    sampled: bool = True
    
    def to_headers(self) -> Dict[str, str]:
        return {
            'X-Trace-Id': self.trace_id,
            'X-Span-Id': self.span_id,
            'X-Parent-Span-Id': self.parent_span_id or '',
            'X-Sampled': '1' if self.sampled else '0'
        }
    
    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> 'SpanContext':
        return cls(
            trace_id=headers.get('X-Trace-Id', ''),
            span_id=headers.get('X-Span-Id', ''),
            parent_span_id=headers.get('X-Parent-Span-Id') or None,
            sampled=headers.get('X-Sampled', '1') == '1'
        )

@dataclass
class Span:
    context: SpanContext
    operation_name: str
    kind: SpanKind = SpanKind.SERVER
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "OK"
    
    def set_tag(self, key: str, value: Any):
        self.tags[key] = value
    
    def log(self, event: str, **kwargs):
        self.logs.append({
            'timestamp': time.time(),
            'event': event,
            **kwargs
        })
    
    def set_status(self, status: str):
        self.status = status
    
    def finish(self):
        self.end_time = time.time()
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

class Tracer:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._spans: List[Span] = []
        self._current_span: Dict[int, Span] = {}
        self._lock = threading.Lock()
    
    def _generate_id(self) -> str:
        return uuid.uuid4().hex[:16]
    
    def start_span(
        self,
        operation_name: str,
        kind: SpanKind = SpanKind.SERVER,
        parent_context: SpanContext = None
    ) -> Span:
        if parent_context:
            trace_id = parent_context.trace_id
            parent_span_id = parent_context.span_id
        else:
            current = self.get_current_span()
            if current:
                trace_id = current.context.trace_id
                parent_span_id = current.context.span_id
            else:
                trace_id = self._generate_id()
                parent_span_id = None
        
        span = Span(
            context=SpanContext(
                trace_id=trace_id,
                span_id=self._generate_id(),
                parent_span_id=parent_span_id
            ),
            operation_name=operation_name,
            kind=kind
        )
        
        span.set_tag('service', self.service_name)
        
        with self._lock:
            self._spans.append(span)
            self._current_span[threading.get_ident()] = span
        
        return span
    
    def finish_span(self, span: Span):
        span.finish()
        
        with self._lock:
            current = self._current_span.get(threading.get_ident())
            if current == span:
                self._current_span.pop(threading.get_ident(), None)
    
    def get_current_span(self) -> Optional[Span]:
        with self._lock:
            return self._current_span.get(threading.get_ident())
    
    def get_current_context(self) -> Optional[SpanContext]:
        span = self.get_current_span()
        return span.context if span else None
    
    def inject(self, headers: Dict[str, str]) -> Dict[str, str]:
        context = self.get_current_context()
        if context:
            headers.update(context.to_headers())
        return headers
    
    def extract(self, headers: Dict[str, str]) -> Optional[SpanContext]:
        if 'X-Trace-Id' in headers:
            return SpanContext.from_headers(headers)
        return None
    
    def get_spans(self) -> List[Span]:
        with self._lock:
            return list(self._spans)
    
    def get_trace(self, trace_id: str) -> List[Span]:
        with self._lock:
            return [
                span for span in self._spans
                if span.context.trace_id == trace_id
            ]

class TraceReporter:
    def __init__(self, tracer: Tracer):
        self.tracer = tracer
    
    def export_json(self) -> List[Dict[str, Any]]:
        spans = self.tracer.get_spans()
        return [
            {
                'trace_id': span.context.trace_id,
                'span_id': span.context.span_id,
                'parent_span_id': span.context.parent_span_id,
                'operation_name': span.operation_name,
                'kind': span.kind.value,
                'start_time': span.start_time,
                'end_time': span.end_time,
                'duration_ms': span.duration * 1000,
                'tags': span.tags,
                'logs': span.logs,
                'status': span.status
            }
            for span in spans
        ]
    
    def get_trace_tree(self, trace_id: str) -> Dict[str, Any]:
        spans = self.tracer.get_trace(trace_id)
        if not spans:
            return {}
        
        span_map = {s.context.span_id: s for s in spans}
        
        def build_tree(span: Span) -> Dict[str, Any]:
            children = [
                build_tree(s) for s in spans
                if s.context.parent_span_id == span.context.span_id
            ]
            
            return {
                'span_id': span.context.span_id,
                'operation_name': span.operation_name,
                'duration_ms': span.duration * 1000,
                'status': span.status,
                'children': children
            }
        
        root = next((s for s in spans if not s.context.parent_span_id), None)
        if root:
            return build_tree(root)
        return {}

def traced(tracer: Tracer, operation_name: str = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            span = tracer.start_span(op_name, SpanKind.SERVER)
            
            try:
                result = func(*args, **kwargs)
                span.set_status("OK")
                return result
            except Exception as e:
                span.set_status("ERROR")
                span.set_tag('error', True)
                span.set_tag('error.message', str(e))
                raise
            finally:
                tracer.finish_span(span)
        
        return wrapper
    return decorator

def main():
    tracer = Tracer("order-service")
    
    span1 = tracer.start_span("process_order", SpanKind.SERVER)
    span1.set_tag("order_id", "ORD-001")
    
    time.sleep(0.01)
    
    span2 = tracer.start_span("validate_order", SpanKind.SERVER)
    span2.set_tag("validation_result", "passed")
    time.sleep(0.005)
    tracer.finish_span(span2)
    
    span3 = tracer.start_span("save_order", SpanKind.CLIENT)
    span3.set_tag("db.operation", "INSERT")
    time.sleep(0.008)
    tracer.finish_span(span3)
    
    span1.log("order_processed", items=3)
    tracer.finish_span(span1)
    
    reporter = TraceReporter(tracer)
    
    print("追踪数据:")
    for span_data in reporter.export_json():
        print(f"  {span_data['operation_name']}: {span_data['duration_ms']:.2f}ms")
    
    trace_id = span1.context.trace_id
    print(f"\n追踪树 (trace_id: {trace_id}):")
    tree = reporter.get_trace_tree(trace_id)
    print(f"  {tree}")

if __name__ == "__main__":
    main()
