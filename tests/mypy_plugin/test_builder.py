def test_fluent_chain_returns_owner_type_from_build(check_mypy):
    status, out = check_mypy(
        """
        from inito import builder

        @builder
        class Point:
            x: int
            y: int

        p = Point.builder().x(1).y(2).build()
        reveal_type(p)
        """
    )
    assert status == 0
    assert 'Revealed type is "snippet.Point"' in out


def test_fluent_setter_rejects_wrong_value_type(check_mypy):
    status, out = check_mypy(
        """
        from inito import builder

        @builder
        class Point:
            x: int

        Point.builder().x("wrong")
        """
    )
    assert status == 1
    assert "incompatible type" in out


def test_to_builder_absent_without_option(check_mypy):
    status, out = check_mypy(
        """
        from inito import builder

        @builder
        class Point:
            x: int

        Point().to_builder()
        """
    )
    assert status == 1
    assert "has no attribute" in out


def test_to_builder_present_and_correctly_typed_with_option(check_mypy):
    status, out = check_mypy(
        """
        from inito import builder
        from dataclasses import dataclass

        @builder(to_builder=True)
        @dataclass
        class Point:
            x: int
            y: int

        original = Point(1, 2)
        revised = original.to_builder().y(9).build()
        reveal_type(revised)
        """
    )
    assert status == 0
    assert 'Revealed type is "snippet.Point"' in out


def test_setter_prefix_and_build_method_name_options(check_mypy):
    status, out = check_mypy(
        """
        from inito import builder

        @builder(setter_prefix="with_", build_method_name="create")
        class Point:
            x: int

        p = Point.builder().with_x(1).create()
        reveal_type(p)
        Point.builder().x(1)
        """
    )
    assert 'Revealed type is "snippet.Point"' in out
    assert "has no attribute" in out
    assert status == 1


def test_builder_composes_with_data(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data, builder

        @builder
        @Data
        class User:
            name: str
            age: int = 0

        user = User.builder().name("Ada").age(30).build()
        reveal_type(user.get_name())
        """
    )
    assert status == 0
    assert 'Revealed type is "str"' in out
