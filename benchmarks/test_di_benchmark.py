"""DI-specific costs, each measured against a hand-written equivalent.

@Service/@Singleton never mutate the decorated class, and warm-cache
container.get()/post-construction attribute access are claimed to be
zero/negligible overhead - these benchmarks make that concrete. Cold
graph resolution and @Inject's per-call cost are NOT claimed to be
zero-overhead (see docs/quickstart.md's DI section); these benchmarks
quantify and track that cost instead of hiding it.
"""

from __future__ import annotations

from inito import Inject, Service, Singleton, default_container
from inito.di.container import Container, Scope


@Singleton
class WarmService:
    def __init__(self) -> None:
        self.x = 1


_handwritten_singleton = WarmService()


def _get_handwritten_singleton() -> WarmService:
    return _handwritten_singleton


def test_container_get_singleton_after_warm_cache(benchmark):
    default_container.get(WarmService)  # warm the cache once, outside the benchmark
    benchmark.group = "di-singleton-get"
    benchmark(lambda: default_container.get(WarmService))


def test_handwritten_singleton_get_baseline(benchmark):
    benchmark.group = "di-singleton-get"
    benchmark(_get_handwritten_singleton)


class HandwrittenPoint:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y


@Service
class ServicePoint:
    def __init__(self) -> None:
        self.x, self.y = 1, 2


def test_attribute_access_on_container_resolved_instance(benchmark):
    instance = default_container.get(ServicePoint)
    benchmark.group = "di-attribute-access"
    benchmark(lambda: instance.x)


def test_attribute_access_on_handwritten_instance_baseline(benchmark):
    instance = HandwrittenPoint(1, 2)
    benchmark.group = "di-attribute-access"
    benchmark(lambda: instance.x)


class GraphC:
    def __init__(self) -> None:
        pass


class GraphB:
    def __init__(self, c: GraphC) -> None:
        self.c = c


class GraphA:
    def __init__(self, b: GraphB) -> None:
        self.b = b


_graph_container = Container()
_graph_container.register(GraphC, scope=Scope.TRANSIENT)
_graph_container.register(GraphB, scope=Scope.TRANSIENT)
_graph_container.register(GraphA, scope=Scope.TRANSIENT)


def _handwritten_nested_construction() -> GraphA:
    return GraphA(GraphB(GraphC()))


def test_di_full_graph_resolution_cold(benchmark):
    benchmark.group = "di-cold-graph-resolution"
    benchmark(lambda: _graph_container.get(GraphA))


def test_handwritten_nested_construction_baseline(benchmark):
    benchmark.group = "di-cold-graph-resolution"
    benchmark(_handwritten_nested_construction)


@Service
class InjectService:
    def __init__(self) -> None:
        self.value = 42


@Inject
def _inject_handler(service: InjectService) -> int:
    return service.value


def _plain_handler(service: InjectService) -> int:
    return service.value


_inject_service_instance = InjectService()


def test_inject_call_overhead(benchmark):
    benchmark.group = "di-inject-call"
    benchmark(_inject_handler)


def test_plain_call_baseline(benchmark):
    benchmark.group = "di-inject-call"
    benchmark(lambda: _plain_handler(_inject_service_instance))
