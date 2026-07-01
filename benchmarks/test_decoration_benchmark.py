"""Decoration-time cost: defining + decorating a brand-new class each round."""


def test_decoration(benchmark, point_class_factory):
    benchmark.group = "decoration"
    benchmark(point_class_factory)
