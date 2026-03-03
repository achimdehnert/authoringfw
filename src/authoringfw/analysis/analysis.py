"""
StyleAnalysisOrchestrator + PlotAnalysisOrchestrator.

action_codes: 'style_analysis', 'plot_analysis'

Both use AnalysisTask as input and return AnalysisResult.
The score field is populated when output_format='score'.
"""

from __future__ import annotations

import re
from typing import Any

from authoringfw.base import BaseContentOrchestrator
from authoringfw.types import ContentTask
from authoringfw.analysis.types import AnalysisResult, AnalysisTask


class StyleAnalysisOrchestrator(BaseContentOrchestrator):
    """
    Analyses style, tone, POV consistency, and prose quality.

    action_code: 'style_analysis'

    Usage::

        result = StyleAnalysisOrchestrator().execute(AnalysisTask(
            action_code="style_analysis",
            source_text=chapter.content,
            output_format="structured",
        ))
        print(result.content)  # Full analysis
        print(result.findings)  # Key bullet points
    """

    action_code = "style_analysis"

    def _build_messages(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        source = self._get_source(task)
        focus = self._get_focus(task)
        fmt = self._get_format(task)

        system_parts = [
            "Du bist ein Lektor und Stilanalyst. Analysiere den folgenden Text auf:",
            "- Stilkonsistenz (Ton, POV, Tempus)",
            "- Sprachliche Qualität (Wortwahl, Satzbau, Rhythmus)",
            "- Stärken und Verbesserungsvorschläge",
        ]
        if focus:
            system_parts.append(f"Fokus besonders auf: {focus}")
        if fmt == "score":
            system_parts.append(
                "Gib am Ende eine Gesamtbewertung als Dezimalzahl von 0.0 bis 1.0 "
                "in der Form: SCORE: 0.75"
            )
        elif fmt == "structured":
            system_parts.append("Strukturiere die Analyse mit klaren Abschnitten.")

        return [
            {"role": "system", "content": "\n".join(system_parts)},
            {"role": "user", "content": source[:8000]},
        ]

    def _map_result(
        self,
        llm_result: Any,
        quality_level: int | None,
        task: ContentTask,
    ) -> AnalysisResult:
        content = llm_result.content if llm_result.success else ""
        score = self._extract_score(content)
        findings = self._extract_findings(content)
        return AnalysisResult(
            content=content,
            action_code=self.action_code,
            quality_level=quality_level,
            model=getattr(llm_result, "model", ""),
            input_tokens=getattr(llm_result, "input_tokens", 0),
            output_tokens=getattr(llm_result, "output_tokens", 0),
            latency_ms=getattr(llm_result, "latency_ms", 0),
            success=getattr(llm_result, "success", True),
            metadata=task.metadata if isinstance(task, AnalysisTask) else {},
            score=score,
            findings=findings,
        )

    def _extract_score(self, content: str) -> float | None:
        match = re.search(r"SCORE:\s*([0-9]+\.?[0-9]*)", content)
        if match:
            try:
                return min(1.0, max(0.0, float(match.group(1))))
            except ValueError:
                return None
        return None

    def _extract_findings(self, content: str) -> list[str]:
        lines = content.splitlines()
        findings = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("- ", "• ", "* ")) and len(stripped) > 5:
                findings.append(stripped.lstrip("-•* ").strip())
        return findings[:10]

    def _get_source(self, task: ContentTask) -> str:
        if isinstance(task, AnalysisTask):
            return task.source_text
        return task.prompt_variables.get("source_text", "")

    def _get_focus(self, task: ContentTask) -> str:
        if isinstance(task, AnalysisTask):
            return task.analysis_focus
        return task.prompt_variables.get("analysis_focus", "")

    def _get_format(self, task: ContentTask) -> str:
        if isinstance(task, AnalysisTask):
            return task.output_format
        return task.prompt_variables.get("output_format", "structured")


class PlotAnalysisOrchestrator(BaseContentOrchestrator):
    """
    Analyses plot structure, pacing, character arcs, and narrative tension.

    action_code: 'plot_analysis'
    """

    action_code = "plot_analysis"

    def _build_messages(
        self,
        task: ContentTask,
    ) -> list[dict[str, str]]:
        source = task.source_text if isinstance(task, AnalysisTask) else task.prompt_variables.get("source_text", "")
        focus = task.analysis_focus if isinstance(task, AnalysisTask) else task.prompt_variables.get("analysis_focus", "")

        system_parts = [
            "Du bist ein Dramaturg und Story-Analyst. Analysiere die Plotstruktur:",
            "- Spannungskurve und Pacing",
            "- Charakterentwicklung und Arcs",
            "- Wendepunkte und dramatische Wirkung",
            "- Kohärenz und Plausibilität",
        ]
        if focus:
            system_parts.append(f"Fokus: {focus}")

        return [
            {"role": "system", "content": "\n".join(system_parts)},
            {"role": "user", "content": source[:8000]},
        ]

    def _map_result(
        self,
        llm_result: Any,
        quality_level: int | None,
        task: ContentTask,
    ) -> AnalysisResult:
        content = llm_result.content if llm_result.success else ""
        findings = [
            line.strip().lstrip("-•* ").strip()
            for line in content.splitlines()
            if line.strip().startswith(("-", "•", "*")) and len(line.strip()) > 5
        ][:10]
        return AnalysisResult(
            content=content,
            action_code=self.action_code,
            quality_level=quality_level,
            model=getattr(llm_result, "model", ""),
            input_tokens=getattr(llm_result, "input_tokens", 0),
            output_tokens=getattr(llm_result, "output_tokens", 0),
            latency_ms=getattr(llm_result, "latency_ms", 0),
            success=getattr(llm_result, "success", True),
            metadata=task.metadata if isinstance(task, AnalysisTask) else {},
            findings=findings[:10],
        )
