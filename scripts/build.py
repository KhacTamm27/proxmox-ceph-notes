#!/usr/bin/env python3
"""Sinh README.md, docs/**/*.md và docs/index.html từ data/commands.json.

Chạy:  python3 scripts/build.py --repo <user>/<repo>
Sửa lệnh CHỈ trong data/commands.json rồi chạy lại, đừng sửa tay file sinh ra.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="", help="user/repo, dùng cho link từ mindmap sang file .md")
args = ap.parse_args()

data = json.loads((ROOT / "data/commands.json").read_text(encoding="utf-8"))
vi = json.loads((ROOT / "data/vi.json").read_text(encoding="utf-8"))
cases = json.loads((ROOT / "data/cases.json").read_text(encoding="utf-8"))
SIDES = {"left": ("proxmox", "Proxmox host"), "right": ("ceph", "Ceph")}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def relpath(b, folder):
    num = int(re.sub(r"\D", "", b["id"]))
    return f"{folder}/{b['id'][0]}{num:02d}-{slug(b['name'])}.md"


def count(b):
    return sum(len(s["items"]) for s in b["subs"])


slugs = {}
all_cmds = set()
covered = 0
for side, branches in data.items():
    for b in branches:
        slugs[b["id"]] = relpath(b, SIDES[side][0])
        for sub in b["subs"]:
            for it in sub["items"]:
                all_cmds.add(it["c"])
                if it["c"] in vi:
                    it["v"], it["k"] = vi[it["c"]]
                    covered += 1
unknown = [c for c in vi if c not in all_cmds]
if unknown:
    print("CẢNH BÁO: vi.json có lệnh không khớp commands.json:", *unknown, sep="\n  ")

for folder in ("proxmox", "ceph", "cases"):
    p = ROOT / "docs" / folder
    shutil.rmtree(p, ignore_errors=True)
    p.mkdir(parents=True)
for sc in ("ceph", "pve"):
    (ROOT / "docs/cases" / sc).mkdir(parents=True, exist_ok=True)
SCOPE_LABEL = {"ceph": "Ceph", "pve": "Proxmox cluster"}

# ---- từng file .md ----
for side, branches in data.items():
    folder, label = SIDES[side]
    for i, b in enumerate(branches):
        out = [f"# {b['id']} · {b['name']}", "",
               f"[← Mục lục](../../README.md) · {label} · {count(b)} lệnh", ""]
        nav = []
        if i > 0:
            pb = branches[i - 1]
            nav.append(f"[← {pb['id']} {pb['name']}](../{slugs[pb['id']]})")
        if i < len(branches) - 1:
            nb = branches[i + 1]
            nav.append(f"[{nb['id']} {nb['name']} →](../{slugs[nb['id']]})")
        if nav:
            out += [" · ".join(nav), ""]
        for s in b["subs"]:
            out += [f"## {s['name']}", "", "```bash"]
            for it in s["items"]:
                tag = "⚠ NGUY HIỂM: " if it["d"] else ""
                if it.get("v"):
                    out += [f"# {tag}{it['v']} | {it['p']}", f"# từ khóa: {it['k']}", it["c"], ""]
                else:
                    out += [f"# {tag}{it['p']}", it["c"], ""]
            out[-1] = "```"
            out.append("")
        (ROOT / "docs" / slugs[b["id"]]).write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

# ---- case study .md ----
for c in cases:
    o = [f"# {c['title']}", "", f"[← Mục lục](../../../README.md) · Case study {SCOPE_LABEL[c['scope']]}", "",
         f"**Triệu chứng:** {c['symptoms']}", "", f"**Nguyên nhân hay gặp:** {c['causes']}", "",
         "## Các bước xử lý", ""]
    for i, st in enumerate(c["steps"], 1):
        o += [f"{i}. {st['t']}", "", "```bash"] + st["cmds"] + ["```", ""]
    o += ["## Lưu ý", "", c["notes"], "",
          f"<!-- từ khóa: {c['tags']} -->"]
    (ROOT / "docs/cases" / c["scope"] / f"{c['id']}.md").write_text("\n".join(o) + "\n", encoding="utf-8")

# ---- README ----
total = sum(count(b) for br in data.values() for b in br)
dang = sum(it["d"] for br in data.values() for b in br for s in b["subs"] for it in s["items"])
ngroups = sum(len(v) for v in data.values())
r = ["# Proxmox + Ceph command notes", "",
     f"Tài liệu cá nhân: {total} lệnh, {ngroups} nhóm. Lệnh có ⚠ ({dang} lệnh) là lệnh phá hủy hoặc "
     "ảnh hưởng dịch vụ, đọc kỹ trước khi chạy.", ""]
if args.repo:
    user, name = args.repo.split("/")
    r += [f"**Mindmap tương tác (lọc lệnh, mở thẳng từng mục):** https://{user}.github.io/{name}/", ""]
r += ["## Cách tìm nhanh", "",
      "- Biết tên nhóm: bấm vào mục lục bên dưới, hoặc mở mindmap kèm `#B13` (ví dụ `.../#B13` mở thẳng RGW).",
      "- Biết từ khóa: mở mindmap, nhấn `/` rồi gõ. Link `.../?q=scrub` mở sẵn kết quả lọc.",
      "- Trên GitHub: nhấn `t` để tìm file theo tên, nhấn `/` để tìm trong repo (gõ `crush`, `radosgw-admin user`).",
      "- Trong một file .md: nút Outline (góc phải trên) nhảy giữa các mục con, mỗi khối lệnh có nút copy.", ""]
for sc in ("ceph", "pve"):
    r += [f"## Case study {SCOPE_LABEL[sc]} (lỗi và cách xử lý)", "", "| Sự cố | Triệu chứng |", "|---|---|"]
    for c in cases:
        if c["scope"] == sc:
            r.append(f"| [{c['title']}](docs/cases/{sc}/{c['id']}.md) | {c['symptoms'].replace('|', '/')} |")
    r.append("")
for side, branches in data.items():
    folder, label = SIDES[side]
    r += [f"## {label}", "", "| ID | Nhóm | Lệnh | Gồm |", "|---|---|---:|---|"]
    for b in branches:
        subs = ", ".join(s["name"] for s in b["subs"])
        r.append(f"| {b['id']} | [{b['name']}](docs/{slugs[b['id']]}) | {count(b)} | {subs} |")
    r.append("")
r += ["## Cập nhật tài liệu", "",
      "- `data/commands.json`: nhóm → nhóm con → `{c: lệnh, p: mô tả, d: nguy hiểm?}`.",
      "- `data/vi.json`: mô tả tiếng Việt và từ khóa, khóa là đúng chuỗi lệnh trong commands.json: `\"lệnh\": [\"mô tả\", \"từ khóa\"]`.",
      "- `data/cases.json`: các case study (triệu chứng, nguyên nhân, các bước, lưu ý).", "",
      "Sau khi sửa, chạy:", "",
      "```bash", f"python3 scripts/build.py --repo {args.repo or '<user>/<repo>'}", "```", "",
      "Lệnh trên sinh lại README này, toàn bộ `docs/**/*.md` và `docs/index.html`.", ""]
(ROOT / "README.md").write_text("\n".join(r), encoding="utf-8")

# ---- mindmap HTML ----
tpl = (ROOT / "scripts/template.html").read_text(encoding="utf-8")
html = (tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
           .replace("/*__REPO__*/", args.repo)
           .replace("/*__SLUGS__*/{}", json.dumps(slugs))
           .replace("/*__CASES__*/[]", json.dumps(cases, ensure_ascii=False)))
(ROOT / "docs/index.html").write_text(html, encoding="utf-8")
print(f"ok: {len(slugs)} file .md, {len(cases)} case ({sum(c["scope"]=="ceph" for c in cases)} Ceph, {sum(c["scope"]=="pve" for c in cases)} Proxmox), {total} lệnh, Việt hóa {covered}/{total}")
