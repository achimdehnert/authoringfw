"""Tests for PlanningFieldConfig and get_planning_config."""

import pytest
from authoringfw.planning import (
    PlanningFieldConfig,
    get_planning_config,
    PLANNING_ROMAN,
    PLANNING_ACADEMIC,
    PLANNING_SCIENTIFIC,
    PLANNING_NONFICTION,
    PLANNING_ESSAY,
)
from authoringfw.formats.base import get_format


class TestGetPlanningConfig:
    def test_roman_returns_fiction_config(self):
        cfg = get_planning_config("roman")
        assert cfg.show_themes is True
        assert cfg.show_logline is True
        assert cfg.show_abstract is False
        assert cfg.show_citation_style is False
        assert cfg.show_field_of_study is False
        assert cfg.word_count_default == 50000

    def test_novel_alias_returns_roman(self):
        assert get_planning_config("novel") is PLANNING_ROMAN

    def test_academic_hides_fiction_fields(self):
        cfg = get_planning_config("academic")
        assert cfg.show_themes is False
        assert cfg.show_logline is False
        assert cfg.show_abstract is True
        assert cfg.show_citation_style is True
        assert cfg.show_field_of_study is True
        assert cfg.show_audience is False
        assert cfg.show_author_style is False
        assert cfg.word_count_default == 80000

    def test_scientific_shows_hypothesis(self):
        cfg = get_planning_config("scientific")
        assert cfg.show_hypothesis is True
        assert cfg.show_keywords is True
        assert cfg.show_citation_style is True
        assert cfg.word_count_default == 8000

    def test_nonfiction_shows_field_of_study(self):
        cfg = get_planning_config("nonfiction")
        assert cfg.show_field_of_study is True
        assert cfg.show_logline is False
        assert cfg.show_abstract is True
        assert cfg.show_audience is True
        assert cfg.word_count_default == 60000

    def test_essay_shows_thesis_fields(self):
        cfg = get_planning_config("essay")
        assert cfg.show_themes is True
        assert cfg.show_logline is False
        assert cfg.show_abstract is False
        assert cfg.show_citation_style is False
        assert cfg.word_count_default == 4000

    def test_unknown_format_falls_back_to_roman(self):
        cfg = get_planning_config("unknown_format")
        assert cfg is PLANNING_ROMAN

    def test_action_codes_are_set(self):
        assert get_planning_config("roman").planning_action_code == "planning_roman"
        assert get_planning_config("academic").planning_action_code == "planning_academic"
        assert get_planning_config("scientific").planning_action_code == "planning_scientific"
        assert get_planning_config("nonfiction").planning_action_code == "planning_nonfiction"
        assert get_planning_config("essay").planning_action_code == "planning_essay"


class TestPlanningFieldConfigModel:
    def test_to_dict_returns_all_fields(self):
        cfg = PLANNING_ACADEMIC
        d = cfg.to_dict()
        assert "premise_label" in d
        assert "show_themes" in d
        assert "show_abstract" in d
        assert "planning_action_code" in d

    def test_premise_labels_are_format_specific(self):
        assert "Prämisse" in get_planning_config("roman").premise_label
        assert "Forschungsfrage" in get_planning_config("academic").premise_label
        assert "These" in get_planning_config("essay").premise_label
        assert "Kernbotschaft" in get_planning_config("nonfiction").premise_label

    def test_is_pydantic_model(self):
        cfg = PlanningFieldConfig()
        assert hasattr(cfg, "model_dump")


class TestFormatProfilePlanningFieldsProperty:
    def test_roman_format_has_planning_fields(self):
        fmt = get_format("roman")
        fields = fmt.planning_fields
        assert isinstance(fields, PlanningFieldConfig)
        assert fields.show_logline is True

    def test_scientific_format_has_planning_fields(self):
        fmt = get_format("scientific")
        fields = fmt.planning_fields
        assert fields.show_citation_style is True
        assert fields.show_hypothesis is True

    def test_academic_format_has_planning_fields(self):
        fmt = get_format("academic")
        fields = fmt.planning_fields
        assert fields.show_abstract is True
        assert fields.show_author_style is False

    def test_nonfiction_format_has_planning_fields(self):
        fmt = get_format("nonfiction")
        fields = fmt.planning_fields
        assert fields.show_field_of_study is True

    def test_unknown_format_fallback(self):
        fmt = get_format("unknown_xyz")
        fields = fmt.planning_fields
        assert isinstance(fields, PlanningFieldConfig)
