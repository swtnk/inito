import linecache
import traceback

import pytest

from inito.exceptions.errors import CodeGenerationError
from inito.utils.codegen import build_function


def test_build_function_compiles_and_returns_callable():
    fn = build_function("add_one", "def add_one(x):\n    return x + 1\n")
    assert fn(1) == 2


def test_build_function_uses_provided_globals():
    fn = build_function(
        "get_default",
        "def get_default():\n    return _default\n",
        {"_default": 42},
    )
    assert fn() == 42


def test_build_function_sets_name_and_qualname():
    fn = build_function("greet", "def greet():\n    return 'hi'\n", qualname="Foo.greet")
    assert fn.__name__ == "greet"
    assert fn.__qualname__ == "Foo.greet"


def test_build_function_defaults_qualname_to_name():
    fn = build_function("solo", "def solo():\n    return 1\n")
    assert fn.__qualname__ == "solo"


def test_build_function_wraps_compile_errors():
    with pytest.raises(CodeGenerationError):
        build_function("broken", "def broken(:\n    pass\n")


def test_generated_source_is_registered_with_linecache_for_tracebacks():
    source = "def boom():\n    raise ValueError('x')\n"
    fn = build_function("boom", source, qualname="Widget.boom")
    filename = fn.__code__.co_filename
    assert linecache.getline(filename, 2).strip() == "raise ValueError('x')"

    try:
        fn()
    except ValueError:
        rendered = traceback.format_exc()
    assert "raise ValueError('x')" in rendered


def test_generated_filenames_are_unique():
    a = build_function("f", "def f():\n    return 1\n", qualname="A.f")
    b = build_function("f", "def f():\n    return 2\n", qualname="A.f")
    assert a.__code__.co_filename != b.__code__.co_filename
