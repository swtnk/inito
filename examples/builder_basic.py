"""Runnable example: the three @builder patterns from the original spec.

Note: the spec's examples used `from UUID import uuid4` (wrong casing,
`uuid` is lowercase) and annotated fields with `uuid4` itself (a function,
not a type). Both are fixed here to valid Python; inito does not validate
annotations against runtime values, so the patterns below are otherwise
verbatim.
"""

from dataclasses import dataclass
from uuid import UUID, uuid4

from inito import builder

# Example 1: bare @builder on a plain class.


@builder
class Request:
    request_id: UUID
    prompt: str
    temperature: float
    top_p: int


# Example 2: @builder stacked on @dataclass.


@builder
@dataclass
class DataclassRequest:
    request_id: UUID
    prompt: str
    temperature: float
    top_p: int


# Example 3: @builder(to_builder=True) stacked on @dataclass.


@builder(to_builder=True)
@dataclass
class ToBuilderRequest:
    request_id: UUID
    prompt: str
    temperature: float
    top_p: int


def main() -> None:
    request = (
        Request.builder().request_id(uuid4()).prompt("hello").temperature(0.7).top_p(1).build()
    )
    print(request.prompt, request.temperature, request.top_p)

    dataclass_request = (
        DataclassRequest.builder()
        .request_id(uuid4())
        .prompt("hi")
        .temperature(0.5)
        .top_p(1)
        .build()
    )
    print(dataclass_request)

    original = ToBuilderRequest(uuid4(), "original", 0.9, 1)
    revised = original.to_builder().prompt("revised").build()
    print(original.prompt, revised.prompt)


if __name__ == "__main__":
    main()
