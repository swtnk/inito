"""Execute every ```python code block in docs/recipes.md so the docs can't rot.

Each recipe block is self-contained (its own imports). Each is executed in its
own throwaway module registered in ``sys.modules`` - the same environment a
real ``.py`` file has, so annotation forward-references (`db: Database`)
resolve exactly as they would for a user.
"""

from __future__ import annotations

import re
import sys
import types
from pathlib import Path

import pytest

_RECIPES = Path(__file__).resolve().parents[2] / "docs" / "recipes.md"
_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _code_blocks() -> list[str]:
    return _BLOCK.findall(_RECIPES.read_text())


def test_recipes_file_has_code_blocks():
    assert _code_blocks(), "expected runnable python blocks in docs/recipes.md"


@pytest.mark.parametrize("index, block", list(enumerate(_code_blocks())))
def test_recipe_block_runs(index: int, block: str):
    name = f"_inito_recipe_{index}"
    module = types.ModuleType(name)
    sys.modules[name] = module
    try:
        exec(compile(block, "<recipes.md>", "exec"), module.__dict__)
    finally:
        del sys.modules[name]
