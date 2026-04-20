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

__version__ = "0.11.0"

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
from authoringfw.adapters import (
    ICharacterAdapter,
    ILocationAdapter,
    ISceneAdapter,
    IStoryAdapter,
    IStyleAdapter,
    IWorldAdapter,
)
from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.scene import SceneProfile
from authoringfw.schema.story import StoryProfile
from authoringfw.schema.style import StyleProfile
from authoringfw.schema.versioning import ChangeType, PhaseSnapshot, VersionMetadata
from authoringfw.schema.world import Location, WorldContext
from authoringfw.types import ContentResult, ContentTask
from authoringfw.text import (
    ReformatResult,
    ReformatTask,
    TextReformatter,
)
from authoringfw.content_types import (
    ContentTypeConfig,
    get_content_type_config,
    list_content_types,
)
from authoringfw.templates import (
    CHAPTER_TEMPLATE,
    OUTLINE_TEMPLATE,
    PromptTemplateSpec,
    PromptVariable,
    SCENE_ENRICHMENT_TEMPLATE,
    SCENE_OUTLINE_TEMPLATE,
    STORYLINE_TEMPLATE,
    render_story_template,
    story_registry,
)
from authoringfw.writing import (
    ChapterOrchestrator,
    ChapterResult,
    ChapterTask,
    ChunkedChapterOrchestrator,
    SummaryOrchestrator,
    SummaryResult,
    SummaryTask,
    compute_max_tokens,
    compute_words_per_chunk,
)

__all__ = [
    # Orchestration base
    "BaseContentOrchestrator",
    "ContentTask",
    "ContentResult",
    # Writing sub-domain
    "ChapterOrchestrator",
    "ChunkedChapterOrchestrator",
    "ChapterTask",
    "ChapterResult",
    "SummaryOrchestrator",
    "SummaryTask",
    "SummaryResult",
    "compute_max_tokens",
    "compute_words_per_chunk",
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
    "Location",
    "SceneProfile",
    "StoryProfile",
    "VersionMetadata",
    "ChangeType",
    "PhaseSnapshot",
    # Adapter interfaces
    "IWorldAdapter",
    "ILocationAdapter",
    "ICharacterAdapter",
    "IStoryAdapter",
    "ISceneAdapter",
    "IStyleAdapter",
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
    # Content-type configuration (0.10.0)
    "ContentTypeConfig",
    "get_content_type_config",
    "list_content_types",
    # Story templates (0.11.0)
    "OUTLINE_TEMPLATE",
    "CHAPTER_TEMPLATE",
    "SCENE_OUTLINE_TEMPLATE",
    "SCENE_ENRICHMENT_TEMPLATE",
    "STORYLINE_TEMPLATE",
    "PromptTemplateSpec",
    "PromptVariable",
    "render_story_template",
    "story_registry",
    "__version__",
]
