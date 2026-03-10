"""authoringfw.adapters — Protocol-based adapter interfaces."""

from authoringfw.adapters.interfaces import (
    ICharacterAdapter,
    ILocationAdapter,
    ISceneAdapter,
    IStoryAdapter,
    IStyleAdapter,
    IWorldAdapter,
)

__all__ = [
    "IWorldAdapter",
    "ILocationAdapter",
    "ICharacterAdapter",
    "IStoryAdapter",
    "ISceneAdapter",
    "IStyleAdapter",
]
