"""__eq__ cost: handwritten vs @Data vs dataclasses vs attrs."""


def test_equality(benchmark, point_class):
    left = point_class(1, 2, "here")
    right = point_class(1, 2, "here")
    benchmark.group = "equality"
    benchmark(lambda: left == right)
