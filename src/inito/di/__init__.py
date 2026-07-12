"""Dependency-injection container: Container, Scope, and the shared default_container."""

from inito.di.container import Container, Scope, ServiceRegistration, default_container
from inito.di.dependency_resolver import Qualifier
from inito.di.factory import Factory

__all__ = [
    "Container",
    "Factory",
    "Qualifier",
    "Scope",
    "ServiceRegistration",
    "default_container",
]
