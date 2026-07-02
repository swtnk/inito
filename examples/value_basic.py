"""Runnable example: @Value, a genuinely immutable data class with no setters."""

from dataclasses import FrozenInstanceError

from inito import Value


@Value
class Point:
    x: int
    y: int


def main() -> None:
    point = Point(1, 2)
    print(point)
    print(point.get_x(), point.get_y())
    print(point == Point(1, 2))
    print(not hasattr(point, "set_x"))

    try:
        point.x = 5  # no @dataclass(frozen=True) stacking needed - @Value enforces this itself
    except FrozenInstanceError as error:
        print(f"blocked: {error}")


if __name__ == "__main__":
    main()
