def test_init_and_getters_are_correctly_typed(check_mypy):
    status, out = check_mypy(
        """
        from inito import Value

        @Value
        class User:
            name: str
            age: int = 0

        user = User("Ada", 30)
        reveal_type(user.get_name())
        reveal_type(user.get_age())
        """
    )
    assert status == 0
    assert 'Revealed type is "str"' in out
    assert 'Revealed type is "int"' in out


def test_missing_required_argument_is_an_error(check_mypy):
    status, out = check_mypy(
        """
        from inito import Value

        @Value
        class User:
            name: str

        User()
        """
    )
    assert status == 1
    assert "Missing positional argument" in out


def test_setters_are_never_generated(check_mypy):
    status, out = check_mypy(
        """
        from inito import Value

        @Value
        class Point:
            x: int

        Point(1).set_x(2)
        """
    )
    assert status == 1
    assert "has no attribute" in out


def test_include_getters_false_omits_getters(check_mypy):
    status, out = check_mypy(
        """
        from inito import Value

        @Value(include_getters=False)
        class Point:
            x: int

        Point(1).get_x()
        """
    )
    assert status == 1
    assert "has no attribute" in out


def test_inheritance_includes_base_fields(check_mypy):
    status, out = check_mypy(
        """
        from inito import Value

        @Value
        class Base:
            a: int

        @Value
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
