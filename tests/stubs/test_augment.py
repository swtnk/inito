import types

from inito import Data
from inito.stubs.augment import augment_stub


def _module_with(**objects: object) -> types.ModuleType:
    module = types.ModuleType("fixture")
    for name, obj in objects.items():
        setattr(module, name, obj)
    return module


def test_injects_members_and_strips_the_inito_decorator():
    @Data
    class User:
        name: str
        age: int = 0

    base = "from inito import Data\n\n@Data\nclass User:\n    name: str\n    age: int\n"
    out = augment_stub(base, _module_with(User=User))

    assert "def get_name(self) -> str:" in out
    assert "def __init__(self, name: str, age: int" in out
    assert "@Data" not in out  # inito's own decorator removed so pyright doesn't double-synthesize


def test_preserves_user_defined_methods():
    @Data
    class Service:
        x: int

        def custom(self) -> int:
            return self.x

    base = "class Service:\n    x: int\n    def custom(self) -> int: ...\n"
    out = augment_stub(base, _module_with(Service=Service))

    assert "def custom(self) -> int:" in out  # kept
    assert "def get_x(self) -> int:" in out  # injected


def test_leaves_non_inito_classes_untouched():
    class Plain:
        pass

    base = "class Plain:\n    y: int\n"
    out = augment_stub(base, _module_with(Plain=Plain))

    assert "get_" not in out
    assert "y: int" in out


def test_strips_an_attribute_style_inito_decorator():
    @Data
    class Model:
        a: int

    base = "import inito\n\n@inito.data\nclass Model:\n    a: int\n"
    out = augment_stub(base, _module_with(Model=Model))
    assert "@inito.data" not in out
    assert "def get_a(self) -> int:" in out


def test_adds_any_import_for_a_fallback_member():
    from inito.core.attach import GENERATED_MARKER

    @Data
    class Widget:
        x: int

    def weird(self):  # a generated member matching none of the known shapes
        pass

    setattr(weird, GENERATED_MARKER, True)
    Widget.weird = weird  # type: ignore[attr-defined]

    out = augment_stub("class Widget:\n    x: int\n", _module_with(Widget=Widget))
    assert "from typing import Any" in out
    assert "def weird(self, *args: Any, **kwargs: Any) -> Any:" in out


def test_replaces_a_conflicting_member_rather_than_duplicating():
    @Data
    class Model:
        a: int

    base = "class Model:\n    a: int\n    def __init__(self) -> None: ...\n"
    out = augment_stub(base, _module_with(Model=Model))

    assert out.count("def __init__") == 1
    assert "def __init__(self, a: int) -> None:" in out
