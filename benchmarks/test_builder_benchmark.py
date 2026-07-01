"""@Builder-specific cost: fluent chain vs a direct constructor call."""


def test_builder_fluent_chain(benchmark, builder_point_class):
    benchmark.group = "builder"
    benchmark(lambda: builder_point_class.builder().x(1).y(2).label("here").build())


def test_direct_construction_for_comparison(benchmark, builder_point_class):
    benchmark.group = "builder"
    benchmark(lambda: builder_point_class(1, 2, "here"))
