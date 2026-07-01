"""Object construction cost: handwritten vs @Data vs dataclasses vs attrs."""


def test_construction(benchmark, point_class):
    benchmark.group = "construction"
    benchmark(lambda: point_class(1, 2, "here"))
