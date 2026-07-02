"""Runnable example: @Service/@Singleton/@Inject and Container-based dependency injection."""

from inito import Inject, Service, Singleton, default_container


@Singleton
class Repo:
    def __init__(self) -> None:
        self.ages = {"Ada": 30}


@Service
class UserService:
    def __init__(self, repo: Repo, retries: int = 3) -> None:
        self.repo = repo
        self.retries = retries

    def age_of(self, name: str) -> int:
        return self.repo.ages[name]


@Inject
def main(service: UserService) -> None:
    print(service.age_of("Ada"))
    print(service.retries)
    print(default_container.get(UserService) is service)

    # @Service never mutates the class - it's still an ordinary, directly
    # constructible Python class, with no DI-specific overhead.
    plain = UserService(Repo(), retries=5)
    print(plain.retries)


if __name__ == "__main__":
    main()
