"""Attribute-read cost: should be near-identical across flavors (plain instance
attributes in every case; inito never uses descriptors/proxies/__getattr__)."""


def test_attribute_access(benchmark, point_class):
    instance = point_class(1, 2, "here")
    benchmark.group = "attribute-access"
    benchmark(lambda: instance.x)
