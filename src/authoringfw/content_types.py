"""
Content-type configuration for AI-assisted authoring.

Provides default StyleProfile and chunk vocabulary per content_type,
loaded from bundled YAML data files. Any repo can use::

    from authoringfw.content_types import get_content_type_config, list_content_types

    cfg = get_content_type_config("academic")
    style = cfg.style_profile        # authoringfw.StyleProfile
    vocab = cfg.chunk_vocab           # dict with opening/mid/mid_detail
    constraints = style.to_constraints()

To add a new content_type: add a YAML file to data/content_types/{name}.yaml
in the authoringfw package. No Python code changes needed.

New in 0.9.0.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

from .schema.style import StyleProfile

logger = logging.getLogger(__name__)

_DEFAULT_CONTENT_TYPE = "novel"

_DEFAULT_CHUNK_VOCAB: dict[str, str] = {
    "opening": "Eröffnung",
    "mid": "Setze den Text fort",
    "mid_detail": "Führe den Inhalt nahtlos weiter",
}


@dataclass(frozen=True)
class ContentTypeConfig:
    """Configuration for a specific content_type, loaded from YAML."""

    name: str
    style_profile: StyleProfile
    chunk_vocab: dict[str, str] = field(default_factory=dict)


def _data_dir() -> Path:
    """Resolve the bundled data/content_types/ directory."""
    try:
        ref = resources.files("authoringfw") / "data" / "content_types"
        return Path(str(ref))
    except (TypeError, FileNotFoundError):
        return Path(__file__).parent / "data" / "content_types"


def list_content_types() -> list[str]:
    """Return all available content_type names (from bundled YAML files)."""
    d = _data_dir()
    if not d.is_dir():
        return [_DEFAULT_CONTENT_TYPE]
    return sorted(p.stem for p in d.glob("*.yaml"))


def get_content_type_config(content_type: str) -> ContentTypeConfig:
    """
    Load ContentTypeConfig for a content_type from bundled YAML.

    Falls back to 'novel' defaults if the content_type is unknown.
    """
    import yaml

    d = _data_dir()
    yaml_path = d / f"{content_type}.yaml"
    if not yaml_path.exists():
        logger.warning(
            "No config for content_type '%s', falling back to '%s'",
            content_type, _DEFAULT_CONTENT_TYPE,
        )
        yaml_path = d / f"{_DEFAULT_CONTENT_TYPE}.yaml"

    if not yaml_path.exists():
        return ContentTypeConfig(
            name=content_type,
            style_profile=StyleProfile(),
            chunk_vocab=dict(_DEFAULT_CHUNK_VOCAB),
        )

    data: dict[str, Any] = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    style_data = data.get("style", {})
    style = StyleProfile(**{k: v for k, v in style_data.items() if k in StyleProfile.model_fields})

    vocab = data.get("chunk_vocab", dict(_DEFAULT_CHUNK_VOCAB))

    return ContentTypeConfig(
        name=content_type,
        style_profile=style,
        chunk_vocab=vocab,
    )
