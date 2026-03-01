"""
authoringfw — Authoring Framework

Domain schemas for AI-assisted creative writing applications.
"""

__version__ = "0.3.0"

from authoringfw.schema.style import StyleProfile
from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.world import WorldContext
from authoringfw.schema.versioning import VersionMetadata, ChangeType, PhaseSnapshot
from authoringfw.formats.base import FormatProfile, WorkflowPhase, get_format
from authoringfw.planning import PlanningFieldConfig, get_planning_config
from authoringfw.consistency import ConsistencyChecker, ConsistencyReport, ConsistencyIssue

__all__ = [
    "StyleProfile",
    "CharacterProfile",
    "WorldContext",
    "VersionMetadata",
    "ChangeType",
    "PhaseSnapshot",
    "FormatProfile",
    "WorkflowPhase",
    "get_format",
    "ConsistencyChecker",
    "ConsistencyReport",
    "ConsistencyIssue",
    "PlanningFieldConfig",
    "get_planning_config",
    "__version__",
]
