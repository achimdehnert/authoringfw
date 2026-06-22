# CLAUDE.md — iil-authoringfw

Repo operating guide for autonomous agents and contributors. Repo-specific
overrides take precedence over user-level `~/.claude/CLAUDE.md`.

## What this is

`iil-authoringfw` (dist name) / `authoringfw` (import name) is the **Authoring
Framework**: domain schemas and an orchestration base for AI-assisted creative
writing. It provides Pydantic domain models (story / character / scene / style /
world), runtime-checkable adapter Protocols, and content orchestrators
(chapter, summary, research, analysis, text reformatting). It is a library — no
service, no DB. LLM integration is optional (`iil-aifw`, `iil-promptfw` extras).

## Setup

```bash
make install              # pip install -e ".[dev]"  (editable + dev deps)
# or, if PEP 668 blocks system pip, use a venv:
python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
```

`requires-python >= 3.12`. Optional extras: `aifw`, `promptfw`, `yaml`, `all`.

## Test / lint / types

```bash
make test     # python3 -m pytest tests/ --tb=short -q   (186 tests)
make test-v   # verbose
make lint     # ruff check src/ tests/
```

There is **no mypy / type-check target** configured in this repo (no
`[tool.mypy]`); `make types` does not exist. Tests use `pytest-asyncio`
(`asyncio_mode = "auto"`) and `pytest-mock`.

## Architecture — public API map

The package exposes a **broad, flat public API**: the root `authoringfw/__init__.py`
re-exports ~60 names from its subpackages and declares `__all__`. Submodule map:

| Module | Public surface |
|---|---|
| `authoringfw.base` / `.types` | `BaseContentOrchestrator`, `ContentTask`, `ContentResult` |
| `authoringfw.exceptions` | `AuthoringFWError`, `OrchestrationError`, `ConfigurationError`, `TemplateNotFoundError` |
| `authoringfw.schema.*` | `StoryProfile`, `CharacterProfile`, `SceneProfile`, `StyleProfile`, `WorldContext`, `Location`, `VersionMetadata`, `PhaseSnapshot`, `ChangeType` |
| `authoringfw.adapters` | runtime-checkable Protocols: `IStoryAdapter`, `ICharacterAdapter`, `ISceneAdapter`, `IStyleAdapter`, `IWorldAdapter`, `ILocationAdapter` |
| `authoringfw.writing` | `ChapterOrchestrator`, `ChunkedChapterOrchestrator`, `SummaryOrchestrator`, task/result types, `compute_max_tokens`, `compute_words_per_chunk` |
| `authoringfw.research` | `ResearchOrchestrator`, `ResearchTask`, `ResearchResult` |
| `authoringfw.analysis` | `StyleAnalysisOrchestrator`, `PlotAnalysisOrchestrator`, `AnalysisTask`, `AnalysisResult` |
| `authoringfw.text` | `TextReformatter`, `ReformatTask`, `ReformatResult` (domain-agnostic transforms) |
| `authoringfw.formats` | `FormatProfile`, `WorkflowPhase`, `get_format` (`roman`, `essay`, `serie`, `scientific`) |
| `authoringfw.planning` | `PlanningFieldConfig`, `get_planning_config` |
| `authoringfw.consistency` | `ConsistencyChecker`, `ConsistencyReport`, `ConsistencyIssue` |
| `authoringfw.content_types` | `ContentTypeConfig`, `get_content_type_config`, `list_content_types` (loads `StyleProfile` from YAML eagerly at import) |
| `authoringfw.templates` | story prompt templates + `story_registry`, `render_story_template` |

`__version__` resolves from installed package metadata via `importlib.metadata`,
falling back to `"0.0.0.dev0"` in an uninstalled source checkout.

## Conventions

- Commits: `[feat|fix|refactor|docs|test|chore](scope): description`.
- Test names: `test_should_{expected_behavior}` (a naming-convention check warns
  on legacy names; opt out per-test only when justified).
- Ruff `line-length = 100`, `target-version = py312`.
- Public API is the `__all__` in the root `__init__.py` — add new exports there.

## Release (GATED — do NOT run autonomously)

Publishing to PyPI is **gated** and never happens on merge. Versions are bumped
and released only on an explicit human instruction, via the platform `/release`
workflow (OIDC trusted publishing; no API token). Do not touch `version =` in
`pyproject.toml`, the `__version__` resolution, or tag/release as part of routine
work.

## Known issues

- Unpublished version drift: `pyproject.toml` is `0.11.2`, PyPI latest is
  `0.11.1` — `0.11.2` was bumped in-repo but not published. Leave as-is; a
  release is a deliberate, gated step. See `AGENT_HANDOVER.md`.
- `NEXT.md` is an **auto-generated cache**, not a source of truth.
