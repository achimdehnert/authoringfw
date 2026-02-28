"""Protocol-based adapter interfaces for authoringfw.

Implementations use duck typing — no inheritance required.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.style import StyleProfile
from authoringfw.schema.world import WorldContext


@runtime_checkable
class IStyleAdapter(Protocol):
    """Adapter for reading and scoring style profiles."""

    async def get_profile(self, style_id: str) -> StyleProfile: ...
    async def analyze_text(self, text: str) -> StyleProfile: ...
    def generate_style_constraints(self, profile: StyleProfile) -> list[str]: ...
    async def score_conformity(self, text: str, profile: StyleProfile) -> float: ...


@runtime_checkable
class ICharacterAdapter(Protocol):
    """Adapter for reading character profiles."""

    async def get_character(self, character_id: str) -> CharacterProfile: ...
    async def list_characters(self, project_id: str) -> list[CharacterProfile]: ...


@runtime_checkable
class IWorldAdapter(Protocol):
    """Adapter for reading world context."""

    async def get_world(self, world_id: str) -> WorldContext: ...
    async def list_locations(self, world_id: str) -> list[str]: ...
