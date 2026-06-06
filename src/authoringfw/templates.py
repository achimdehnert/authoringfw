"""
Story Generation Prompt Templates — shared across travel-beat, writing-hub.

Templates for outline, chapter, scene, and storyline generation.
Rendering powered by iil-promptfw when available, otherwise plain Jinja2.

Migrated from travel-beat/apps/stories/prompts/ (Issue #13).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VariableType(Enum):
    STRING = "string"
    INTEGER = "integer"


@dataclass
class PromptVariable:
    name: str
    var_type: VariableType = VariableType.STRING
    required: bool = False
    default: Any = ""


@dataclass
class LLMConfig:
    tier: str = "standard"
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class PromptTemplateSpec:
    """Prompt template spec — backed by iil-promptfw for rendering."""

    template_key: str = ""
    domain_code: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    user_prompt_template: str = ""
    variables: list = field(default_factory=list)
    llm_config: LLMConfig = field(default_factory=LLMConfig)
    tags: list = field(default_factory=list)


class InMemoryRegistry:
    def __init__(self):
        self._templates: dict = {}

    def register(self, spec):
        self._templates[spec.template_key] = spec

    save = register

    def get(self, key: str):
        return self._templates.get(key)


def render_story_template(
    spec: PromptTemplateSpec,
    variables: dict,
) -> tuple[str, str]:
    """Render system + user prompts via promptfw Jinja2 engine.

    Returns (system_prompt, user_prompt).
    Missing variables default to empty string.

    Requires iil-promptfw: ``pip install iil-promptfw``
    """
    try:
        from promptfw import PromptRenderer, PromptTemplate, TemplateLayer

        renderer = PromptRenderer()
        merged: dict[str, Any] = {}
        for v in spec.variables:
            if isinstance(v, PromptVariable):
                merged[v.name] = v.default if v.default != "" else ""
            else:
                merged[str(v)] = ""
        merged.update(variables)

        var_names = [v.name if isinstance(v, PromptVariable) else str(v) for v in spec.variables]
        sys_tmpl = PromptTemplate(
            id=f"{spec.template_key}.system",
            layer=TemplateLayer.SYSTEM,
            template=spec.system_prompt,
            variables=var_names,
        )
        tpl = spec.user_prompt or spec.user_prompt_template
        task_tmpl = PromptTemplate(
            id=f"{spec.template_key}.task",
            layer=TemplateLayer.TASK,
            template=tpl,
            variables=var_names,
        )
        rendered = renderer.render_stack([sys_tmpl, task_tmpl], merged)
        return rendered.system, rendered.user
    except ImportError:
        raise ImportError(
            "iil-promptfw is required for template rendering. "
            "Install with: pip install iil-promptfw"
        )


# =============================================================================
# Registry
# =============================================================================

story_registry = InMemoryRegistry()


# =============================================================================
# OUTLINE GENERATION TEMPLATE
# =============================================================================

OUTLINE_TEMPLATE = PromptTemplateSpec(
    template_key="story.outline.v1",
    domain_code="story",
    name="Story Outline Generator",
    description="Generates a structured story outline from trip data",
    category="outline",
    system_prompt="""Du bist ein erfahrener Geschichtenerzähler und Reiseschriftsteller.
Erstelle eine detaillierte Outline für eine Reisegeschichte basierend auf den gegebenen Informationen.

Die Outline sollte folgende JSON-Struktur haben:
{
    "title": "Titel der Geschichte",
    "genre": "romantic_suspense",
    "chapters": [
        {
            "number": 1,
            "title": "Kapiteltitel",
            "act": "act_1",
            "beat": "hook",
            "pacing": "atmospheric",
            "target_words": 2500,
            "summary": "Kurze Zusammenfassung des Kapitels",
            "key_events": ["Event 1", "Event 2"]
        }
    ]
}""",
    user_prompt="""Erstelle eine Outline für folgende Reise:

