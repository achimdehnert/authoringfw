"""
authoringfw — Authoring Framework

Domain schemas and orchestration base for AI-assisted creative writing.

New in 0.4.0: BaseContentOrchestrator, ContentTask, ContentResult,
OrchestrationError, ConfigurationError (ADR-096 Phase 3).
"""

__version__ = "0.4.0"

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

__all__ = [
    "BaseContentOrchestrator",
    "ContentTask",
    "ContentResult",
    "AuthoringFWError",
    "OrchestrationError",
    "ConfigurationError",
    "TemplateNotFoundError",
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
