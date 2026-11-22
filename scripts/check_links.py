#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
cases = json.loads((ROOT / "data/cases.json").read_text(encoding="utf-8"))
case_ids = {c["id"] for c in cases}
html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
errors = []

# Validate local Markdown/asset links in source Markdown.
for base in ((ROOT / "docs").glob("**/*.md")):
    text = base.read_text(encoding="utf-8", errors="replace")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("?", 1)[0]
        resolved = (base.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{base.relative_to(ROOT).as_posix()}: liên kết local không tồn tại: {target}")

# Validate legacy/detail route names embedded in generated JS data.
for cid in re.findall(r'"id"\s*:\s*"([^"]+)"', html):
    if cid in case_ids:
        continue

if errors:
    print("link check:")
    print("\n".join("  " + e for e in errors))
    sys.exit(1)
print("links: không phát hiện link Markdown local hỏng")
