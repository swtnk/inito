"""Public exception types raised by inito."""

from inito.exceptions.errors import (
    AmbiguousDependencyError,
    AnnotationResolutionError,
    BuilderValidationError,
    CircularDependencyError,
    CodeGenerationError,
    ConfigResolutionError,
    DecoratorConfigurationError,
    DependencyRegistrationError,
    DuplicateGeneratorError,
    InitoError,
    InvalidFieldDefinitionError,
    MetadataExtractionError,
    UnresolvableDependencyError,
)

__all__ = [
    "AmbiguousDependencyError",
    "AnnotationResolutionError",
    "BuilderValidationError",
    "CircularDependencyError",
    "CodeGenerationError",
    "ConfigResolutionError",
    "DecoratorConfigurationError",
    "DependencyRegistrationError",
    "DuplicateGeneratorError",
    "InitoError",
    "InvalidFieldDefinitionError",
    "MetadataExtractionError",
    "UnresolvableDependencyError",
]
