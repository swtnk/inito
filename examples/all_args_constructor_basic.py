"""Runnable example: @AllArgsConstructor generates a constructor only."""

from inito import AllArgsConstructor


@AllArgsConstructor
class Point:
    x: int
    y: int


def main() -> None:
    point = Point(1, 2)
    print(point.x, point.y)


if __name__ == "__main__":
    main()