{{ input_context }}
{{ beats_info }}

Erstelle eine spannende Geschichte mit einem Kapitel pro Reise-Stopp.
Kurze Aufenthalte (1 Nacht) am selben Ort können in einem Kapitel zusammengefasst werden.
Langstrecken-Transporte (Flüge >4h) verdienen ein eigenes Kapitel.
JEDER Stopp der Reise MUSS in mindestens einem Kapitel vorkommen.
Antworte NUR mit dem JSON-Objekt, keine weiteren Erklärungen.""",
    variables=[
        PromptVariable(name="input_context", var_type=VariableType.STRING, required=True),
        PromptVariable(name="beats_info", var_type=VariableType.STRING, required=False, default=""),
    ],
    llm_config=LLMConfig(
        tier="standard",
        temperature=0.7,
        max_tokens=2000,
    ),
    tags=["story", "outline", "travel"],
)


# =============================================================================
# CHAPTER GENERATION TEMPLATE
# =============================================================================

CHAPTER_TEMPLATE = PromptTemplateSpec(
    template_key="story.chapter.v2",
    domain_code="story",
    name="Story Chapter Generator",
    description="Generates a full chapter from outline and context",
    category="chapter",
    system_prompt="""Du bist ein erfahrener Romanautor, spezialisiert auf {{ genre }}.
Schreibe ein ausführliches Kapitel für die Geschichte \"{{ story_title }}\".

WICHTIG - Schreibstil und Umfang:
- MINDESTENS {{ target_words }} Wörter - dies ist eine HARTE Anforderung
- Verwende ausführliche, detaillierte Beschreibungen der Umgebung und Sinneseindrücke
- Entwickle Dialoge mit mindestens 10-15 Gesprächswechseln pro Szene
- Füge innere Monologe und Gedanken der Charaktere ein
- Beschreibe Emotionen, Körpersprache und nonverbale Kommunikation
- Integriere die Reisedetails (Orte, Essen, Kultur) ausführlich in die Handlung
- Schreibe auf Deutsch in literarischem Stil

KRITISCH - VARIANZ DER ERÖFFNUNGEN:
Beginne NIEMALS mit Aufwachen, Sonnenstrahlen durch Vorhänge oder dem Morgengrauen,
es sei denn, der Beat verlangt es ausdrücklich. Wähle stattdessen eine der
folgenden Eröffnungstechniken passend zum Story-Beat:
- \"hook\" / \"catalyst\": Mitten in der Handlung (medias in res), ein Geräusch, ein Fund
- \"fun_and_games\": Sensorischer Einstieg (Geruch, Geschmack, Geräusch am Ort)
- \"midpoint\": Dialog-Eröffnung, eine überraschende Aussage oder Frage
- \"all_is_lost\" / \"dark_night\": Innerer Monolog, Rückblende, emotionaler Zustand
- \"finale\": Action-Einstieg, eine Entscheidung, ein Aufbruch
- \"b_story\": Perspektivwechsel, Beobachtung einer anderen Person
- \"setup\" / \"opening_image\": Kontrast-Beschreibung (Erwartung vs. Realität)
- \"final_image\": Spiegelung des Anfangs, aber verändert
- \"break_into_two\" / \"break_into_three\": Reise-/Transportszene, Schwellenübergang
Jedes Kapitel MUSS einen anderen Einstieg als das vorherige verwenden.

Struktur pro Kapitel:
1. Eröffnung passend zum Beat (~500 Wörter) - VARIIERE den Einstieg!
2. Haupthandlung mit Dialogen (~1500 Wörter)
3. Abschlussszene mit Cliffhanger oder Übergang (~500 Wörter)""",
    user_prompt="""Schreibe Kapitel {{ chapter_number }}: {{ chapter_title }}

Story-Beat: {{ beat }}
Beat-Beschreibung: {{ beat_description }}
Pacing: {{ pacing }}
Akt: {{ act }}

