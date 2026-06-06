"""Tests for authoringfw.templates — story prompt templates (Issue #13)."""

from authoringfw.templates import (
    CHAPTER_TEMPLATE,
    InMemoryRegistry,
    LLMConfig,
    OUTLINE_TEMPLATE,
    PromptTemplateSpec,
    PromptVariable,
    SCENE_ENRICHMENT_TEMPLATE,
    SCENE_OUTLINE_TEMPLATE,
    STORYLINE_TEMPLATE,
    VariableType,
    story_registry,
)


class TestPromptTemplateSpec:
    """Test dataclass definitions."""

    def test_should_create_default_spec(self):
        spec = PromptTemplateSpec()
        assert spec.template_key == ""
        assert spec.llm_config.temperature == 0.7

    def test_should_create_variable(self):
        v = PromptVariable(name="genre", var_type=VariableType.STRING, required=True)
        assert v.name == "genre"
        assert v.var_type == VariableType.STRING
        assert v.required is True

    def test_should_create_llm_config(self):
        cfg = LLMConfig(tier="premium", temperature=0.5, max_tokens=4000)
        assert cfg.tier == "premium"
        assert cfg.max_tokens == 4000


class TestTemplateConstants:
    """Test the 5 migrated template constants."""

    def test_should_have_outline_template(self):
        assert OUTLINE_TEMPLATE.template_key == "story.outline.v1"
        assert OUTLINE_TEMPLATE.category == "outline"
        assert len(OUTLINE_TEMPLATE.variables) == 2

    def test_should_have_chapter_template(self):
        assert CHAPTER_TEMPLATE.template_key == "story.chapter.v2"
        assert CHAPTER_TEMPLATE.category == "chapter"
        assert CHAPTER_TEMPLATE.llm_config.max_tokens == 4000
        assert len(CHAPTER_TEMPLATE.variables) >= 10

    def test_should_have_scene_outline_template(self):
        assert SCENE_OUTLINE_TEMPLATE.template_key == "story.scene_outline.v1"
        assert SCENE_OUTLINE_TEMPLATE.category == "outline"
        assert len(SCENE_OUTLINE_TEMPLATE.variables) >= 5

    def test_should_have_scene_enrichment_template(self):
        assert SCENE_ENRICHMENT_TEMPLATE.template_key == "story.scene_enrich.v1"
        assert SCENE_ENRICHMENT_TEMPLATE.category == "scene"
        assert len(SCENE_ENRICHMENT_TEMPLATE.variables) >= 8

    def test_should_have_storyline_template(self):
        assert STORYLINE_TEMPLATE.template_key == "story.storyline.v1"
        assert STORYLINE_TEMPLATE.category == "storyline"
        assert "adr-025" in STORYLINE_TEMPLATE.tags

    def test_should_all_have_system_and_user_prompts(self):
        for tmpl in [
            OUTLINE_TEMPLATE,
            CHAPTER_TEMPLATE,
            SCENE_OUTLINE_TEMPLATE,
            SCENE_ENRICHMENT_TEMPLATE,
            STORYLINE_TEMPLATE,
        ]:
            assert tmpl.system_prompt, f"{tmpl.template_key} missing system_prompt"
            assert tmpl.user_prompt, f"{tmpl.template_key} missing user_prompt"

    def test_should_all_have_domain_code_story(self):
        for tmpl in [
            OUTLINE_TEMPLATE,
            CHAPTER_TEMPLATE,
            SCENE_OUTLINE_TEMPLATE,
            SCENE_ENRICHMENT_TEMPLATE,
            STORYLINE_TEMPLATE,
        ]:
            assert tmpl.domain_code == "story"


class TestInMemoryRegistry:
    """Test template registry."""

    def test_should_register_and_retrieve(self):
        reg = InMemoryRegistry()
        spec = PromptTemplateSpec(template_key="test.v1", name="Test")
        reg.register(spec)
        assert reg.get("test.v1") is spec

    def test_should_return_none_for_missing(self):
        reg = InMemoryRegistry()
        assert reg.get("nonexistent") is None

    def test_should_have_all_templates_in_story_registry(self):
        assert story_registry.get("story.outline.v1") is OUTLINE_TEMPLATE
        assert story_registry.get("story.chapter.v2") is CHAPTER_TEMPLATE
        assert story_registry.get("story.scene_outline.v1") is SCENE_OUTLINE_TEMPLATE
        assert story_registry.get("story.scene_enrich.v1") is SCENE_ENRICHMENT_TEMPLATE
        assert story_registry.get("story.storyline.v1") is STORYLINE_TEMPLATE


class TestTopLevelImport:
    """Test that templates are accessible from authoringfw top-level."""

    def test_should_import_from_authoringfw_directly(self):
        from authoringfw import (
            CHAPTER_TEMPLATE as CT,
            OUTLINE_TEMPLATE as OT,
            SCENE_ENRICHMENT_TEMPLATE as SET,
            SCENE_OUTLINE_TEMPLATE as SOT,
            STORYLINE_TEMPLATE as ST,
            render_story_template,
        )

        assert OT.template_key == "story.outline.v1"
        assert CT.template_key == "story.chapter.v2"
        assert SOT.template_key == "story.scene_outline.v1"
        assert SET.template_key == "story.scene_enrich.v1"
        assert ST.template_key == "story.storyline.v1"
        assert callable(render_story_template)
