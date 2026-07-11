import pytest

pytest.importorskip("boto3")

from examples.di.boto3.services import S3Client, Storage, container


class _FakeS3:
    def list_buckets(self):
        return {"Buckets": [{"Name": "alpha"}, {"Name": "beta"}]}


class _FakeS3Client:
    def __init__(self) -> None:
        self.client = _FakeS3()


def test_storage_wiring_resolves():
    # The boto3 client is constructed without any network/credentials call.
    container.reset()
    assert isinstance(container.get(Storage), Storage)


def test_bucket_names_with_an_overridden_client():
    container.reset()
    container.override(S3Client, _FakeS3Client())
    assert container.get(Storage).bucket_names() == ["alpha", "beta"]
    container.clear_overrides()
