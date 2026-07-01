"""Runnable example: @ToString paired with @Builder for a readable repr."""

from inito import ToString, builder


@builder
@ToString
class Point:
    x: int
    y: int


def main() -> None:
    point = Point.builder().x(1).y(2).build()
    print(point)


if __name__ == "__main__":
    main()
