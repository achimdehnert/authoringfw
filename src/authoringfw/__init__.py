"""
authoringfw — Authoring Framework

Domain schemas and orchestration base for AI-assisted creative writing.

New in 0.4.0: BaseContentOrchestrator, ContentTask, ContentResult,
OrchestrationError, ConfigurationError (ADR-096 Phase 3).

New in 0.4.1: writing/ sub-domain — ChapterOrchestrator, SummaryOrchestrator.

New in 0.5.0: research/ sub-domain — ResearchOrchestrator.
              analysis/ sub-domain — StyleAnalysisOrchestrator, PlotAnalysisOrchestrator.
              Full ADR-096 §4.5 Research → Writing pipeline supported.
              demo/ui.html — standalone browser-based prompt builder & pipeline tester.

New in 0.6.2: text/ sub-domain — TextReformatter, ReformatTask, ReformatResult.
              Generic post-hoc text transformation (no domain coupling).
              Usable from iil-researchfw, bfagent, or any consumer.
"""

__version__ = "0.6.2"

from authoringfw.analysis import (
    AnalysisResult,
    AnalysisTask,
    PlotAnalysisOrchestrator,
    StyleAnalysisOrchestrator,
)
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
from authoringfw.research import ResearchOrchestrator, ResearchResult, ResearchTask
from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.style import StyleProfile
from authoringfw.schema.versioning import ChangeType, PhaseSnapshot, VersionMetadata
from authoringfw.schema.world import WorldContext
from authoringfw.types import ContentResult, ContentTask
from authoringfw.text import (
    ReformatResult,
    ReformatTask,
    TextReformatter,
)
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
    # Research sub-domain
    "ResearchOrchestrator",
    "ResearchTask",
    "ResearchResult",
    # Analysis sub-domain
    "StyleAnalysisOrchestrator",
    "PlotAnalysisOrchestrator",
    "AnalysisTask",
    "AnalysisResult",
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
    # Text sub-domain
    "TextReformatter",
    "ReformatTask",
    "ReformatResult",
    "__version__",
]
