from dataclasses import dataclass
from typing import Callable, TypeVar, overload

from typing_extensions import dataclass_transform

from inito.metadata.field import field

_C = TypeVar("_C", bound=type)

@dataclass(frozen=True)
class AllArgsConstructorOptions: ...

@overload
@dataclass_transform(field_specifiers=(field,))
def AllArgsConstructor(maybe_cls: _C) -> _C: ...
@overload
@dataclass_transform(field_specifiers=(field,))
def AllArgsConstructor() -> Callable[[_C], _C]: ...

all_args_constructor = AllArgsConstructor