Zusammenfassung dieses Kapitels: {{ summary }}

Wichtige Ereignisse:
{{ key_events }}

{{ previous_summary }}

Kontext:
{{ input_context }}

WICHTIG: Schreibe ein VOLLSTÄNDIGES, AUSFÜHRLICHES Kapitel mit MINDESTENS {{ target_words }} Wörtern.
Wähle einen Eröffnungsstil passend zum Beat \"{{ beat }}\" — NICHT Aufwachen/Sonnenstrahlen.
Das Kapitel muss eigenständig lesbar sein und darf NICHT abgekürzt werden.""",
    variables=[
        PromptVariable(name="genre", var_type=VariableType.STRING, required=True),
        PromptVariable(name="story_title", var_type=VariableType.STRING, required=True),
        PromptVariable(name="chapter_number", var_type=VariableType.INTEGER, required=True),
        PromptVariable(name="chapter_title", var_type=VariableType.STRING, required=True),
        PromptVariable(
            name="beat",
            var_type=VariableType.STRING,
            required=False,
            default="continuation",
        ),
        PromptVariable(
            name="beat_description",
            var_type=VariableType.STRING,
            required=False,
            default="Fortführung der Handlung",
        ),
        PromptVariable(
            name="pacing",
            var_type=VariableType.STRING,
            required=False,
            default="atmospheric",
        ),
        PromptVariable(name="act", var_type=VariableType.STRING, required=False, default=""),
        PromptVariable(name="summary", var_type=VariableType.STRING, required=False, default=""),
        PromptVariable(name="key_events", var_type=VariableType.STRING, required=False, default=""),
        PromptVariable(
            name="previous_summary",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(name="input_context", var_type=VariableType.STRING, required=True),
        PromptVariable(
            name="target_words",
            var_type=VariableType.INTEGER,
            required=False,
            default=2500,
        ),
    ],
    llm_config=LLMConfig(
        tier="standard",
        temperature=0.7,
        max_tokens=4000,
    ),
    tags=["story", "chapter", "travel"],
)


# =============================================================================
# SCENE OUTLINE TEMPLATE (for LLM-based outline enrichment)
# =============================================================================

SCENE_OUTLINE_TEMPLATE = PromptTemplateSpec(
    template_key="story.scene_outline.v1",
    domain_code="story",
    name="Scene-Based Outline Enrichment",
    description=(
        "Enriches a scene-based outline with logline, synopsis, themes, conflict, and character arcs"
        " using LLM"
    ),
    category="outline",
    system_prompt="""Du bist ein erfahrener Story-Architekt.
Deine Aufgabe: Eine strukturierte Reise-Outline mit Scenes anreichern.

Antworte IMMER als JSON:
{
    "logline": "Ein Satz, der die ganze Geschichte zusammenfasst",
    "synopsis": "3-5 Sätze Zusammenfassung",
    "themes": ["Thema1", "Thema2"],
    "central_conflict": "Der zentrale Konflikt",
    "protagonist_arc": "Entwicklung des Protagonisten",
    "scenes": [
        {
            "order": 1,
            "title": "Szenen-Titel",
            "summary": "Was passiert (2-3 Sätze)",
            "emotional_state": "Emotionaler Zustand",
            "hook": "Übergang zur nächsten Szene"
        }
    ]
}""",
    user_prompt="""Genre: {{ genre }}
Protagonist: {{ protagonist_name }} ({{ protagonist_gender }})
Reiseroute: {{ route_summary }}

{{ companion_info }}

Story-Struktur: {{ framework_name }}
Anzahl Szenen: {{ num_scenes }}

Szenen-Grundgerüst:
{{ scenes_skeleton }}

{{ preferences }}

