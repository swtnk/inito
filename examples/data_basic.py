"""Runnable example: @Data on a plain class and on a stacked @dataclass."""

from dataclasses import dataclass

from inito import Data


@Data
class User:
    name: str
    age: int = 0


@Data(frozen=True)
@dataclass
class Point:
    x: int
    y: int


def main() -> None:
    user = User("Ada", age=30)
    print(user)
    print(user.get_name(), user.get_age())
    user.set_age(31)
    print(user)
    print(User("Ada", 31) == user)

    origin = Point(0, 0)
    print(origin)
    print(hash(origin) == hash(Point(0, 0)))


if __name__ == "__main__":
    main()
