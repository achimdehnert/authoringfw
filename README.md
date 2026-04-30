# iil-authoringfw — Authoring Framework

Domain schemas for AI-assisted creative writing applications.

[![PyPI](https://img.shields.io/pypi/v/iil-authoringfw)](https://pypi.org/project/iil-authoringfw/)
[![Python](https://img.shields.io/pypi/pyversions/iil-authoringfw)](https://pypi.org/project/iil-authoringfw/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install iil-authoringfw
# With aifw LLM integration:
pip install "iil-authoringfw[aifw]"
# All optional dependencies:
pip install "iil-authoringfw[all]"
```

## Extras / Optional Dependencies

| Extra | Dependencies | Purpose |
|---|---|---|
| `aifw` | iil-aifw>=0.6.1 | LLM completion integration |
| `yaml` | pyyaml>=6.0 | YAML template loading |
| `promptfw` | iil-promptfw>=0.5.5 | Prompt template rendering |
| `all` | all above | Full feature set |

## Quick Start

```python
from authoringfw import StyleProfile, CharacterProfile, WorldContext, get_format

# Style constraints for prompt injection
style = StyleProfile(tone="melancholic", pov="third_limited", tense="past")
constraints = style.to_constraints()

# Character context
alice = CharacterProfile(
    name="Alice",
    role="protagonist",
    personality_traits=["brave", "curious"],
    arc="From fear to courage",
)
print(alice.to_context_string())

# World context
world = WorldContext(
    title="The Shattered Realms",
    genre="fantasy",
    world_rules=["Magic costs life force", "Dragons are extinct"],
)
print(world.to_context_string())

# Format profiles (novel, essay, series, scientific)
roman = get_format("roman")
print(roman.style_constraints)
```

## Schemas

- **`StyleProfile`** — tone, POV, tense, vocabulary, sentence rhythm
- **`CharacterProfile`** — name, role, traits, backstory, arc, relationships
- **`WorldContext`** — title, genre, setting, world rules, locations, lore
- **`VersionMetadata`** — immutable content snapshot with hash, semver, LLM metadata
- **`PhaseSnapshot`** — project state at a workflow phase boundary

## Format Profiles

Built-in formats: `roman`, `essay`, `serie`, `scientific`

```python
from authoringfw.formats.base import get_format, WorkflowPhase

novel = get_format("roman")
outline_steps = novel.steps_for_phase(WorkflowPhase.OUTLINE)
```

## Adapter Interfaces

Protocol-based adapters — no inheritance required:

```python
from authoringfw.adapters.interfaces import IStyleAdapter

class MyStyleAdapter:
    async def get_profile(self, style_id): ...
    async def analyze_text(self, text): ...
    def generate_style_constraints(self, profile): ...
    async def score_conformity(self, text, profile): ...

adapter = MyStyleAdapter()
assert isinstance(adapter, IStyleAdapter)  # True via @runtime_checkable
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
