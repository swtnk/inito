---
name: release
description: Cut an inito release — bump __version__, fold the CHANGELOG entry, run the gate, commit, push, wait for CI green, then tag to publish to PyPI via the OIDC Release workflow. Use only when the user asks to release / cut an rc / publish a version. Publishing is outward-facing and irreversible per version — confirm the version before tagging.
---

# release

The bump → gate → push → CI → tag flow (run 3× for rc1–rc3).

## Preconditions
- Feature work committed; `gate` skill green (incl. a 3.9 check for release-grade).
- Decide the version with the user. Keep the `-rcN` suffix unless promoting to a
  stable release. Publishing a tag is **irreversible for that version** — confirm.

## Steps
1. Bump `__version__` in `src/inito/__init__.py` (e.g. `1.0.0-rc3` → `1.0.0-rc4`
   or `1.0.0`). Verify: `python -c "import inito; print(inito.__version__)"`,
   `uv build`, `uvx twine check dist/*` (normalizes to e.g. `1.0.0rc4`).
2. Ensure `CHANGELOG.md` has the version's entry (Keep-a-Changelog style); do
   **not** name reference products in it (see auto-memory).
3. Commit `release: <version>`; `git push origin main`.
4. Poll CI on the pushed SHA (GitHub Actions API): all 3.9–3.14 legs + the
   `framework interop` job + build must be **success** before tagging.
5. `git tag -a v<version> -m "…"; git push origin v<version>` → triggers the
   Release workflow (OIDC trusted publishing; no stored token).
6. Confirm: Release run `success`, then `https://pypi.org/pypi/inito/<norm>/json`
   → HTTP 200 (PyPI JSON lags ~1 min).
7. Update `dev/README.md` status; tick the phase task file.

## Notes
- `gh` is not installed here — use `curl` against `api.github.com/repos/swtnk/inito/...`.
- Commit trailer: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Docs auto-publish to the `gh-pages` branch on push to `main` (branch-based Pages).
