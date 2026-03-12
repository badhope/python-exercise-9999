"""
N048 - 分布式链路追踪
难度：Nightmare

题目描述：
实现一个分布式链路追踪系统，支持请求链路的完整追踪、调用链分析、性能监控和错误定位。
系统需要处理Span的创建和传播、Trace的聚合分析、调用链可视化等核心功能。

学习目标：
1. 理解分布式链路追踪的核心概念（Trace、Span）
2. 掌握Span的创建、传播和关联机制
3. 实现调用链的聚合分析
4. 处理性能监控和错误定位

输入输出要求：
输入：追踪请求（操作名称、标签、日志）
输出：追踪结果（Trace树、性能指标、错误信息）

预期解决方案：
使用Span构建调用链，通过Trace ID关联分布式请求，实现链路追踪和性能分析。
"""

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SpanKind(Enum):
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class SpanStatus(Enum):
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    sampled: bool = True
    
    def to_headers(self) -> Dict[str, str]:
        return {
            "x-trace-id": self.trace_id,
            "x-span-id": self.span_id,
            "x-parent-span-id": self.parent_span_id or "",
            "x-sampled": "1" if self.sampled else "0"
        }
    
    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional["SpanContext"]:
        trace_id = headers.get("x-trace-id")
        span_id = headers.get("x-span-id")
        
        if not trace_id or not span_id:
            return None
        
        return cls(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=headers.get("x-parent-span-id") or None,
            sampled=headers.get("x-sampled", "1") == "1"
        )


@dataclass
class SpanEvent:
    name: str
    timestamp: float
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    trace_id: str
    span_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    context: SpanContext
    name: str
    kind: SpanKind
    start_time: float
    end_time: Optional[float] = None
    status: SpanStatus = SpanStatus.OK
    status_message: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)
    links: List[SpanLink] = field(default_factory=list)
    
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        self.events.append(SpanEvent(
            name=name,
            timestamp=time.time(),
            attributes=attributes or {}
        ))
    
    def add_link(self, trace_id: str, span_id: str, attributes: Dict[str, Any] = None):
        self.links.append(SpanLink(
            trace_id=trace_id,
            span_id=span_id,
            attributes=attributes or {}
        ))
    
    def set_status(self, status: SpanStatus, message: str = ""):
        self.status = status
        self.status_message = message
    
    def record_exception(self, exception: Exception):
        self.set_status(SpanStatus.ERROR, str(exception))
        self.add_event("exception", {
            "type": type(exception).__name__,
            "message": str(exception)
        })
    
    def end(self):
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
        self._active_spans: Dict[str, Span] = {}
        self._lock = threading.Lock()
    
    def _generate_id(self) -> str:
        return uuid.uuid4().hex[:16]
    
    def start_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL,
                   parent: Optional[SpanContext] = None,
                   attributes: Dict[str, Any] = None) -> Span:
        trace_id = parent.trace_id if parent else self._generate_id()
        span_id = self._generate_id()
        parent_span_id = parent.span_id if parent else None
        
        context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id
        )
        
        span = Span(
            context=context,
            name=name,
            kind=kind,
            start_time=time.time(),
            attributes=attributes or {}
        )
        
        span.set_attribute("service.name", self.service_name)
        
        with self._lock:
            self._active_spans[span_id] = span
        
        return span
    
    def end_span(self, span: Span):
        span.end()
        
        with self._lock:
            if span.context.span_id in self._active_spans:
                del self._active_spans[span.context.span_id]
            self._spans.append(span)
    
    def get_active_span(self) -> Optional[Span]:
        with self._lock:
            if self._active_spans:
                return list(self._active_spans.values())[-1]
        return None
    
    def get_trace(self, trace_id: str) -> List[Span]:
        with self._lock:
            return [s for s in self._spans if s.context.trace_id == trace_id]
    
    def get_all_spans(self) -> List[Span]:
        with self._lock:
            return list(self._spans)


class TraceCollector:
    def __init__(self):
        self._traces: Dict[str, List[Span]] = {}
        self._lock = threading.Lock()
    
    def collect(self, span: Span):
        with self._lock:
            trace_id = span.context.trace_id
            if trace_id not in self._traces:
                self._traces[trace_id] = []
            self._traces[trace_id].append(span)
    
    def get_trace(self, trace_id: str) -> List[Span]:
        with self._lock:
            return list(self._traces.get(trace_id, []))
    
    def get_all_traces(self) -> Dict[str, List[Span]]:
        with self._lock:
            return {k: list(v) for k, v in self._traces.items()}


