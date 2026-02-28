"""Versioning schema for AI-generated content snapshots."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    AI_GENERATED = "ai_generated"
    HUMAN_EDITED = "human_edited"
    MERGED = "merged"
    REVERTED = "reverted"


class VersionMetadata(BaseModel):
    """Immutable metadata snapshot for a content version."""

    version_id: str
    semver: str = "1.0.0"
    phase: str = ""
    node_id: str = ""
    change_type: ChangeType = ChangeType.AI_GENERATED
    author: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    parent_version_id: str | None = None
    content_hash: str = ""
    prompt_template_id: str = ""
    prompt_template_version: str = ""
    llm_model: str = ""
    llm_temperature: float = 0.7
    quality_scores: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}

    def compute_hash(self, content: str) -> "VersionMetadata":
        """Return a new instance with content_hash filled in."""
        h = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.model_copy(update={"content_hash": h})


class PhaseSnapshot(BaseModel):
    """A complete snapshot of a project at a workflow phase boundary."""

    snapshot_id: str
    phase: str
    project_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    node_versions: dict[str, str] = Field(default_factory=dict)
    approved_by: str = ""
    notes: str = ""
