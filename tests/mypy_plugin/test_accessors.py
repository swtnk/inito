def test_getter_synthesizes_only_getters(check_mypy):
    status, out = check_mypy(
        """
        from inito import Getter

        @Getter
        class Point:
            x: int
            y: int

        p = Point()
        reveal_type(p.get_x())
        p.set_x(1)
        """
    )
    assert status == 1
    assert 'Revealed type is "int"' in out
    assert "has no attribute" in out


def test_setter_synthesizes_only_setters(check_mypy):
    status, out = check_mypy(
        """
        from inito import Setter

        @Setter
        class Point:
            x: int

        p = Point()
        p.set_x(1)
        p.get_x()
        """
    )
    assert status == 1
    assert "has no attribute" in out


def test_setter_rejects_wrong_value_type(check_mypy):
    status, out = check_mypy(
        """
        from inito import Setter

        @Setter
        class Point:
            x: int

        Point().set_x("wrong")
        """
    )
    assert status == 1
    assert "incompatible type" in out
