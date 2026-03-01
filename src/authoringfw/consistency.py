"""
ConsistencyChecker — verify generated text against CharacterProfile and WorldContext.

New in 0.2.0.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from authoringfw.schema.character import CharacterProfile
from authoringfw.schema.world import WorldContext


@dataclass
class ConsistencyIssue:
    """A single detected inconsistency."""

    severity: str
    category: str
    message: str
    suggestion: str = ""


@dataclass
class ConsistencyReport:
    """Full consistency check result."""

    issues: list[ConsistencyIssue] = field(default_factory=list)
    score: float = 1.0

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def warnings(self) -> list[ConsistencyIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def errors(self) -> list[ConsistencyIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def summary(self) -> str:
        if not self.issues:
            return "✅ No consistency issues found."
        lines = [f"Score: {self.score:.0%} — {len(self.errors)} errors, {len(self.warnings)} warnings"]
        for issue in self.issues:
            prefix = "❌" if issue.severity == "error" else "⚠️"
            lines.append(f"{prefix} [{issue.category}] {issue.message}")
            if issue.suggestion:
                lines.append(f"   → {issue.suggestion}")
        return "\n".join(lines)


class ConsistencyChecker:
    """
    Checks generated text for consistency with CharacterProfiles and WorldContext.

    Rule-based (fast, no LLM needed). For deeper semantic checks use
    the async check_with_llm() method which requires aifw.

    Usage::

        checker = ConsistencyChecker()
        checker.add_character(alice)
        checker.set_world(world)

        report = checker.check(generated_text)
        if not report.passed:
            print(report.summary())
    """

    def __init__(self) -> None:
        self._characters: list[CharacterProfile] = []
        self._world: WorldContext | None = None

    def add_character(self, character: CharacterProfile) -> None:
        self._characters.append(character)

    def set_world(self, world: WorldContext) -> None:
        self._world = world

    def check(self, text: str) -> ConsistencyReport:
        """Run all rule-based consistency checks."""
        issues: list[ConsistencyIssue] = []
        issues.extend(self._check_character_names(text))
        issues.extend(self._check_world_rules(text))
        issues.extend(self._check_forbidden_terms(text))
        score = max(0.0, 1.0 - (len(issues) * 0.1))
        return ConsistencyReport(issues=issues, score=score)

    def _check_character_names(self, text: str) -> list[ConsistencyIssue]:
        """Warn if known character names appear with wrong capitalization."""
        issues = []
        for char in self._characters:
            wrong_caps = [
                m.group() for m in re.finditer(
                    re.escape(char.name.lower()), text
                )
                if m.group() != char.name and m.group().lower() == char.name.lower()
            ]
            if wrong_caps:
                issues.append(ConsistencyIssue(
                    severity="warning",
                    category="character_name",
                    message=f"Name '{char.name}' appears with wrong capitalization: {set(wrong_caps)}",
                    suggestion=f"Always use '{char.name}' (exact casing).",
                ))
        return issues

    def _check_world_rules(self, text: str) -> list[ConsistencyIssue]:
        """Warn if text seems to contradict explicit world rules."""
        if not self._world:
            return []
        issues = []
        for rule in self._world.world_rules:
            if len(rule) < 10:
                continue
            key_phrase = rule.split()[0:4]
            negated = f"no {' '.join(key_phrase[:2]).lower()}"
            if negated in text.lower():
                issues.append(ConsistencyIssue(
                    severity="warning",
                    category="world_rule",
                    message=f"Text may contradict world rule: '{rule}'",
                    suggestion="Review the passage against world rules.",
                ))
        return issues

    def _check_forbidden_terms(self, text: str) -> list[ConsistencyIssue]:
        """Error if anachronistic terms appear (configurable)."""
        issues = []
        if self._world and self._world.time_period:
            period = self._world.time_period.lower()
            if any(p in period for p in ("medieval", "fantasy", "ancient")):
                modern_terms = ["smartphone", "internet", "computer", "email", "twitter"]
                found = [t for t in modern_terms if t in text.lower()]
                if found:
                    issues.append(ConsistencyIssue(
                        severity="error",
                        category="anachronism",
                        message=f"Anachronistic terms found in {period} setting: {found}",
                        suggestion="Remove or replace modern terms.",
                    ))
        return issues

    async def check_with_llm(
        self,
        text: str,
        action_code: str = "consistency_check",
        llm_completion_fn=None,
    ) -> ConsistencyReport:
        """
        Deep semantic consistency check via LLM (requires aifw or custom fn).

        Combines rule-based check with LLM analysis for subtle issues.
        """
        base_report = self.check(text)

        character_context = "\n".join(
            c.to_context_string() for c in self._characters
        )
        world_context = self._world.to_context_string() if self._world else ""

        prompt = (
            "Check the following text for consistency issues against the provided characters "
            "and world context. Return a JSON array of objects with keys: "
            "severity (error|warning), category (string), message (string), suggestion (string).\n\n"
            f"Characters:\n{character_context}\n\n"
            f"World:\n{world_context}\n\n"
            f"Text to check:\n{text[:4000]}\n\n"
            "Return ONLY the JSON array, no explanation."
        )
        messages = [{"role": "user", "content": prompt}]

        if llm_completion_fn is None:
            try:
                from aifw.service import completion as aifw_completion
                llm_completion_fn = aifw_completion
            except ImportError as e:
                raise ImportError(
                    "aifw is required for check_with_llm(). Install with: pip install aifw"
                ) from e

        import json
        result = await llm_completion_fn(action_code, messages)
        if result.success:
            try:
                content = result.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                llm_issues = json.loads(content.strip())
                for item in llm_issues:
                    base_report.issues.append(ConsistencyIssue(**item))
            except Exception:
                pass

        base_report.score = max(0.0, 1.0 - len(base_report.issues) * 0.1)
        return base_report
