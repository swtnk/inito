"""Runnable example: @Setter on its own, without @Data's other capabilities."""

from inito import Setter


@Setter
class User:
    name: str
    age: int = 0


def main() -> None:
    user = User()
    user.set_name("Ada")
    user.set_age(30)
    print(user.name, user.age)


if __name__ == "__main__":
    main()
