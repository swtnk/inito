"""Dependency-injection container: Container, Scope, and the shared default_container."""

from inito.di.container import Container, Scope, ServiceRegistration, default_container
from inito.di.dependency_resolver import Qualifier

__all__ = ["Container", "Qualifier", "Scope", "ServiceRegistration", "default_container"]
