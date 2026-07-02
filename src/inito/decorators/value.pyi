from dataclasses import dataclass
from typing import Callable, TypeVar, overload

from typing_extensions import dataclass_transform

_C = TypeVar("_C", bound=type)

@dataclass(frozen=True)
class ValueOptions:
    include_getters: bool = ...

@overload
@dataclass_transform()
def Value(maybe_cls: _C) -> _C: ...
@overload
@dataclass_transform()
def Value(*, include_getters: bool = ...) -> Callable[[_C], _C]: ...

value = Value
