# pyright stub generator (`inito-stubgen`)

Closes the README's headline "pyright doesn't see most generated members"
limitation — the Phase 17 pyright gap. pyright has no plugin API, so the only
complete fix is generated `.pyi` stubs it reads automatically.

Legend: `[x]` done · `[ ]` todo

## Done
- [x] `core/attach.py`: stamp `_inito_generated` on every generated member (and
      the Builder class/factory/to_builder) so the tool can find them.
- [x] `src/inito/stubs/`: `emit` (member stub source from `ClassMetadata` +
      marked members — correct per-decorator signatures incl. NoArgs/Required),
      `augment` (AST-inject into a stubgen base, strip inito decorators, dedup,
      ensure `Any` import), `generator` (mypy `stubgen` base + import +
      augment), `cli` (`inito-stubgen <paths>`).
- [x] Packaging: `[project.scripts] inito-stubgen`; `stubgen` extra (mypy).
      Runtime stays zero-dependency (tool is opt-in, dev-time).
- [x] Tests (`tests/stubs/`, 21): dep-free `emit`/`augment` unit tests +
      `generator`/`cli` (real stubgen) + **pyright end-to-end acid test**
      (skipif no pyright) proving 2→0 errors on a consumer. New CI `pyright`
      job. Coverage 97%+.
- [x] Docs: README + `docs/installation.md` + `docs/troubleshooting.md` +
      `docs/migration.md` retired the limitation → "full support via
      `inito-stubgen`". docs build clean `-W`.

## Verified
- pyright on a consumer importing `@Data`/`@Builder` models: **2 errors → 0**
  after `inito-stubgen`. `user.get_name()`, `Request.builder().path().build()`,
  `request.path`, and per-decorator constructors all type-check.

## Later (out of scope here)
- [ ] pre-commit hook recipe / watch mode (documented as manual for now).
- [ ] Unify `emit.py`'s per-decorator member rules with the mypy plugin's into
      one shared spec (cleanup; not needed for correctness).
