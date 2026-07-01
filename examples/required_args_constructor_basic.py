"""Runnable example: @RequiredArgsConstructor only requires fields without defaults."""

from inito import RequiredArgsConstructor


@RequiredArgsConstructor
class User:
    name: str
    age: int = 0


def main() -> None:
    user = User("Ada")
    print(user.name, user.age)


if __name__ == "__main__":
    main()
