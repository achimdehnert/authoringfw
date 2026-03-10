"""Protocol-based adapter interfaces for authoringfw.

All adapters use structural subtyping (duck typing via Protocol).
No inheritance required — implement the methods, pass type checks.

Domain coverage:
  IWorldAdapter      — WorldContext CRUD
  ILocationAdapter   — Location CRUD (world-scoped)
  ICharacterAdapter  — CharacterProfile CRUD (world-scoped)
  IStoryAdapter      — StoryProfile CRUD (world-scoped)
  ISceneAdapter      — SceneProfile CRUD (story-scoped)
  IStyleAdapter      — StyleProfile read + analysis
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.scene import SceneProfile
from authoringfw.schema.story import StoryProfile
from authoringfw.schema.style import StyleProfile
from authoringfw.schema.world import Location, WorldContext


@runtime_checkable
class IWorldAdapter(Protocol):
    """Adapter for World CRUD operations."""

    async def get_world(self, world_id: str) -> WorldContext: ...
    async def list_worlds(self, search: str = "") -> list[WorldContext]: ...
    async def create_world(
        self, title: str, genre: str = "", setting: str = "", **kw: object
    ) -> WorldContext: ...
    async def update_world(
        self, world_id: str, **fields: object
    ) -> WorldContext: ...
    async def delete_world(self, world_id: str) -> None: ...


@runtime_checkable
class ILocationAdapter(Protocol):
    """Adapter for Location CRUD operations (scoped to a world)."""

    async def get_location(self, location_id: str) -> Location: ...
    async def list_locations(self, world_id: str) -> list[Location]: ...
    async def create_location(
        self,
        world_id: str,
        name: str,
        description: str = "",
        parent_id: str = "",
        **kw: object,
    ) -> Location: ...
    async def update_location(
        self, location_id: str, **fields: object
    ) -> Location: ...
    async def delete_location(self, location_id: str) -> None: ...


@runtime_checkable
class ICharacterAdapter(Protocol):
    """Adapter for CharacterProfile CRUD operations (scoped to a world)."""

    async def get_character(self, character_id: str) -> CharacterProfile: ...
    async def list_characters(self, world_id: str) -> list[CharacterProfile]: ...
    async def create_character(
        self,
        world_id: str,
        name: str,
        role: str = "supporting",
        **kw: object,
    ) -> CharacterProfile: ...
    async def update_character(
        self, character_id: str, **fields: object
    ) -> CharacterProfile: ...
    async def delete_character(self, character_id: str) -> None: ...


@runtime_checkable
class IStoryAdapter(Protocol):
    """Adapter for StoryProfile CRUD operations (scoped to a world)."""

    async def get_story(self, story_id: str) -> StoryProfile: ...
    async def list_stories(self, world_id: str) -> list[StoryProfile]: ...
    async def create_story(
        self,
        world_id: str,
        title: str,
        synopsis: str = "",
        **kw: object,
    ) -> StoryProfile: ...
    async def update_story(
        self, story_id: str, **fields: object
    ) -> StoryProfile: ...
    async def delete_story(self, story_id: str) -> None: ...


@runtime_checkable
class ISceneAdapter(Protocol):
    """Adapter for SceneProfile CRUD operations (scoped to a story)."""

    async def get_scene(self, scene_id: str) -> SceneProfile: ...
    async def list_scenes(self, story_id: str) -> list[SceneProfile]: ...
    async def create_scene(
        self,
        story_id: str,
        title: str,
        summary: str = "",
        order: int = 0,
        **kw: object,
    ) -> SceneProfile: ...
    async def update_scene(
        self, scene_id: str, **fields: object
    ) -> SceneProfile: ...
    async def delete_scene(self, scene_id: str) -> None: ...


@runtime_checkable
class IStyleAdapter(Protocol):
    """Adapter for reading and scoring style profiles."""

    async def get_profile(self, style_id: str) -> StyleProfile: ...
    async def analyze_text(self, text: str) -> StyleProfile: ...
    def generate_style_constraints(
        self, profile: StyleProfile
    ) -> list[str]: ...
    async def score_conformity(
        self, text: str, profile: StyleProfile
    ) -> float: ...
