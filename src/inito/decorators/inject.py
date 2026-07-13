"""@Inject: auto-wires a function's type-annotated parameters from a DI container per call."""

from __future__ import annotations

import functools
import inspect
import typing
from typing import Any, Callable, Optional

from inito.di.container import _MISSING, Container, default_container
from inito.di.dependency_resolver import registrable_type
from inito.utils.codegen import build_function

# (param_name, positional_index_or_None, resolved_type) computed once at decoration time.
_Injectable = tuple[str, Optional[int], Any]

_UNSET = object()
"""Marks a specialized-wrapper parameter the caller did not supply (distinct from _MISSING)."""


def Inject(  # noqa: N802 -- PascalCase matches every other inito decorator
    func: Callable[..., Any] | None = None,
    *,
    container: Container | None = None,
) -> Any:  # noqa: ANN401 -- dual-mode dispatch, returns either a wrapped function or a decorator
    """Wrap fn so its type-annotated, unfilled parameters are resolved from a Container per call.

    Explicit args/kwargs supplied by the caller are never overridden. Unlike
    every class decorator in this library, resolution here is a real per-call
    cost (a container.get() per unfilled, container-registered parameter) -
    @Inject targets composition-root entry points (e.g. a main()/handler
    function), not generated hot-path methods, so this cost is intentional
    and documented rather than hidden. All signature/type-hint inspection is
    still done exactly once, at decoration time; the per-call path only checks
    which parameters the caller already supplied and resolves the rest.

    For an ordinary signature (no ``*args``/``**kwargs``/positional-only), the
    wrapper is generated with the function's own parameters, so a call skips the
    generic ``*args``/``**kwargs`` packing and per-parameter loop; exotic
    signatures fall back to a generic wrapper with identical behavior.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        return _wrap(fn, container if container is not None else default_container)

    return decorator(func) if func is not None else decorator


def _collect_injectables(fn: Callable[..., Any]) -> list[_Injectable]:
    """Precompute, once, each annotated parameter's name, positional index, and resolved type.

    A parameter is injectable if it carries a type annotation. Its positional
    index (used per call to tell whether the caller already passed it
    positionally) is None for keyword-only parameters and for anything after a
    ``*args`` - those can only be supplied by keyword.
    """
    hints = typing.get_type_hints(fn, include_extras=True)
    hints.pop("return", None)
    injectables: list[_Injectable] = []
    positional_index = 0
    after_var_positional = False
    for param in inspect.signature(fn).parameters.values():
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            after_var_positional = True
            continue
        if param.kind is inspect.Parameter.VAR_KEYWORD:
            continue
        positional = param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        if param.name in hints:
            index = positional_index if (positional and not after_var_positional) else None
            injectables.append((param.name, index, registrable_type(hints[param.name])))
        if positional:
            positional_index += 1
    return injectables


def _wrap(fn: Callable[..., Any], target_container: Container) -> Callable[..., Any]:
    injectables = _collect_injectables(fn)
    specialized = _specialized_wrapper(fn, injectables, target_container)
    if specialized is not None:
        return specialized
    return _generic_wrapper(fn, injectables, target_container)


def _generic_wrapper(
    fn: Callable[..., Any], injectables: list[_Injectable], target_container: Container
) -> Callable[..., Any]:
    # Bind the resolver once, at decoration time, so the per-call loop makes a
    # single local call (no ``target_container.`` attribute lookup per injectable)
    # and folds the old is_registered + get pair into one container traversal.
    resolve = target_container._resolve_optional

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401 -- forwards fn's own signature
        supplied_positional = len(args)
        for name, index, resolved_type in injectables:
            if name in kwargs or (index is not None and index < supplied_positional):
                continue
            value = resolve(resolved_type)
            if value is not _MISSING:
                kwargs[name] = value
        return fn(*args, **kwargs)

    return wrapper


_SPECIALIZABLE_KINDS = frozenset(
    {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
)
_RESERVED_PREFIX = "_inito_"
"""Prefix reserved for the generated wrapper's helper names; a parameter using it
forces the generic-wrapper fallback so a user name can never shadow a helper."""


def _specialized_wrapper(
    fn: Callable[..., Any], injectables: list[_Injectable], target_container: Container
) -> Callable[..., Any] | None:
    """Generate a wrapper with fn's own signature, or None for an exotic signature.

    Falls back (returns None) for ``*args``/``**kwargs``/positional-only parameters,
    a parameter using the reserved ``_inito_`` prefix, or when a required positional
    parameter would follow a defaulted one - cases the generic wrapper still handles
    with identical behavior.
    """
    if not injectables:
        return None
    parameters = list(inspect.signature(fn).parameters.values())
    if any(param.kind not in _SPECIALIZABLE_KINDS for param in parameters):
        return None
    if any(param.name.startswith(_RESERVED_PREFIX) for param in parameters):
        return None
    injected_types = {name: resolved_type for name, _, resolved_type in injectables}
    plan = _render_specialized_source(fn, parameters, injected_types)
    if plan is None:
        return None
    source, namespace = plan
    namespace["_inito_resolve"] = target_container._resolve_optional
    wrapper = build_function(fn.__name__, source, namespace, fn.__qualname__)
    return functools.wraps(fn)(wrapper)


def _render_specialized_source(
    fn: Callable[..., Any],
    parameters: list[inspect.Parameter],
    injected_types: dict[str, Any],
) -> tuple[str, dict[str, Any]] | None:
    namespace: dict[str, Any] = {
        "_inito_unset": _UNSET,
        "_inito_missing": _MISSING,
        "_inito_fn": fn,
    }
    signature_parts: list[str] = []
    call_parts: list[str] = []
    body: list[str] = []
    saw_default = False
    star_emitted = False
    for param in parameters:
        name = param.name
        keyword_only = param.kind is inspect.Parameter.KEYWORD_ONLY
        if keyword_only and not star_emitted:
            signature_parts.append("*")
            star_emitted = True
        if name in injected_types:
            signature_parts.append(f"{name}=_inito_unset")
            saw_default = True
            _emit_injection(name, param, injected_types[name], namespace, body)
        elif param.default is not inspect.Parameter.empty:
            default_ref = f"_inito_default_{name}"
            namespace[default_ref] = param.default
            signature_parts.append(f"{name}={default_ref}")
            saw_default = True
        else:
            if saw_default and not keyword_only:
                return None  # a required positional after a defaulted one - not expressible
            signature_parts.append(name)
        call_parts.append(f"{name}={name}" if keyword_only else name)
    header = f"def {fn.__name__}({', '.join(signature_parts)}):"
    # body is always non-empty here: the caller only specializes when there is at
    # least one injectable, and each emits its resolve block.
    return f"{header}\n" + "\n".join(
        body
    ) + f"\n    return _inito_fn({', '.join(call_parts)})\n", namespace


def _emit_injection(
    name: str,
    param: inspect.Parameter,
    resolved_type: Any,  # noqa: ANN401 -- the parameter's autowire type
    namespace: dict[str, Any],
    body: list[str],
) -> None:
    type_ref = f"_inito_type_{name}"
    namespace[type_ref] = resolved_type
    body.append(f"    if {name} is _inito_unset:")
    body.append(f"        _inito_resolved = _inito_resolve({type_ref})")
    if param.default is inspect.Parameter.empty:
        message_ref = f"_inito_missingmsg_{name}"
        namespace[message_ref] = f"{param.name!r} is required, unregistered, and was not supplied"
        body.append("        if _inito_resolved is _inito_missing:")
        body.append(f"            raise TypeError({message_ref})")
        body.append(f"        {name} = _inito_resolved")
    else:
        default_ref = f"_inito_default_{name}"
        namespace[default_ref] = param.default
        body.append(
            f"        {name} = _inito_resolved if _inito_resolved is not _inito_missing "
            f"else {default_ref}"
        )


inject = Inject
