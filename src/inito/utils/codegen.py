"""Compiles generated source text into live function objects.

This module is the only place in inito that calls ``exec``. Every generator
builds a complete ``def`` block as source text; this function turns that text
into a real, directly callable function object once, at decoration time.
"""

from __future__ import annotations

from typing import Any, Callable

from inito.exceptions.errors import CodeGenerationError


def build_function(
    name: str,
    source: str,
    globals_ns: dict[str, Any] | None = None,
    qualname: str | None = None,
) -> Callable[..., Any]:
    """Compile a ``def <name>(...): ...`` source block into a function."""
    exec_globals = dict(globals_ns or {})
    filename = f"<inito:{qualname or name}>"
    try:
        code = compile(source, filename=filename, mode="exec")
        exec(code, exec_globals)
    except Exception as error:
        raise CodeGenerationError(f"Failed to generate {name!r}:\n{source}") from error

    function = exec_globals[name]
    function.__name__ = name
    function.__qualname__ = qualname or name
    return function  # type: ignore[no-any-return]
