---
description: Quality Gate
---

# Repo Health Check

```bash
python3 -c "
import tomllib
d = tomllib.load(open('pyproject.toml','rb'))['project']
print('MISSING:', [f for f in ['name','version','description','readme','authors'] if not d.get(f)] or 'none')
"
python3 ~/github/platform/tools/repo_health_check.py --profile python-package --path .
```
