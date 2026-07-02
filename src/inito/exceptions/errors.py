"""Exception hierarchy for all inito errors."""

from __future__ import annotations


class InitoError(Exception):
    """Base class for all inito errors."""


class MetadataExtractionError(InitoError):
    """Raised when class metadata cannot be built at decoration time."""


class AnnotationResolutionError(MetadataExtractionError):
    """Raised when field type hints cannot be resolved."""


class InvalidFieldDefinitionError(MetadataExtractionError):
    """Raised when a field declaration is structurally invalid."""


class CodeGenerationError(InitoError):
    """Raised when generated method source fails to compile or execute."""


class DecoratorConfigurationError(InitoError):
    """Raised when decorator options are invalid or conflicting."""


class DuplicateGeneratorError(InitoError):
    """Raised when a generator name collides in the registry."""


class BuilderValidationError(InitoError):
    """Raised when `.build()` is called before every required field is set."""


class DependencyRegistrationError(InitoError):
    """Raised when @Service/@Singleton registration or its constructor annotations are invalid."""


class UnresolvableDependencyError(InitoError):
    """Raised when a needed dependency type has no registration and no default value."""


class CircularDependencyError(InitoError):
    """Raised when resolving a dependency graph revisits a class already mid-resolution."""
