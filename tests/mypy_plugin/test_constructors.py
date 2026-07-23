def test_no_args_constructor_accepts_no_arguments(check_mypy):
    status, out = check_mypy(
        """
        from inito import NoArgsConstructor

        @NoArgsConstructor
        class Config:
            debug: bool = False

        Config()
        Config(True)
        """
    )
    assert status == 1
    assert "Too many arguments" in out


def test_no_args_constructor_errors_on_field_without_default(check_mypy):
    status, out = check_mypy(
        """
        from inito import NoArgsConstructor

        @NoArgsConstructor
        class Config:
            debug: bool
        """
    )
    assert status == 1
    assert "requires every field to have a default" in out


def test_all_args_constructor_accepts_every_field(check_mypy):
    status, out = check_mypy(
        """
        from inito import AllArgsConstructor

        @AllArgsConstructor
        class Point:
            x: int
            y: str = "a"

        Point(1)
        Point(1, "b")
        Point()
        """
    )
    assert status == 1
    assert "Missing positional argument" in out


def test_required_args_constructor_excludes_defaulted_fields(check_mypy):
    status, out = check_mypy(
        """
        from inito import RequiredArgsConstructor

        @RequiredArgsConstructor
        class Point:
            x: int
            y: str = "a"

        Point(1)
        reveal_type(Point(1).y)
        Point()
        Point(1, "b")
        """
    )
    assert status == 1
    assert 'Revealed type is "str"' in out
    assert "Missing positional argument" in out
    assert "Too many arguments" in out


def test_all_args_constructor_rejects_required_after_optional(check_mypy):
    status, out = check_mypy(
        """
        from inito import AllArgsConstructor

        @AllArgsConstructor
        class Bad:
            a: int = 1
            b: int
        """
    )
    assert status == 1
    assert "cannot follow defaulted field" in out


def test_field_default_factory_makes_the_param_optional(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data, field

        @Data
        class Bag:
            items: list[int] = field(default_factory=list)

        Bag()
        Bag(items=[1])
        """
    )
    assert status == 0, out
