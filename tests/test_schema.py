"""Tests for authoringfw schema models."""

import pytest
from pydantic import ValidationError

from authoringfw.schema.style import StyleProfile
from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.world import WorldContext, Location
from authoringfw.schema.versioning import VersionMetadata, ChangeType, PhaseSnapshot
from authoringfw.formats.base import FormatProfile, WorkflowPhase, get_format


def test_style_profile_defaults():
    s = StyleProfile()
    assert s.tone == "neutral"
    assert s.pov == "third_limited"


def test_style_profile_to_constraints():
    s = StyleProfile(tone="dark", pov="first_person", tense="present")
    constraints = s.to_constraints()
    assert any("dark" in c for c in constraints)
    assert any("first_person" in c for c in constraints)


def test_character_profile_context_string():
    c = CharacterProfile(
        name="Alice",
        role="protagonist",
        personality_traits=["brave", "curious"],
        arc="From fear to courage",
    )
    ctx = c.to_context_string()
    assert "Alice" in ctx
    assert "brave" in ctx
    assert "courage" in ctx


def test_world_context_to_string():
    w = WorldContext(
        title="Middle Earth",
        genre="fantasy",
        setting="medieval",
        world_rules=["Magic exists", "Dragons are rare"],
    )
    ctx = w.to_context_string()
    assert "Middle Earth" in ctx
    assert "fantasy" in ctx
    assert "Magic exists" in ctx


def test_version_metadata_frozen():
    v = VersionMetadata(version_id="v1", semver="1.0.0")
    with pytest.raises(Exception):
        v.version_id = "v2"


def test_version_metadata_compute_hash():
    v = VersionMetadata(version_id="v1")
    v2 = v.compute_hash("Hello world content")
    assert v2.content_hash != ""
    assert len(v2.content_hash) == 16


def test_change_type_values():
    assert ChangeType.AI_GENERATED == "ai_generated"
    assert ChangeType.HUMAN_EDITED == "human_edited"


def test_get_format_roman():
    f = get_format("roman")
    assert f.format_type == "roman"
    assert len(f.style_constraints) > 0


def test_get_format_unknown():
    with pytest.raises(KeyError) as exc:
        get_format("nonexistent")
    assert "nonexistent" in str(exc.value)


def test_workflow_phase_values():
    assert WorkflowPhase.FIRST_DRAFT == "first_draft"
    assert WorkflowPhase.PRODUCTION == "production"


def test_format_profile_steps_for_phase():
    from authoringfw.formats.base import StepConfig
    f = FormatProfile(
        format_type="test",
        display_name="Test",
        steps=[
            StepConfig(name="s1", phase=WorkflowPhase.OUTLINE, prompt_template_id="t1"),
            StepConfig(name="s2", phase=WorkflowPhase.FIRST_DRAFT, prompt_template_id="t2"),
        ],
    )
    outline_steps = f.steps_for_phase(WorkflowPhase.OUTLINE)
    assert len(outline_steps) == 1
    assert outline_steps[0].name == "s1"