Reichere diese Outline an mit Logline, Synopsis, Themen,
zentralem Konflikt, Protagonisten-Arc und detaillierten
Szenen-Beschreibungen. Jede Szene braucht einen konkreten
Summary und einen Hook zur nächsten Szene.""",
    variables=[
        PromptVariable(
            name="genre",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="protagonist_name",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="protagonist_gender",
            var_type=VariableType.STRING,
            required=False,
            default="unbekannt",
        ),
        PromptVariable(
            name="route_summary",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="companion_info",
            var_type=VariableType.STRING,
            required=False,
            default="Reist alleine.",
        ),
        PromptVariable(
            name="framework_name",
            var_type=VariableType.STRING,
            required=False,
            default="Save the Cat",
        ),
        PromptVariable(
            name="num_scenes",
            var_type=VariableType.INTEGER,
            required=True,
        ),
        PromptVariable(
            name="scenes_skeleton",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="preferences",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
    ],
    llm_config=LLMConfig(
        tier="standard",
        temperature=0.7,
        max_tokens=3000,
    ),
    tags=["story", "outline", "scene", "enrichment"],
)


# =============================================================================
# SCENE ENRICHMENT TEMPLATE (for individual scene detail)
# =============================================================================

SCENE_ENRICHMENT_TEMPLATE = PromptTemplateSpec(
    template_key="story.scene_enrich.v1",
    domain_code="story",
    name="Single Scene Enrichment",
    description="Generates detailed content plan for a single scene",
    category="scene",
    system_prompt="""Du bist ein Szenenplaner für Reisegeschichten.
Erstelle einen detaillierten Plan für eine einzelne Szene.

Antworte als JSON:
{
    "title": "Szenen-Titel",
    "summary": "Detaillierte Beschreibung (3-5 Sätze)",
    "key_events": ["Event 1", "Event 2"],
    "sensory_details": ["Detail 1", "Detail 2"],
    "dialogue_hooks": ["Dialogansatz 1"],
    "emotional_arc": "Emotionaler Verlauf in der Szene",
    "hook": "Übergang/Cliffhanger zur nächsten Szene"
}""",
    user_prompt="""Genre: {{ genre }}
Beat: {{ beat }} ({{ beat_description }})
Akt: {{ act }}

Ort: {{ location_city }}, {{ location_country }}
Datum: {{ scene_date }}
Tageszeit: {{ time_of_day }}

Anwesende Charaktere: {{ characters_present }}
Spannungslevel: {{ tension_level }}

{{ transport_info }}
{{ previous_scene_summary }}

Erstelle einen detaillierten Szenenplan mit konkreten
Orts-Details aus {{ location_city }}.""",
    variables=[
        PromptVariable(
            name="genre",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="beat",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="beat_description",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="act",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="location_city",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="location_country",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="scene_date",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="time_of_day",
            var_type=VariableType.STRING,
            required=False,
            default="afternoon",
        ),
        PromptVariable(
            name="characters_present",
            var_type=VariableType.STRING,
            required=False,
            default="Protagonist",
        ),
        PromptVariable(
            name="tension_level",
            var_type=VariableType.STRING,
            required=False,
            default="medium",
        ),
        PromptVariable(
            name="transport_info",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="previous_scene_summary",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
    ],
    llm_config=LLMConfig(
        tier="standard",
        temperature=0.7,
        max_tokens=1500,
    ),
    tags=["story", "scene", "enrichment", "detail"],
)


# =============================================================================
# STORYLINE GENERATION TEMPLATE (ADR-025 v2 — Phase 1)
# =============================================================================

STORYLINE_TEMPLATE = PromptTemplateSpec(
    template_key="story.storyline.v1",
    domain_code="story",
    name="Storyline Generator (Phase 1)",
    description="Generates a global storyline across all trip stops",
    category="storyline",
    system_prompt="""Du bist ein erfahrener Romanautor und Reiseschriftsteller.
Erstelle einen uebergreifenden Handlungsbogen fuer eine Reisegeschichte.

