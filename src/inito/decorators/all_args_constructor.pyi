from dataclasses import dataclass
from typing import Callable, TypeVar, overload

from typing_extensions import dataclass_transform

_C = TypeVar("_C", bound=type)

@dataclass(frozen=True)
class AllArgsConstructorOptions: ...

@overload
@dataclass_transform()
def AllArgsConstructor(maybe_cls: _C) -> _C: ...
@overload
@dataclass_transform()
def AllArgsConstructor() -> Callable[[_C], _C]: ...

all_args_constructor = AllArgsConstructor
