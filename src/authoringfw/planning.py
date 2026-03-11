"""Planning phase field configuration per format type.

Defines which fields are shown/required in the project wizard
and planning editor for each content format.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlanningFieldConfig(BaseModel):
    """UI field visibility and labels for the planning phase per format.

    Consumed by:
    - Project wizard (which fields to show on creation)
    - Planning editor (which sections are visible/labeled correctly)
    - LLM prompt selection (which action_code to use)
    """

    premise_label: str = "Prämisse"
    premise_placeholder: str = "Die zentrale Idee in 2-3 Sätzen..."
    show_themes: bool = True
    show_logline: bool = True
    logline_label: str = "Logline"
    logline_placeholder: str = "Wenn [Protagonist] [Herausforderung] begegnet..."
    show_abstract: bool = False
    abstract_label: str = "Abstract"
    abstract_placeholder: str = "Kurzzusammenfassung (150 Wörter)..."
    show_hypothesis: bool = False
    hypothesis_label: str = "Hypothese"
    hypothesis_placeholder: str = "Die zentrale Hypothese dieser Arbeit lautet..."
    show_keywords: bool = False
    show_citation_style: bool = False
    show_field_of_study: bool = False
    show_audience: bool = True
    show_author_style: bool = True
    word_count_default: int = 50000
    planning_action_code: str = "planning_roman"

    def to_dict(self) -> dict:
        """Alias for model_dump() — convenience for Django template context."""
        return self.model_dump()


PLANNING_ROMAN = PlanningFieldConfig(
    premise_label="Prämisse",
    premise_placeholder=(
        "z.B. In einer Welt, in der Magie verboten ist, entdeckt ein junger Schmied, "
        "dass er der letzte einer langen Linie von Magiern ist..."
    ),
    show_themes=True,
    show_logline=True,
    logline_label="Logline",
    logline_placeholder="Wenn [Protagonist] [Herausforderung] begegnet, muss [er/sie] [Handlung], bevor [Konsequenz].",
    show_abstract=False,
    show_hypothesis=False,
    show_keywords=False,
    show_citation_style=False,
    show_field_of_study=False,
    show_audience=True,
    show_author_style=True,
    word_count_default=50000,
    planning_action_code="planning_roman",
)

PLANNING_NONFICTION = PlanningFieldConfig(
    premise_label="Thema & Kernbotschaft",
    premise_placeholder=(
        "Was ist das zentrale Thema und die Kernbotschaft des Buches? "
        "Welches Problem löst es für die Leser?"
    ),
    show_themes=True,
    show_logline=False,
    show_abstract=True,
    abstract_label="Kurzzusammenfassung",
    abstract_placeholder="Worum geht es in diesem Sachbuch? Für wen ist es gedacht?",
    show_hypothesis=False,
    show_keywords=False,
    show_citation_style=False,
    show_field_of_study=True,
    show_audience=True,
    show_author_style=True,
    word_count_default=60000,
    planning_action_code="planning_nonfiction",
)

PLANNING_ACADEMIC = PlanningFieldConfig(
    premise_label="Forschungsfrage & Zielsetzung",
    premise_placeholder=(
        "Was ist deine zentrale Forschungsfrage? "
        "Welches wissenschaftliche Ziel verfolgst du?"
    ),
    show_themes=False,
    show_logline=False,
    show_abstract=True,
    abstract_label="Abstract",
    abstract_placeholder=(
        "Kurzzusammenfassung der Arbeit (ca. 150 Wörter): "
        "Fragestellung, Methode, Ergebnisse, Schlussfolgerung."
    ),
    show_hypothesis=False,
    show_keywords=True,
    show_citation_style=True,
    show_field_of_study=True,
    show_audience=False,
    show_author_style=False,
    word_count_default=80000,
    planning_action_code="planning_academic",
)

PLANNING_SCIENTIFIC = PlanningFieldConfig(
    premise_label="Forschungsfrage & Hypothese",
    premise_placeholder=(
        "Was ist deine Forschungsfrage? "
        "Formuliere eine testbare Hypothese."
    ),
    show_themes=False,
    show_logline=False,
    show_abstract=True,
    abstract_label="Abstract (IMRaD)",
    abstract_placeholder=(
        "Introduction / Methods / Results / Discussion — "
        "Kurzzusammenfassung der Arbeit."
    ),
    show_hypothesis=True,
    hypothesis_label="Nullhypothese",
    hypothesis_placeholder="Die Nullhypothese dieser Studie lautet...",
    show_keywords=True,
    show_citation_style=True,
    show_field_of_study=True,
    show_audience=False,
    show_author_style=False,
    word_count_default=8000,
    planning_action_code="planning_scientific",
)

PLANNING_ESSAY = PlanningFieldConfig(
    premise_label="These / Kernargument",
    premise_placeholder=(
        "Was ist deine Hauptthese? "
        "Welche Position vertrittst du?"
    ),
    show_themes=True,
    show_logline=False,
    show_abstract=False,
    show_hypothesis=False,
    show_keywords=False,
    show_citation_style=False,
    show_field_of_study=False,
    show_audience=True,
    show_author_style=True,
    word_count_default=4000,
    planning_action_code="planning_essay",
)

PLANNING_SERIE = PlanningFieldConfig(
    premise_label="Serienbibel / Prämisse",
    premise_placeholder=(
        "Was ist das übergreifende Thema und die Welt der Serie? "
        "Was verbindet alle Bände?"
    ),
    show_themes=True,
    show_logline=True,
    logline_label="Serien-Logline",
    logline_placeholder="Eine Serie über [Welt], in der [Protagonist] [übergreifendes Ziel] verfolgt.",
    show_abstract=False,
    show_hypothesis=False,
    show_keywords=False,
    show_citation_style=False,
    show_field_of_study=False,
    show_audience=True,
    show_author_style=True,
    word_count_default=80000,
    planning_action_code="planning_roman",
)

PLANNING_SCREENPLAY = PlanningFieldConfig(
    premise_label="Konzept / Logline",
    premise_placeholder=(
        "Worum geht es in deinem Film/deiner Serie? "
        "Was ist der zentrale Konflikt?"
    ),
    show_themes=True,
    show_logline=True,
    logline_label="Logline (1 Satz)",
    logline_placeholder="Wenn [Protagonist] [Auslöser], muss [er/sie] [Handlung], sonst [Einsatz].",
    show_abstract=False,
    show_hypothesis=False,
    show_keywords=False,
    show_citation_style=False,
    show_field_of_study=False,
    show_audience=True,
    show_author_style=False,
    word_count_default=25000,
    planning_action_code="planning_roman",
)

PLANNING_SHORT_STORY = PlanningFieldConfig(
    premise_label="Kernidee",
    premise_placeholder=(
        "Was ist die zentrale Idee deiner Kurzgeschichte? "
        "Welche Emotion oder Erkenntnis soll der Leser mitnehmen?"
    ),
    show_themes=True,
    show_logline=True,
    logline_label="Logline",
    logline_placeholder="Eine Kurzgeschichte über [Protagonist], der/die [Konflikt] erlebt.",
    show_abstract=False,
    show_hypothesis=False,
    show_keywords=False,
    show_citation_style=False,
    show_field_of_study=False,
    show_audience=True,
    show_author_style=True,
    word_count_default=5000,
    planning_action_code="planning_roman",
)

PLANNING_BLOG_POST = PlanningFieldConfig(
    premise_label="Thema & Kernaussage",
    premise_placeholder=(
        "Worüber schreibst du? "
        "Was ist die wichtigste Erkenntnis für den Leser?"
    ),
    show_themes=False,
    show_logline=False,
    show_abstract=True,
    abstract_label="Teaser / Einleitung",
    abstract_placeholder="Die ersten 2-3 Sätze, die den Leser zum Weiterlesen motivieren.",
    show_hypothesis=False,
    show_keywords=True,
    show_citation_style=False,
    show_field_of_study=False,
    show_audience=True,
    show_author_style=True,
    word_count_default=1500,
    planning_action_code="planning_nonfiction",
)

PLANNING_PODCAST_SCRIPT = PlanningFieldConfig(
    premise_label="Folgenthema",
    premise_placeholder=(
        "Was ist das Thema dieser Episode? "
        "Welche Frage wird beantwortet?"
    ),
    show_themes=False,
    show_logline=False,
    show_abstract=True,
    abstract_label="Show Notes",
    abstract_placeholder="Stichpunkte für die Episodenbeschreibung und Kapitelmarken.",
    show_hypothesis=False,
    show_keywords=True,
    show_citation_style=False,
    show_field_of_study=False,
    show_audience=True,
    show_author_style=False,
    word_count_default=3000,
    planning_action_code="planning_nonfiction",
)

PLANNING_REGISTRY: dict[str, PlanningFieldConfig] = {
    "roman": PLANNING_ROMAN,
    "novel": PLANNING_ROMAN,
    "nonfiction": PLANNING_NONFICTION,
    "academic": PLANNING_ACADEMIC,
    "scientific": PLANNING_SCIENTIFIC,
    "essay": PLANNING_ESSAY,
    "serie": PLANNING_SERIE,
    "screenplay": PLANNING_SCREENPLAY,
    "short_story": PLANNING_SHORT_STORY,
    "blog_post": PLANNING_BLOG_POST,
    "podcast_script": PLANNING_PODCAST_SCRIPT,
}


def get_planning_config(format_type: str) -> PlanningFieldConfig:
    """Get the PlanningFieldConfig for a given format type.

    Falls back to PLANNING_ROMAN for unknown types.

    Args:
        format_type: Format slug, e.g. 'roman', 'academic', 'scientific'.

    Returns:
        PlanningFieldConfig with UI labels and field visibility flags.
    """
    return PLANNING_REGISTRY.get(format_type, PLANNING_ROMAN)
