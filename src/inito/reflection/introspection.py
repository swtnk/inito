"""Low-level annotation and MRO inspection helpers used at decoration time."""

from __future__ import annotations

import sys
import typing
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from inito.exceptions.errors import AnnotationResolutionError


def collect_ordered_field_names(cls: type) -> tuple[str, ...]:
    """Return every annotated field name across cls's MRO, in declaration order."""
    ordered: dict[str, None] = {}
    for klass in reversed(cls.__mro__[:-1]):
        for name in _own_annotation_names(klass):
            ordered.setdefault(name, None)
    return tuple(ordered)


def _own_annotation_names(klass: type) -> tuple[str, ...]:
    """Return the names klass annotates itself (not inherited), version-safely.

    Python 3.14 (PEP 649/749) evaluates class annotations lazily: a class's
    ``__annotations__`` may not be materialised in its ``__dict__`` until first
    access, so the pre-3.14 ``klass.__dict__.get("__annotations__")`` read can
    miss fields. From 3.14 the ``annotationlib`` module is used with the
    forward-reference format, which returns the annotation *names* without
    evaluating any annotation value (so an undefined forward reference can't
    raise here - resolution happens later, in ``resolve_type_hints``).
    """
    if sys.version_info >= (3, 14):
        import annotationlib

        return tuple(annotationlib.get_annotations(klass, format=annotationlib.Format.FORWARDREF))
    return tuple(klass.__dict__.get("__annotations__", {}))


@contextmanager
def _self_reference_injected(cls: type) -> Iterator[None]:
    """Temporarily bind cls's own name in its module's globals, if not already bound.

    A self-referential annotation (e.g. a linked-list ``next: Node``) would
    otherwise fail to resolve: at decoration time, ``cls``'s own name isn't
    bound in its module's globals yet. Seeding the module dict with ``cls``
    itself (only if that name isn't already bound to something else) lets
    such annotations resolve, without affecting resolution of any other
    class in the MRO, since ``get_type_hints`` looks up each ancestor in
    *its own* module dict only when no explicit ``globalns`` override is
    passed - passing one would apply to every ancestor uniformly instead.
    Shared by ``resolve_type_hints`` (class field annotations) and
    ``inito.di.dependency_resolver`` (constructor parameter annotations),
    since both hit the exact same forward-reference problem.
    """
    module = sys.modules.get(cls.__module__)
    injected = module is not None and not hasattr(module, cls.__name__)
    if injected:
        setattr(module, cls.__name__, cls)
    try:
        yield
    finally:
        if injected:
            delattr(module, cls.__name__)


def resolve_type_hints(cls: type) -> dict[str, Any]:
    """Resolve cls's annotations to real type objects, once."""
    try:
        with _self_reference_injected(cls):
            return typing.get_type_hints(cls, include_extras=True)
    except NameError as error:
        raise AnnotationResolutionError(
            f"Could not resolve type hints for {cls.__qualname__!r}: {error}"
        ) from error


def is_class_var(type_hint: Any) -> bool:  # noqa: ANN401 -- inspects an arbitrary resolved hint
    """Whether type_hint is a typing.ClassVar annotation."""
    return typing.get_origin(type_hint) is typing.ClassVar
