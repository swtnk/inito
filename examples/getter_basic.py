"""Runnable example: @Getter on its own, without @Data's other capabilities."""

from inito import Getter


@Getter
class User:
    name: str
    age: int = 0


def main() -> None:
    user = User()
    user.name = "Ada"
    user.age = 30
    print(user.get_name(), user.get_age())


if __name__ == "__main__":
    main()
