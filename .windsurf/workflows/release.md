---
description: Publish iil-authoringfw to PyPI
---

# Release — PyPI Publish

## Build + Publish

```bash
bash ~/github/platform/scripts/publish-package.sh ~/github/authoringfw
```

## Test-Upload zuerst

```bash
bash ~/github/platform/scripts/publish-package.sh ~/github/authoringfw --test
```

## Verify

```bash
pip index versions iil-authoringfw 2>/dev/null | head -3
```
