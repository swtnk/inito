from dataclasses import dataclass
from typing import Callable, TypeVar, overload

from typing_extensions import dataclass_transform

from inito.metadata.field import field

_C = TypeVar("_C", bound=type)

@dataclass(frozen=True)
class DataOptions:
    frozen: bool = ...
    include_getters: bool = ...
    include_setters: bool = ...

@overload
@dataclass_transform(field_specifiers=(field,))
def Data(maybe_cls: _C) -> _C: ...
@overload
@dataclass_transform(field_specifiers=(field,))
def Data(
    *, frozen: bool = ..., include_getters: bool = ..., include_setters: bool = ...
) -> Callable[[_C], _C]: ...

data = Data
