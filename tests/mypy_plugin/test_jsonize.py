"""The mypy plugin synthesizes @Jsonize's to_dict()/to_json()."""


def test_jsonize_synthesizes_to_dict_and_to_json(check_mypy):
    status, out = check_mypy(
        """
        from inito import Data, Jsonize

        @Jsonize
        @Data
        class Doc:
            title: str

        doc = Doc(title="x")
        reveal_type(doc.to_dict())
        reveal_type(doc.to_json())
        """
    )
    assert status == 0  # no type errors
    assert "str, Any]" in out  # to_dict() -> dict[str, Any]
    assert 'Revealed type is "str"' in out  # to_json() -> str
