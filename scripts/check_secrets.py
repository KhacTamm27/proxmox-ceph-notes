#!/usr/bin/env python3
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
IGNORE = ROOT / ".secretsignore"
ignored = set()
if IGNORE.exists():
    ignored = {line.strip().replace("\\", "/") for line in IGNORE.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")}

secret_patterns = [
    re.compile(r"AKIA[0-9A-Z]{16}", re.I),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(r"(secret[_ -]?key|password|passwd|token)\s*[:=]\s*[^\s\"']{12,}", re.I),
    re.compile(r"\b(?:key|secret)\s*=\s*[A-Za-z0-9+/]{24,}={0,2}", re.I),
]
ip_pattern = re.compile(r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b")

errors = []
warnings = []
for base in (ROOT / "docs", ROOT / "data"):
    if not base.exists():
        continue
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json"}:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in ignored:
            continue
        for no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if any(p.search(line) for p in secret_patterns):
                errors.append(f"{rel}:{no}: {line.strip()}")
            for ip in ip_pattern.findall(line):
                warnings.append(f"{rel}:{no}: {ip}")

if warnings:
    print("CẢNH BÁO IP nội bộ:")
    print("\n".join("  " + w for w in sorted(set(warnings))))
if errors:
    print("LỖI: phát hiện key/mật khẩu/token nghi ngờ:")
    print("\n".join("  " + e for e in errors))
    sys.exit(1)
print("secrets: không phát hiện key/mật khẩu/token nghi ngờ")
