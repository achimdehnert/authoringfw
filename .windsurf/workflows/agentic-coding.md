---
description: Agentic Coding Workflow
---

# Agentic Coding

## Governance (bei moderate+): `/governance-check`

## Ausführung
1. Minimale Änderungen, Tests: `test_should_*`
2. `ruff check . --fix && pytest tests/ -q`

## PR
```bash
git checkout -b feat/ISSUE-beschreibung
git commit -m "feat(scope): desc\n\nCloses #ISSUE"
```
