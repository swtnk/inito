"""__repr__ cost: handwritten vs @Data vs dataclasses vs attrs."""


def test_repr(benchmark, point_class):
    instance = point_class(1, 2, "here")
    benchmark.group = "repr"
    benchmark(lambda: repr(instance))
