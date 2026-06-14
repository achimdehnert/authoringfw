# Changelog — authoringfw

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.11.2] — 2026-06-14

### Changed
- **Dependency floor `iil-aifw>=0.6.1` → `>=0.11.2`** (in both the `aifw` and `all` extras). authoringfw passes `quality_level`/`priority` into `aifw.sync_completion()`/`completion()`, but aifw silently ignored those parameters until 0.11.2 (it routed every call to the catch-all `AIActionType` row). From 0.11.2 the routing cascade is actually applied, so authoringfw's quality-tier routing works for the first time. Pinning the floor guarantees the feature is present rather than a silent no-op.

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