Genre: {{ genre }}
Spice Level: {{ spice_level }}
Ending: {{ ending_type }}
Erzaehlperspektive: {{ narrative_voice }}
{{ focus_instruction }}
{{ premise }}
{{ atmosphere }}
{{ themes }}

Antworte NUR mit einem JSON-Objekt in folgender Struktur:
{
    "theme": "Uebergreifendes Thema",
    "protagonist_arc": "Entwicklung des Protagonisten",
    "antagonist_concept": "Antagonist oder Hindernis",
    "tone_progression": "leicht -> spannend -> kathartisch",
    "plot_threads": [
        {
            "name": "Thread-Name",
            "description": "1-2 Saetze",
            "start_stop_id": 42,
            "climax_stop_id": 55,
            "resolution_stop_id": 60
        }
    ],
    "stop_roles": [
        {
            "stop_id": 42,
            "narrative_role": "Aufbruch, alte Welt verlassen",
            "emotional_tone": "melancholisch",
            "recommended_chapters": 1
        }
    ],
    "transport_moments": [
        {
            "transport_id": 17,
            "narrative_use": "Innerer Monolog ueber Vergangenheit"
        }
    ]
}

KRITISCHE REGELN:
1. Jeder Stopp MUSS in stop_roles vorkommen. Verwende die exakten stop_id-Werte.
2. recommended_chapters als Ganzzahl (0-5). Summe zwischen 8 und 30.
3. Mindestens 1, maximal 5 plot_threads.
4. transport_moments nur fuer Langstrecken (>4h) oder narrativ wichtige Reisen.
5. Antworte NUR mit dem JSON-Objekt.""",
    user_prompt="""Erstelle einen Handlungsbogen fuer folgende Reise:

{{ input_context }}

STOPPS (verwende diese exakten stop_id-Werte):
{{ stops_info }}

TRANSPORTE (verwende diese exakten transport_id-Werte):
{{ transports_info }}

{{ poi_context }}""",
    variables=[
        PromptVariable(
            name="input_context",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="stops_info",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="transports_info",
            var_type=VariableType.STRING,
            required=True,
        ),
        PromptVariable(
            name="genre",
            var_type=VariableType.STRING,
            required=False,
            default="Romantic Suspense",
        ),
        PromptVariable(
            name="spice_level",
            var_type=VariableType.STRING,
            required=False,
            default="Mild",
        ),
        PromptVariable(
            name="ending_type",
            var_type=VariableType.STRING,
            required=False,
            default="Happy End",
        ),
        PromptVariable(
            name="focus_instruction",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="poi_context",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="premise",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="atmosphere",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="themes",
            var_type=VariableType.STRING,
            required=False,
            default="",
        ),
        PromptVariable(
            name="narrative_voice",
            var_type=VariableType.STRING,
            required=False,
            default="Dritte Person",
        ),
    ],
    llm_config=LLMConfig(
        tier="standard",
        temperature=0.7,
        max_tokens=3000,
    ),
    tags=["story", "storyline", "travel", "adr-025"],
)


# =============================================================================
# Auto-register on import
# =============================================================================


def register_templates():
    """Register all story templates in the registry."""
    story_registry.save(OUTLINE_TEMPLATE)
    story_registry.save(CHAPTER_TEMPLATE)
    story_registry.save(SCENE_OUTLINE_TEMPLATE)
    story_registry.save(SCENE_ENRICHMENT_TEMPLATE)
    story_registry.save(STORYLINE_TEMPLATE)


register_templates()


__all__ = [
    "CHAPTER_TEMPLATE",
    "InMemoryRegistry",
    "LLMConfig",
    "OUTLINE_TEMPLATE",
    "PromptTemplateSpec",
    "PromptVariable",
    "SCENE_ENRICHMENT_TEMPLATE",
    "SCENE_OUTLINE_TEMPLATE",
    "STORYLINE_TEMPLATE",
    "VariableType",
    "render_story_template",
    "story_registry",
]
