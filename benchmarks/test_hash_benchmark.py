"""__hash__ cost: handwritten vs @Data vs dataclasses vs attrs."""


def test_hash(benchmark, point_class):
    instance = point_class(1, 2, "here")
    benchmark.group = "hash"
    benchmark(lambda: hash(instance))
