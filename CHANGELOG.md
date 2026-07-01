# Changelog — authoringfw

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

> Accumulated changes on top of the last published release (`0.11.1` on PyPI).
> `pyproject.toml` is at `0.11.2` but that version has not been tagged/published yet —
> cut a release by renaming this section to the chosen version + date and tagging it.

### Changed
- Dependency floor **`iil-aifw>=0.11.2` → `>=0.11.4`** in the `aifw` and `all` extras (#7).
- `__version__` is now derived from installed package metadata (`importlib.metadata`)
  instead of a hardcoded literal, so it can no longer drift from `pyproject.toml` (#8).
- Ruff `target-version` `py311` → `py312` (matches `requires-python >= 3.12`); removed a
  duplicate `Python :: 3.12` classifier (#8).
- Strengthened async orchestrator tests: the ConfigurationError-propagation test now uses
  `pytest.raises` (previously could pass without the error being raised), and the
  aifw-delegation test asserts the forwarded `messages`/`quality_level`/`priority` (#16).

### Added
- Root `CLAUDE.md` and `AGENT_HANDOVER.md` agent-orientation files (#8).

### Fixed
- `ChunkedChapterOrchestrator` over-generated one extra chunk on exact multiples of
  `words_per_chunk` (`(target // wpc) + 1` → `math.ceil`) (#15).
- `ImportError` hints now say `pip install iil-aifw` (the real PyPI name), not `aifw` (#15).
- Replaced deprecated `asyncio.get_event_loop()` with `get_running_loop()` in
  `TextReformatter.areformat()` (Python 3.12+) (#15).
- `yaml.safe_load(...)` results are guarded against `None` on empty YAML in
  `content_types` and the schema `from_yaml` classmethods (avoids `cls(**None)`) (#15).
- Docs/metadata drift: README `aifw` floor and format list, `catalog-info.yaml`
  `pypi/package-name` (`authoringfw` → `iil-authoringfw`); `.hypothesis/` gitignored (#16).

## [0.11.2] — 2026-06-14

### Changed
- **Dependency floor `iil-aifw>=0.6.1` → `>=0.11.2`** (in both the `aifw` and `all` extras). authoringfw passes `quality_level`/`priority` into `aifw.sync_completion()`/`completion()`, but aifw silently ignored those parameters until 0.11.2 (it routed every call to the catch-all `AIActionType` row). From 0.11.2 the routing cascade is actually applied, so authoringfw's quality-tier routing works for the first time. Pinning the floor guarantees the feature is present rather than a silent no-op.

> **Note:** `0.11.2` is the version in `pyproject.toml` but has not been tagged or
> published to PyPI. The latest published release is `0.11.1`.

## [0.11.1] — 2026-06-06

### Fixed
- Declared **PyYAML as a runtime dependency** (`pyyaml>=6.0`). `content_types` imports
  `yaml` at module top and is imported eagerly by the package `__init__`, so `pyyaml` must
  be present at runtime rather than only via the optional `yaml` extra (#4).
- Green CI: label-bootstrap script and lint/test workflow fixes (#4).

## [0.11.0] — 2026-04-25

### Added
- Story prompt templates module (#13)
- `content_types` module — data-driven `StyleProfile` + `chunk_vocab` per content_type (v0.10.0)
- CI workflow with ruff lint, coverage gate, pip-audit
- Platform-Workflows + Rules via bootstrap/sync-workflows

### Changed
- `requires-python = ">=3.12"` — aligns with platform standard
- PyPI publish switched to OIDC trusted publishing (no API token needed)

### Fixed
- `lru_cache`, docstring version, yaml import (34 tests passing)
- Python classifier 3.11 → 3.12

---

> **Note:** Versions 0.2.0–0.10.0 were released but not individually documented here.
> See git log for details: `git log --oneline v0.1.0..v0.11.0`

---

## [0.1.0] — 2026-02-28

### Added
- Initial release
- `StyleProfile` — tone, POV, tense, vocabulary, sentence rhythm + `to_constraints()`
- `CharacterProfile` — name, role, traits, backstory, arc, relationships + `to_context_string()`
- `WorldContext` + `Location` — world rules, locations, lore + `to_context_string()`
- `VersionMetadata` — immutable content snapshot with SHA-256 hash, semver, LLM metadata
- `PhaseSnapshot` — project state at workflow phase boundary
- `ChangeType` enum (AI_GENERATED, HUMAN_EDITED, MERGED, REVERTED)
- `FormatProfile` — novel, essay, series, scientific with workflow phases and style constraints
- `WorkflowPhase` enum (IDEATION → PRODUCTION)
- `StepConfig` — per-step template and parameter config
- `get_format()` — lookup built-in format profiles
- `IStyleAdapter`, `ICharacterAdapter`, `IWorldAdapter` Protocol interfaces (`@runtime_checkable`)
