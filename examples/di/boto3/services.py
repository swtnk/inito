"""Wire a boto3 S3 client as a singleton and inject a Storage service.

Run:  AWS_REGION=us-east-1 python -m examples.di.boto3.services
"""

from __future__ import annotations

import boto3

from inito import Config, Container, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="AWS_")
class AwsSettings:
    region: str = "us-east-1"


@Singleton(container=container)
class S3Client:
    def __init__(self, settings: AwsSettings) -> None:
        self.client = boto3.client("s3", region_name=settings.region)


@Service(container=container)
class Storage:
    def __init__(self, s3: S3Client) -> None:
        self._s3 = s3.client

    def bucket_names(self) -> list[str]:
        return [bucket["Name"] for bucket in self._s3.list_buckets()["Buckets"]]


def main() -> None:
    print(container.get(Storage).bucket_names())


if __name__ == "__main__":
    main()
