# AGENT_HANDOVER.md — iil-authoringfw

Living current-state / next-priorities handover for the next agent or contributor.
`NEXT.md` is an auto-generated cache, not the source of truth — this file is.

## Current state (observed)

- Library package: dist `iil-authoringfw`, import `authoringfw`. `requires-python >= 3.12`.
- In-repo version `0.11.2` (`pyproject.toml`); root `__init__.py` resolves
  `__version__` from installed metadata via `importlib.metadata`.
- Tests: **186 passing** (`make test`). Ruff lint clean (`make lint`).
- No mypy / type-check target exists in this repo.
- Broad flat public API: root `__init__.py` re-exports ~60 names with `__all__`.

## Recently landed

- Tier-1 agent-readiness (this change): `CLAUDE.md` + `AGENT_HANDOVER.md`,
  `__version__` now from `importlib.metadata` (was hardcoded `"0.11.0"`, stale vs
  pyproject), config alignment — ruff `target-version py311 → py312`, classifiers
  cleaned (duplicate `3.12` → `3` + `3.12`). No behavior change.
- `iil-aifw` floor raised to `>=0.11.4` (#7) so `quality_level`/`priority` routing
  is actually applied rather than a silent no-op.
- Publish gate + build moved py3.11 → 3.12 (#5).

## Known issues / TODO

- **Unpublished version drift**: `pyproject.toml` = `0.11.2`, PyPI latest = `0.11.1`.
  `0.11.2` was bumped in-repo but never published. Do **not** auto-publish; a
  release is a deliberate, gated human step (`/release`). Just be aware imports
  from PyPI lag the repo by one patch.
- Hardcoded version strings remain inside the `__init__.py` module docstring
  ("New in 0.x.y …" changelog notes) — cosmetic only; `__version__` itself is now
  metadata-driven.
- No mypy config — types are unchecked. Out of scope for Tier 1.

## Next priorities

1. Decide whether to publish `0.11.2` (closes the PyPI drift) — gated, human call.
2. Optional: add a `[tool.mypy]` config + `make types` target for Tier 2.
3. Keep `__all__` in sync as new public symbols are added.

## Pointers

- Operating guide: `CLAUDE.md` (setup / test-lint / module map / release gate).
- Public API: `src/authoringfw/__init__.py` (`__all__`).
- Changelog: `CHANGELOG.md`. Release flow: platform `/release` workflow (OIDC).
