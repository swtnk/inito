"""mypy plugin synthesizing generated members for every inito decorator.

Register in pyproject.toml::

    [tool.mypy]
    plugins = ["inito.typing.mypy_plugin"]
"""

from __future__ import annotations

from collections.abc import Callable

from mypy.plugin import ClassDefContext, Plugin

from inito.typing.mypy_plugin.builder import transform_builder
from inito.typing.mypy_plugin.constructors import (
    transform_all_args_constructor,
    transform_data,
    transform_getter,
    transform_no_args_constructor,
    transform_required_args_constructor,
    transform_setter,
)

_DECORATOR_MODULE = "inito.decorators"


def _register(
    transforms: dict[str, Callable[[ClassDefContext], bool]],
    module: str,
    pascal_name: str,
    lower_name: str,
    transform: Callable[[ClassDefContext], bool],
) -> None:
    transforms[f"{_DECORATOR_MODULE}.{module}.{pascal_name}"] = transform
    transforms[f"{_DECORATOR_MODULE}.{module}.{lower_name}"] = transform


def _build_transforms() -> dict[str, Callable[[ClassDefContext], bool]]:
    transforms: dict[str, Callable[[ClassDefContext], bool]] = {}
    _register(transforms, "data", "Data", "data", transform_data)
    _register(transforms, "getter", "Getter", "getter", transform_getter)
    _register(transforms, "setter", "Setter", "setter", transform_setter)
    _register(
        transforms,
        "no_args_constructor",
        "NoArgsConstructor",
        "no_args_constructor",
        transform_no_args_constructor,
    )
    _register(
        transforms,
        "all_args_constructor",
        "AllArgsConstructor",
        "all_args_constructor",
        transform_all_args_constructor,
    )
    _register(
        transforms,
        "required_args_constructor",
        "RequiredArgsConstructor",
        "required_args_constructor",
        transform_required_args_constructor,
    )
    _register(transforms, "builder", "Builder", "builder", transform_builder)
    return transforms


_TRANSFORMS = _build_transforms()


class InitoPlugin(Plugin):
    """Synthesizes __init__/accessor/builder members for inito decorators."""

    def get_class_decorator_hook_2(self, fullname: str) -> Callable[[ClassDefContext], bool] | None:
        """Return the transform for fullname, if it names an inito decorator."""
        return _TRANSFORMS.get(fullname)


def plugin(version: str) -> type[Plugin]:
    """Mypy plugin entry point (see module docstring for registration)."""
    return InitoPlugin
