def test_init_and_accessors_are_correctly_typed(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data

        @Data
        class User:
            name: str
            age: int = 0

        user = User("Ada", 30)
        reveal_type(user.get_name())
        reveal_type(user.get_age())
        user.set_age(31)
        """
    )
    assert status == 0
    assert 'Revealed type is "str"' in out
    assert 'Revealed type is "int"' in out


def test_missing_required_argument_is_an_error(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data

        @Data
        class User:
            name: str

        User()
        """
    )
    assert status == 1
    assert "Missing positional argument" in out


def test_unknown_attribute_is_an_error(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data

        @Data
        class User:
            name: str

        User("Ada").get_missing()
        """
    )
    assert status == 1
    assert "has no attribute" in out


def test_frozen_true_omits_setters_but_keeps_getters(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data

        @Data(frozen=True)
        class Point:
            x: int

        p = Point(1)
        reveal_type(p.get_x())
        p.set_x(2)
        """
    )
    assert status == 1
    assert 'Revealed type is "int"' in out
    assert "has no attribute" in out


def test_include_getters_false_omits_getters(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data

        @Data(include_getters=False)
        class Point:
            x: int

        Point(1).get_x()
        """
    )
    assert status == 1
    assert "has no attribute" in out


def test_class_var_fields_are_excluded(check_mypy):
    status, out = check_mypy(
        """
        from typing import ClassVar
        from inito import Data

        @Data
        class Sample:
            counter: ClassVar[int] = 0
            a: int

        Sample(1).get_a()
        Sample(1).get_counter()
        """
    )
    assert status == 1
    assert "has no attribute" in out


def test_tuple_assignment_in_class_body_is_ignored(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data

        @Data
        class Sample:
            a: int
            x, y = 1, 2

        reveal_type(Sample(1).get_a())
        """
    )
    assert status == 0
    assert 'Revealed type is "int"' in out


def test_inheritance_includes_base_fields(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data

        @Data
        class Base:
            a: int

        @Data
        class Sub(Base):
            b: str

        s = Sub(1, "x")
        reveal_type(s.get_a())
        reveal_type(s.get_b())
        Sub(1)
        """
    )
    assert 'Revealed type is "int"' in out
    assert 'Revealed type is "str"' in out
    assert "Missing positional argument" in out
    assert status == 1
