"""
authoringfw — Authoring Framework

Domain schemas and orchestration base for AI-assisted creative writing.

New in 0.4.0: BaseContentOrchestrator, ContentTask, ContentResult,
OrchestrationError, ConfigurationError (ADR-096 Phase 3).

New in 0.4.1: writing/ sub-domain — ChapterOrchestrator, SummaryOrchestrator,
ChapterTask, ChapterResult, SummaryTask, SummaryResult.
"""

__version__ = "0.4.1"

from authoringfw.base import BaseContentOrchestrator
from authoringfw.consistency import ConsistencyChecker, ConsistencyIssue, ConsistencyReport
from authoringfw.exceptions import (
    AuthoringFWError,
    ConfigurationError,
    OrchestrationError,
    TemplateNotFoundError,
)
from authoringfw.formats.base import FormatProfile, WorkflowPhase, get_format
from authoringfw.planning import PlanningFieldConfig, get_planning_config
from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.style import StyleProfile
from authoringfw.schema.versioning import ChangeType, PhaseSnapshot, VersionMetadata
from authoringfw.schema.world import WorldContext
from authoringfw.types import ContentResult, ContentTask
from authoringfw.writing import (
    ChapterOrchestrator,
    ChapterResult,
    ChapterTask,
    SummaryOrchestrator,
    SummaryResult,
    SummaryTask,
)

__all__ = [
    # Orchestration base
    "BaseContentOrchestrator",
    "ContentTask",
    "ContentResult",
    # Writing sub-domain
    "ChapterOrchestrator",
    "ChapterTask",
    "ChapterResult",
    "SummaryOrchestrator",
    "SummaryTask",
    "SummaryResult",
    # Exceptions
    "AuthoringFWError",
    "OrchestrationError",
    "ConfigurationError",
    "TemplateNotFoundError",
    # Schemas
    "StyleProfile",
    "CharacterProfile",
    "WorldContext",
    "VersionMetadata",
    "ChangeType",
    "PhaseSnapshot",
    # Formats & planning
    "FormatProfile",
    "WorkflowPhase",
    "get_format",
    "PlanningFieldConfig",
    "get_planning_config",
    # Consistency
    "ConsistencyChecker",
    "ConsistencyReport",
    "ConsistencyIssue",
    "__version__",
]
