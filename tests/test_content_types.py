"""
Tests for authoringfw.content_types module (0.10.0).

Verifies:
  - list_content_types() returns all 7 bundled content types
  - get_content_type_config() returns correct ContentTypeConfig
  - Fallback to 'novel' for unknown content types
  - lru_cache returns same instance on repeated calls
  - StyleProfile and chunk_vocab are correctly populated
"""

import pytest

from authoringfw.content_types import (
    ContentTypeConfig,
    get_content_type_config,
    list_content_types,
)
from authoringfw.schema.style import StyleProfile


EXPECTED_CONTENT_TYPES = [
    "academic",
    "essay",
    "nonfiction",
    "novel",
    "scientific",
    "screenplay",
    "short_story",
]


class TestListContentTypes:
    def test_should_return_all_bundled_content_types(self):
        result = list_content_types()
        assert result == EXPECTED_CONTENT_TYPES

    def test_should_return_sorted_list(self):
        result = list_content_types()
        assert result == sorted(result)


class TestGetContentTypeConfig:
    @pytest.fixture(autouse=True)
    def _clear_cache(self):
        get_content_type_config.cache_clear()
        yield
        get_content_type_config.cache_clear()

    @pytest.mark.parametrize("ct", EXPECTED_CONTENT_TYPES)
    def test_should_load_config_for_each_content_type(self, ct):
        cfg = get_content_type_config(ct)
        assert isinstance(cfg, ContentTypeConfig)
        assert cfg.name == ct

    @pytest.mark.parametrize("ct", EXPECTED_CONTENT_TYPES)
    def test_should_have_style_profile(self, ct):
        cfg = get_content_type_config(ct)
        assert isinstance(cfg.style_profile, StyleProfile)
        assert cfg.style_profile.tone != ""

    @pytest.mark.parametrize("ct", EXPECTED_CONTENT_TYPES)
    def test_should_have_chunk_vocab_with_required_keys(self, ct):
        cfg = get_content_type_config(ct)
        assert isinstance(cfg.chunk_vocab, dict)
        for key in ("opening", "mid", "mid_detail"):
            assert key in cfg.chunk_vocab, f"Missing chunk_vocab key '{key}' for {ct}"
            assert isinstance(cfg.chunk_vocab[key], str)
            assert len(cfg.chunk_vocab[key]) > 0

    def test_should_fallback_to_novel_for_unknown_type(self):
        cfg = get_content_type_config("nonexistent_type_xyz")
        novel_cfg = get_content_type_config("novel")
        assert cfg.style_profile.tone == novel_cfg.style_profile.tone

    def test_should_cache_repeated_calls(self):
        cfg1 = get_content_type_config("academic")
        cfg2 = get_content_type_config("academic")
        # Same content and the YAML parse is cached (second call is a hit)...
        assert cfg1 == cfg2
        assert get_content_type_config.cache_info().hits >= 1
        # ...but callers get independent objects (no shared mutable state).
        assert cfg1 is not cfg2
        assert cfg1.style_profile is not cfg2.style_profile

    def test_should_not_leak_mutations_across_calls(self):
        """Mutating a returned config must not poison the cache (A1)."""
        cfg1 = get_content_type_config("academic")
        original_tone = cfg1.style_profile.tone
        original_opening = cfg1.chunk_vocab["opening"]

        # Poison attempt on the returned (mutable) config.
        cfg1.style_profile.tone = "POISONED"
        cfg1.chunk_vocab["opening"] = "POISONED"

        cfg2 = get_content_type_config("academic")
        assert cfg2.style_profile.tone == original_tone
        assert cfg2.chunk_vocab["opening"] == original_opening

    def test_should_not_cache_different_types(self):
        cfg_novel = get_content_type_config("novel")
        cfg_academic = get_content_type_config("academic")
        assert cfg_novel is not cfg_academic
        assert cfg_novel.style_profile.tone != cfg_academic.style_profile.tone


class TestContentTypeConfigContract:
    def test_should_be_frozen_dataclass(self):
        cfg = get_content_type_config("novel")
        with pytest.raises(AttributeError):
            cfg.name = "changed"

    def test_should_produce_style_constraints(self):
        cfg = get_content_type_config("academic")
        constraints = cfg.style_profile.to_constraints()
        assert isinstance(constraints, list)
        assert len(constraints) > 0
        assert all(isinstance(c, str) for c in constraints)


class TestAcademicSpecificConfig:
    def test_should_have_academic_tone(self):
        cfg = get_content_type_config("academic")
        assert cfg.style_profile.tone == "academic"

    def test_should_have_present_tense(self):
        cfg = get_content_type_config("academic")
        assert cfg.style_profile.tense == "present"

    def test_should_have_advanced_vocabulary(self):
        cfg = get_content_type_config("academic")
        assert cfg.style_profile.vocabulary_level == "advanced"


class TestNovelSpecificConfig:
    def test_should_have_literary_tone(self):
        cfg = get_content_type_config("novel")
        assert cfg.style_profile.tone == "literary"

    def test_should_have_past_tense(self):
        cfg = get_content_type_config("novel")
        assert cfg.style_profile.tense == "past"

    def test_should_have_third_limited_pov(self):
        cfg = get_content_type_config("novel")
        assert cfg.style_profile.pov == "third_limited"
