#!/usr/bin/env python3
"""Sinh README.md, docs/**/*.md, docs/index.html và prototype/index.html từ data/*.json.

Chạy:  python3 scripts/build.py --repo <user>/<repo>
Sửa lệnh CHỈ trong data/commands.json rồi chạy lại, đừng sửa tay file sinh ra.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="", help="user/repo, dùng cho link từ mindmap sang file .md")
args = ap.parse_args()

data = json.loads((ROOT / "data/commands.json").read_text(encoding="utf-8"))
vi = json.loads((ROOT / "data/vi.json").read_text(encoding="utf-8"))
cases = json.loads((ROOT / "data/cases.json").read_text(encoding="utf-8"))
triage = json.loads((ROOT / "data/triage.json").read_text(encoding="utf-8"))
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
missing = []
for side, branches in data.items():
    for b in branches:
        slugs[b["id"]] = relpath(b, SIDES[side][0])
        for sub in b["subs"]:
            for it in sub["items"]:
                all_cmds.add(it["c"])
                if it["c"] in vi:
                    it["v"], it["k"] = vi[it["c"]]
                    covered += 1
                else:
                    missing.append(it["c"])
unknown = [c for c in vi if c not in all_cmds]
if unknown:
    print("CẢNH BÁO: vi.json có lệnh không khớp commands.json:", *unknown, sep="\n  ")
if missing:
    print("CẢNH BÁO: commands.json có lệnh thiếu mô tả tiếng Việt/từ khóa trong vi.json:", *missing, sep="\n  ")

for folder in ("proxmox", "ceph", "cases", "runbooks", "scripts", "diagrams"):
    p = ROOT / "docs" / folder
    shutil.rmtree(p, ignore_errors=True)
    p.mkdir(parents=True)
for sc in ("ceph", "pve"):
    (ROOT / "docs/cases" / sc).mkdir(parents=True, exist_ok=True)
scr_list = json.loads((ROOT / "data/scripts.json").read_text(encoding="utf-8"))
for sc_ in scr_list:
    sc_["code"] = (ROOT / "tools" / sc_["file"]).read_text(encoding="utf-8")
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

# ---- case study / runbook .md ----
# ---- nạp file cấu hình (configs/) và sơ đồ (data/diagrams/) mà các bước tham chiếu ----
for c in cases:
    for st in c["steps"]:
        for f in st.get("files", []):
            f["code"] = (ROOT / "configs" / f["src"]).read_text(encoding="utf-8")
    for g in c.get("diagrams", []):
        g["svg"] = (ROOT / "data/diagrams" / g["src"]).read_text(encoding="utf-8")
        shutil.copy(ROOT / "data/diagrams" / g["src"], ROOT / "docs/diagrams" / g["src"])

for c in cases:
    rb = c.get("kind") == "runbook"
    if rb:
        o = [f"# {c['title']}", "", "[← Mục lục](../../README.md) · Runbook", "",
             f"**Mục tiêu:** {c['goal']}", "", f"**Điều kiện trước khi làm:** {c['prereq']}", "", "## Các bước", ""]
        o[8:8] = [x for g in c.get("diagrams", []) for x in (f"![{g['caption']}](../diagrams/{g['src']})", "")]
    else:
        o = [f"# {c['title']}", "", f"[← Mục lục](../../../README.md) · Case study {SCOPE_LABEL[c['scope']]}", "",
             f"**Triệu chứng:** {c['symptoms']}", "", f"**Nguyên nhân hay gặp:** {c['causes']}", "",
             "## Các bước xử lý", ""]
    for i, st in enumerate(c["steps"], 1):
        o += [f"{i}. {st['t']}", ""]
        if st["cmds"]:
            o += ["```bash"] + st["cmds"] + ["```", ""]
        for f in st.get("files", []):
            o += [f"**`{f['path']}`**", "", f"```{f.get('lang', '')}", f["code"].rstrip("\n"), "```", ""]
    if c.get("quick_reference"):
        o += ["## Tham khảo nhanh", ""]
        o += [f"- **{item['title']}:** {item['text']}" for item in c["quick_reference"]]
        o.append("")
    o += ["## Lưu ý", "", c["notes"], ""]
    if c.get("refs"):
        o += ["## Nguồn tham khảo", ""] + [f"- [{r['t']}]({r['u']})" for r in c["refs"]] + [""]
    o += [f"<!-- từ khóa: {c['tags']} -->"]
    dest = ROOT / "docs/runbooks" / f"{c['id']}.md" if rb else ROOT / "docs/cases" / c["scope"] / f"{c['id']}.md"
    dest.write_text("\n".join(o) + "\n", encoding="utf-8")

# ---- script .md ----
for sc_ in scr_list:
    lang = "python" if Path(sc_["file"]).suffix == ".py" else "bash"
    o = [f"# {sc_['title']}", "", "[← Mục lục](../../README.md) · Script tiện ích", "",
         f"**Mục đích:** {sc_['goal']}", "", "## Cách dùng", "", "```bash"]
    o += [f"{u['c']}    # {u['d']}" for u in sc_["usage"]]
    o += ["```", "", f"File gốc: [`tools/{sc_['file']}`](../../tools/{sc_['file']})", "",
          "## Lưu ý", "", sc_["notes"], "", "## Mã nguồn", "", f"```{lang}", sc_["code"].rstrip("\n"), "```", "",
          f"<!-- từ khóa: {sc_['tags']} -->"]
    (ROOT / "docs/scripts" / f"{sc_['id']}.md").write_text("\n".join(o) + "\n", encoding="utf-8")

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
      "- Mới bắt đầu: mở mindmap, chọn lối đi theo nhu cầu (tìm lệnh, sửa lỗi Proxmox/Ceph, cấu hình network); mở case để đọc triệu chứng, nguyên nhân, các bước và lưu ý.",
      "- Tìm nội dung: gõ từ khóa tiếng Việt hoặc tiếng Anh vào ô tìm kiếm; truy vấn như `storage bị chậm` hoặc `VM crash` có thể hiện quy trình chẩn đoán ban đầu, lệnh đọc trạng thái và cách hiểu dấu hiệu. Mindmap tài liệu là trang tĩnh, không kết nối cluster.",
      "- Prototype chẩn đoán nội bộ: `prototype/` có thể yêu cầu backend riêng lấy snapshot PVE chỉ đọc khi người vận hành bấm nút. Cần VPN, xác thực, token giới hạn và triển khai theo `prototype/DEPLOYMENT.md`; không nhúng token vào trình duyệt.",
      "- Nhấn `/` để focus tìm kiếm, Enter để tới kết quả, Esc để xóa.",
      "- Tra cứu nhóm lệnh: mở nhóm theo chủ đề; bấm lệnh để copy. Các nhóm Proxmox và Ceph có nhãn màu riêng.",
      "- Mở nhanh qua URL: thêm `#B13` để tới nhóm lệnh (ví dụ RGW), hoặc `?q=scrub` để mở sẵn kết quả tìm kiếm.",
      "- Trên GitHub: nhấn `t` để tìm file theo tên, nhấn `/` để tìm trong repo (gõ `crush`, `radosgw-admin user`).",
      "- Lệnh có ⚠ hoặc hiển thị cảnh báo cần được đọc kỹ trước khi chạy trên cluster thật.", ""]
for sc in ("ceph", "pve"):
    r += [f"## Case study {SCOPE_LABEL[sc]} (lỗi và cách xử lý)", "", "| Sự cố | Triệu chứng |", "|---|---|"]
    for c in cases:
        if c["scope"] == sc and c.get("kind") != "runbook":
            r.append(f"| [{c['title']}](docs/cases/{sc}/{c['id']}.md) | {c['symptoms'].replace('|', '/')} |")
    r.append("")
r += ["## Runbook (quy trình thao tác từng bước)", "", "| Runbook | Mục tiêu |", "|---|---|"]
for c in cases:
    if c.get("kind") == "runbook":
        r.append(f"| [{c['title']}](docs/runbooks/{c['id']}.md) | {c['goal'].replace('|', '/')} |")
r.append("")
r += ["## Script tiện ích", "", "| Script | Mục đích |", "|---|---|"]
for sc_ in scr_list:
    r.append(f"| [{sc_['title']}](docs/scripts/{sc_['id']}.md) | {sc_['goal'].replace('|', '/')} |")
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
      "- `data/cases.json`: các case study (triệu chứng, nguyên nhân, các bước, lưu ý).",
      "- `data/triage.json`: hướng dẫn chẩn đoán ban đầu theo mô tả tự nhiên (ví dụ VM crash, storage chậm), gồm lệnh chỉ đọc, dấu hiệu cần xem và case liên quan.",
      "- `data/scripts.json` và thư mục `tools/`: script tiện ích (siêu dữ liệu trong JSON, mã nguồn `.sh` hoặc `.py` trong `tools/`).", "",
      "Sau khi sửa, chạy:", "",
      "```bash", f"python3 scripts/build.py --repo {args.repo or '<user>/<repo>'}", "```", "",
      "Lệnh trên sinh lại README này, toàn bộ `docs/**/*.md`, `docs/index.html` và `prototype/index.html`.", ""]
(ROOT / "README.md").write_text("\n".join(r), encoding="utf-8")

# ---- mindmap HTML ----
tpl = (ROOT / "scripts/template.html").read_text(encoding="utf-8")
html = (tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
           .replace("/*__REPO__*/", args.repo)
           .replace("/*__SLUGS__*/{}", json.dumps(slugs))
           .replace("/*__CASES__*/[]", json.dumps(cases, ensure_ascii=False).replace("</", "<\\/"))
           .replace("/*__TRIAGE__*/[]", json.dumps(triage, ensure_ascii=False).replace("</", "<\\/"))
           .replace("/*__SCRIPTS__*/[]", json.dumps(scr_list, ensure_ascii=False).replace("</", "<\\/")))
(ROOT / "docs/index.html").write_text(html, encoding="utf-8")
prototype_tpl = (ROOT / "prototype/template.html").read_text(encoding="utf-8")
prototype_html = (prototype_tpl
                  .replace("/*__TRIAGE__*/[]", json.dumps(triage, ensure_ascii=False).replace("</", "<\\/"))
                  .replace("/*__CASES__*/[]", json.dumps(cases, ensure_ascii=False).replace("</", "<\\/")))
(ROOT / "prototype/index.html").write_text(prototype_html, encoding="utf-8")
nrb = sum(c.get("kind") == "runbook" for c in cases)
nce = sum(c["scope"] == "ceph" and c.get("kind") != "runbook" for c in cases)
npv = sum(c["scope"] == "pve" and c.get("kind") != "runbook" for c in cases)
print(
    f"ok: {len(slugs)} file .md, {nce + npv} case ({nce} Ceph, {npv} Proxmox), "
    f"{nrb} runbook, {len(scr_list)} script, {total} lệnh, Việt hóa {covered}/{total}"
    .encode("utf-8", errors="replace").decode("utf-8")
)
