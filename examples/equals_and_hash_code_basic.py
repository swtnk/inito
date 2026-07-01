"""Runnable example: @EqualsAndHashCode on its own, without @Data's other capabilities."""

from inito import EqualsAndHashCode


@EqualsAndHashCode
class Point:
    x: int
    y: int


def main() -> None:
    a, b = Point(), Point()
    a.x, a.y = 1, 2
    b.x, b.y = 1, 2
    print(a == b, hash(a) == hash(b))


if __name__ == "__main__":
    main()
