"""Runnable example: @Value, an immutable-style data class with no setters."""

from dataclasses import dataclass

from inito import Value


@Value
class Point:
    x: int
    y: int


@Value
@dataclass(frozen=True)
class FrozenPoint:
    x: int
    y: int


def main() -> None:
    point = Point(1, 2)
    print(point)
    print(point.get_x(), point.get_y())
    print(point == Point(1, 2))
    print(not hasattr(point, "set_x"))

    frozen_point = FrozenPoint(1, 2)
    print(frozen_point)


if __name__ == "__main__":
    main()
