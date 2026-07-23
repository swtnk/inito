from dataclasses import dataclass
from typing import Callable, TypeVar, overload

from typing_extensions import dataclass_transform

from inito.metadata.field import field

_C = TypeVar("_C", bound=type)

@dataclass(frozen=True)
class ValueOptions:
    include_getters: bool = ...
    slots: bool = ...
    freeze_collections: bool = ...

@overload
@dataclass_transform(field_specifiers=(field,))
def Value(maybe_cls: _C) -> _C: ...
@overload
@dataclass_transform(field_specifiers=(field,))
def Value(
    *, include_getters: bool = ..., slots: bool = ..., freeze_collections: bool = ...
) -> Callable[[_C], _C]: ...

value = Value
