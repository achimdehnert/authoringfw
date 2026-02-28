"""
authoringfw — Authoring Framework

Domain schemas for AI-assisted creative writing applications.
"""

__version__ = "0.1.0"

from authoringfw.schema.style import StyleProfile
from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.world import WorldContext
from authoringfw.schema.versioning import VersionMetadata, ChangeType
from authoringfw.formats.base import FormatProfile, WorkflowPhase

__all__ = [
    "StyleProfile",
    "CharacterProfile",
    "WorldContext",
    "VersionMetadata",
    "ChangeType",
    "FormatProfile",
    "WorkflowPhase",
    "__version__",
]
