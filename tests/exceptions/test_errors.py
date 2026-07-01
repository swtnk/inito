import pytest

from inito.exceptions import (
    AnnotationResolutionError,
    BuilderValidationError,
    CodeGenerationError,
    DecoratorConfigurationError,
    DuplicateGeneratorError,
    InitoError,
    InvalidFieldDefinitionError,
    MetadataExtractionError,
)


@pytest.mark.parametrize(
    "exception_type",
    [
        MetadataExtractionError,
        AnnotationResolutionError,
        InvalidFieldDefinitionError,
        CodeGenerationError,
        DecoratorConfigurationError,
        DuplicateGeneratorError,
        BuilderValidationError,
    ],
)
def test_every_error_type_is_an_inito_error(exception_type: type) -> None:
    assert issubclass(exception_type, InitoError)


def test_annotation_resolution_error_is_a_metadata_extraction_error():
    assert issubclass(AnnotationResolutionError, MetadataExtractionError)


def test_invalid_field_definition_error_is_a_metadata_extraction_error():
    assert issubclass(InvalidFieldDefinitionError, MetadataExtractionError)


def test_error_message_is_preserved():
    error = InitoError("boom")
    assert str(error) == "boom"
