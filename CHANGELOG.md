# Changelog — authoringfw

## [0.11.0] — 2026-04-25

- chore(authoringfw): Platform-Workflows + Rules via bootstrap/sync-workflows
- fix(authoringfw): Python classifier 3.11 → 3.12 (matches requires-python)
- chore: sync .windsurf rules (typechange symlink→file)
- chore: requires-python >= 3.12
- chore: add MIT LICENSE
- feat: add story prompt templates module (#13)
- fix: lru_cache, docstring version, yaml import, tests (34 passed)
- ci: switch PyPI publish to OIDC trusted publishing (no API token needed)
- feat: content_types module — data-driven StyleProfile + chunk_vocab per content_type (0.10.0)
- ci: add CI workflow with ruff lint, coverage gate, pip-audit


## [Unreleased]

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
