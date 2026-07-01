"""Runnable example: @NoArgsConstructor requires every field to have a default."""

from inito import NoArgsConstructor


@NoArgsConstructor
class Config:
    debug: bool = False
    retries: int = 3


def main() -> None:
    config = Config()
    print(config.debug, config.retries)


if __name__ == "__main__":
    main()