class TraceAnalyzer:
    def __init__(self, collector: TraceCollector):
        self.collector = collector
    
    def analyze_trace(self, trace_id: str) -> Dict[str, Any]:
        spans = self.collector.get_trace(trace_id)
        
        if not spans:
            return {}
        
        total_duration = 0
        error_count = 0
        span_count = len(spans)
        
        for span in spans:
            total_duration = max(total_duration, span.duration)
            if span.status == SpanStatus.ERROR:
                error_count += 1
        
        span_tree = self._build_span_tree(spans)
        
        service_stats = {}
        for span in spans:
            service = span.attributes.get("service.name", "unknown")
            if service not in service_stats:
                service_stats[service] = {
                    "span_count": 0,
                    "total_duration": 0,
                    "error_count": 0
                }
            service_stats[service]["span_count"] += 1
            service_stats[service]["total_duration"] += span.duration
            if span.status == SpanStatus.ERROR:
                service_stats[service]["error_count"] += 1
        
        return {
            "trace_id": trace_id,
            "span_count": span_count,
            "total_duration": total_duration,
            "error_count": error_count,
            "has_error": error_count > 0,
            "span_tree": span_tree,
            "service_stats": service_stats
        }
    
    def _build_span_tree(self, spans: List[Span]) -> Dict[str, Any]:
        span_map = {s.context.span_id: s for s in spans}
        children_map: Dict[str, List[str]] = {}
        root_spans = []
        
        for span in spans:
            parent_id = span.context.parent_span_id
            if parent_id:
                if parent_id not in children_map:
                    children_map[parent_id] = []
                children_map[parent_id].append(span.context.span_id)
            else:
                root_spans.append(span.context.span_id)
        
        def build_node(span_id: str) -> Dict[str, Any]:
            span = span_map.get(span_id)
            if not span:
                return {}
            
            node = {
                "span_id": span.context.span_id,
                "name": span.name,
                "kind": span.kind.value,
                "duration": span.duration,
                "status": span.status.value,
                "attributes": span.attributes,
                "children": []
            }
            
            for child_id in children_map.get(span_id, []):
                node["children"].append(build_node(child_id))
            
            return node
        
        if len(root_spans) == 1:
            return build_node(root_spans[0])
        
        return {
            "span_id": "root",
            "name": "multiple_roots",
            "children": [build_node(rid) for rid in root_spans]
        }
    
    def get_slow_traces(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        slow_traces = []
        
        for trace_id, spans in self.collector.get_all_traces().items():
            analysis = self.analyze_trace(trace_id)
            if analysis.get("total_duration", 0) > threshold:
                slow_traces.append(analysis)
        
        return sorted(slow_traces, key=lambda x: x["total_duration"], reverse=True)
    
    def get_error_traces(self) -> List[Dict[str, Any]]:
        error_traces = []
        
        for trace_id in self.collector.get_all_traces():
            analysis = self.analyze_trace(trace_id)
            if analysis.get("has_error"):
                error_traces.append(analysis)
        
        return error_traces
    
    def get_service_dependencies(self) -> Dict[str, List[str]]:
        dependencies: Dict[str, set] = {}
        
        for trace_id in self.collector.get_all_traces():
            spans = self.collector.get_trace(trace_id)
            span_map = {s.context.span_id: s for s in spans}
            
            for span in spans:
                if span.context.parent_span_id:
                    parent = span_map.get(span.context.parent_span_id)
                    if parent:
                        from_service = parent.attributes.get("service.name", "unknown")
                        to_service = span.attributes.get("service.name", "unknown")
                        
                        if from_service not in dependencies:
                            dependencies[from_service] = set()
                        dependencies[from_service].add(to_service)
        
        return {k: list(v) for k, v in dependencies.items()}


class TracingContext:
    _current_span: Dict[int, Span] = {}
    
    @classmethod
    def get_current_span(cls) -> Optional[Span]:
        thread_id = threading.get_ident()
        return cls._current_span.get(thread_id)
    
    @classmethod
    def set_current_span(cls, span: Optional[Span]):
        thread_id = threading.get_ident()
        if span:
            cls._current_span[thread_id] = span
        elif thread_id in cls._current_span:
            del cls._current_span[thread_id]


def traced(name: str = None, kind: SpanKind = SpanKind.INTERNAL):
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = getattr(wrapper, "_tracer", None)
            if not tracer:
                return func(*args, **kwargs)
            
            span_name = name or func.__name__
            parent = TracingContext.get_current_span()
            parent_context = parent.context if parent else None
            
            span = tracer.start_span(span_name, kind, parent_context)
            TracingContext.set_current_span(span)
            
            try:
                result = func(*args, **kwargs)
                span.set_status(SpanStatus.OK)
                return result
            except Exception as e:
                span.record_exception(e)
                raise
            finally:
                tracer.end_span(span)
                TracingContext.set_current_span(parent)
        
        return wrapper
    return decorator


def main():
    collector = TraceCollector()
    
    api_tracer = Tracer("api-gateway")
    user_tracer = Tracer("user-service")
    order_tracer = Tracer("order-service")
    db_tracer = Tracer("database")
    
    print("=== 模拟分布式请求链路 ===")
    
    trace_id = uuid.uuid4().hex[:16]
    
    api_span = api_tracer.start_span(
        "HTTP GET /api/orders/123",
        SpanKind.SERVER,
        attributes={"http.method": "GET", "http.url": "/api/orders/123"}
    )
    api_span.set_attribute("http.status_code", 200)
    
    user_span = user_tracer.start_span(
        "get_user_info",
        SpanKind.SERVER,
        api_span.context,
        attributes={"user.id": "123"}
    )
    
    db_span1 = db_tracer.start_span(
        "SELECT users",
        SpanKind.CLIENT,
        user_span.context,
        attributes={"db.statement": "SELECT * FROM users WHERE id = ?"}
    )
    time.sleep(0.01)
    db_span1.end()
    db_tracer.end_span(db_span1)
    collector.collect(db_span1)
    
    user_span.add_event("cache_hit", {"key": "user:123"})
    time.sleep(0.02)
    user_span.end()
    user_tracer.end_span(user_span)
    collector.collect(user_span)
    
    order_span = order_tracer.start_span(
        "get_order",
        SpanKind.SERVER,
        api_span.context,
        attributes={"order.id": "456"}
    )
    
    db_span2 = db_tracer.start_span(
        "SELECT orders",
        SpanKind.CLIENT,
        order_span.context,
        attributes={"db.statement": "SELECT * FROM orders WHERE id = ?"}
    )
    time.sleep(0.015)
    db_span2.end()
    db_tracer.end_span(db_span2)
    collector.collect(db_span2)
    
    time.sleep(0.01)
    order_span.end()
    order_tracer.end_span(order_span)
    collector.collect(order_span)
    
    time.sleep(0.005)
    api_span.end()
    api_tracer.end_span(api_span)
    collector.collect(api_span)
    
    print("\n=== 链路分析 ===")
    analyzer = TraceAnalyzer(collector)
    analysis = analyzer.analyze_trace(api_span.context.trace_id)
    
    print(f"Trace ID: {analysis['trace_id']}")
    print(f"Span数量: {analysis['span_count']}")
    print(f"总耗时: {analysis['total_duration']*1000:.2f}ms")
    print(f"错误数: {analysis['error_count']}")
    
    print("\n=== 服务统计 ===")
    for service, stats in analysis["service_stats"].items():
        print(f"{service}:")
        print(f"  Span数: {stats['span_count']}")
        print(f"  总耗时: {stats['total_duration']*1000:.2f}ms")
    
    print("\n=== 调用链树 ===")
    def print_tree(node, indent=0):
        prefix = "  " * indent
        print(f"{prefix}└─ {node['name']} ({node['duration']*1000:.2f}ms)")
        for child in node.get("children", []):
            print_tree(child, indent + 1)
    
    print_tree(analysis["span_tree"])
    
    print("\n=== 模拟错误场景 ===")
    error_span = api_tracer.start_span(
        "HTTP POST /api/users",
        SpanKind.SERVER,
        attributes={"http.method": "POST"}
    )
    
    try:
        raise ValueError("用户名已存在")
    except Exception as e:
        error_span.record_exception(e)
    
    error_span.end()
    api_tracer.end_span(error_span)
    collector.collect(error_span)
    
    error_traces = analyzer.get_error_traces()
    print(f"发现 {len(error_traces)} 条错误链路")
    for trace in error_traces:
        print(f"  Trace {trace['trace_id']}: {trace['error_count']} 个错误")
    
    print("\n=== 服务依赖关系 ===")
    deps = analyzer.get_service_dependencies()
    for service, dependencies in deps.items():
        print(f"{service} -> {', '.join(dependencies)}")
    
    print("\n=== Span上下文传播 ===")
    headers = api_span.context.to_headers()
    print("传播Headers:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    restored_context = SpanContext.from_headers(headers)
    print(f"\n恢复的Trace ID: {restored_context.trace_id}")
    print(f"恢复的Span ID: {restored_context.span_id}")


if __name__ == "__main__":
    main()
