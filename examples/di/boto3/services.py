"""Wire a boto3 S3 client as a singleton and inject a Storage service.

`Storage` declares its dependency as a field and lets inito write the
constructor (`@RequiredArgsConstructor`); `S3Client` keeps a hand-written
`__init__` because building the boto3 client is real work, not field-forwarding
boilerplate.

Run:  AWS_REGION=us-east-1 python -m examples.di.boto3.services
"""

from __future__ import annotations

import boto3

from inito import Config, Container, RequiredArgsConstructor, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="AWS_")
class AwsSettings:
    region: str = "us-east-1"


@Singleton(container=container)
class S3Client:
    def __init__(self, settings: AwsSettings) -> None:  # real work: build the client
        self.client = boto3.client("s3", region_name=settings.region)


@Service(container=container)
@RequiredArgsConstructor
class Storage:
    s3: S3Client

    def bucket_names(self) -> list[str]:
        return [bucket["Name"] for bucket in self.s3.client.list_buckets()["Buckets"]]


def main() -> None:
    print(container.get(Storage).bucket_names())


if __name__ == "__main__":
    main()
