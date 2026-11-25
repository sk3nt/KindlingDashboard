r"""Build site/dev-dashboard.html: a static snapshot of Kindling engine development.

Reads the task queue (handover/queue/kindling-task-queue.md) and reports/ from the KindlingEngine repo and
writes dev-dashboard.html in this repo. Engine path: first argument, else the KINDLING_ENGINE environment
variable, else ../Kindling next to this repo (D:\AIGameDev\Kindling).
Run from anywhere:  python tools/build_dev_dashboard.py [path-to-KindlingEngine]
The chat integrator rebuilds it whenever it pushes queue changes. The old local dashboard is retired (2026-11-25).
"""
import html, re, subprocess, datetime, pathlib, json

import os, sys
SITE = pathlib.Path(__file__).resolve().parent.parent
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KINDLING_ENGINE", SITE.parent / "Kindling")).resolve()
QUEUE = ROOT / "handover/queue/kindling-task-queue.md"
OUT = SITE / "dev-dashboard.html"

STEPS = [
    (1, "Project root abstraction and headless copy sync", "step1"),
    (2, "Pipeline package: Unity wrapper, typed CLI results", "step2"),
    (3, "Budget client", "step3"),
    (4, "Dashboard job runner (4b board, 4c review pane)", "step4"),
    (5, "Permission profiles and two-way canary", "step5"),
    (6, "Build and player smoke test", "step6"),
    (7, "Stub morning report", "step7"),
    (8, "Reconciler and five layer scenes", "step8"),
    (9, "Work repo and one-click merge into main", "step9"),
    (10, "Production agents, then judges, then the watcher", "step10"),
]
STANDARDS = [
    ("S1", "Scale, units and axes", "Prism"),
    ("S2", "Character sheet standard", "Lumen, Gait, Pivot"),
    ("S3", "Rig standard v2", "Pivot"),
    ("S4", "Head and face landmarks", "Pivot"),
    ("S5", "Mesh and UV standard", "Prism"),
    ("S6", "Material library and PBR rules", "Prism, Lumen"),
    ("S7", "Prop sheet standard", "Prism, Lumen"),
    ("S8", "World grid and streaming", "Ridge, Prism, Anvil"),
    ("S9", "Quality tiers", "Prism, Anvil"),
]
# Experiments: queue task number, short name, owner, depends on
EXPERIMENTS = [
    (50, "E1", "Turnaround, head and hand sheets", "Lumen", []),
    (51, "E2", "Mesh bake-off", "Clay", ["E1"]),
    (52, "E3", "Rig standard v2 and landmarks", "Pivot", ["E2"]),
    (53, "E4", "Prop sheets and 5 props", "Prism, Kiln", []),
    (54, "E5", "PBR materials, hero at 3 tiers", "Prism, Lumen", ["E3"]),
    (55, "E6", "Face shapes and video-driven clip", "Flip, Pivot", ["E3"]),
    (56, "E7", "One streamed 1 km tile", "Ridge, Prism", []),
    (57, "E8", "Mobile proof", "Anvil", ["E5", "E7"]),
]
OPEN_DECISIONS = [
    "Realism level: fully photoreal or stylised real (production-targets.md).",
    "Character heights, and Tally's scale.",
    "Lead platform: PC first, mobile as a scaled tier (default).",
    "New crafts and names: world streaming, VFX.",
    "Let Claude Code commit and push handover/ only, so its queue notes reach git (rule 10).",
]


def classify(status, body):
    s = status.lower()
    accepted = bool(re.search(r"^\s*-?\s*Accepted:\s*Steven", body, re.M))
    if s.startswith("done"):
        if "superseded" in s or "by integrator" in s:
            return "done"
        return "done" if accepted or "accepted" in s else "review"
    if s.startswith("parked"):
        return "parked"
    if s.startswith("in-progress"):
        return "active"
    if s.startswith("awaiting-approval"):
        return "steven"
    if s.startswith("awaiting"):
        return "blocked"
    if s.startswith("ready") or s.startswith("approved"):
        notes = " ".join(re.findall(r"Claude Code notes:?(.*)", body))
        return "active" if re.search(r"\bstarted\b", notes) else "ready"
    return "ready"


LABEL = {"done": "Done", "review": "Done, awaiting your acceptance", "active": "In progress",
         "ready": "Ready", "blocked": "Waiting on another task", "steven": "Waiting on Steven",
         "parked": "Parked"}
ORDER = ["active", "ready", "blocked", "steven", "review", "done", "parked"]


def parse_queue(text):
    tasks = []
    for m in re.finditer(r"^### (\d+)\. (.+?)\n(.*?)(?=^### |\Z)", text, re.S | re.M):
        n, title, body = int(m.group(1)), m.group(2).strip(), m.group(3)
        st = re.search(r"^- Status: (.*)$", body, re.M)
        status = st.group(1).strip() if st else ""
        tasks.append({"n": n, "title": title, "status": status, "k": classify(status, body)})
    dec = re.findall(r"^- (?:\*\*)?(?:2026-\d\d-\d\d|[A-Z][^.]*\(Steven, chat 2026-\d\d-\d\d\)).*$", text, re.M)
    return tasks, dec[-6:]


def esc(s):
    return html.escape(s, quote=True)


def main():
    text = QUEUE.read_text(encoding="utf-8")
    tasks, decisions = parse_queue(text)
    by_n = {t["n"]: t for t in tasks}
    try:
        commit = subprocess.check_output(["git", "-C", str(ROOT), "log", "-1", "--format=%h %cd", "--date=format:%Y-%m-%d %H:%M"], text=True).strip()
    except Exception:
        commit = "unknown"
    reports = {p.name for p in (ROOT / "reports").glob("*.md")}
    built = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    counts = {k: sum(1 for t in tasks if t["k"] == k) for k in ORDER}
    total = len(tasks)
    bar = "".join(f'<span class="seg {k}" style="flex:{counts[k]}" title="{LABEL[k]}: {counts[k]}"></span>' for k in ORDER if counts[k])
    legend = "".join(f'<button class="chip {k}" data-k="{k}" aria-pressed="false"><i></i>{LABEL[k]} <b>{counts[k]}</b></button>' for k in ORDER if counts[k])

    needs = [t for t in tasks if t["k"] in ("steven", "review")]
    needs_html = "".join(f'<li><span class="n">{t["n"]}</span> {esc(t["title"])}<em>{LABEL[t["k"]]}</em></li>' for t in needs)
    needs_html += "".join(f'<li><span class="n">?</span> {esc(d)}<em>Open decision</em></li>' for d in OPEN_DECISIONS)

    exp_html = ""
    for n, e, name, owner, dep in EXPERIMENTS:
        t = by_n.get(n)
        k = t["k"] if t else "blocked"
        exp_html += (f'<div class="exp {k}"><div class="eh"><b>{e}</b><span>{LABEL[k]}</span></div>'
                     f'<p>{esc(name)}</p><small>{esc(owner)}' + (f' · after {", ".join(dep)}' if dep else '') +
                     f' · task {n}</small></div>')

    steps_html = ""
    for i, name, key in STEPS:
        rep = sorted(r for r in reports if re.match(key + r"[a-z]?-\d", r))
        ok = bool(rep) and i < 10
        part = i == 10 and any(r.startswith("step10") for r in reports)
        cls = "done" if ok else ("active" if part else "ready")
        note = (", ".join(rep[:3])) if rep else "not started"
        steps_html += f'<li class="{cls}"><b>{i}</b><span>{esc(name)}</span><small>{esc(note)}</small></li>'

    std_html = "".join(f'<tr><td><b>{s}</b></td><td>{esc(n)}</td><td>{esc(o)}</td><td><span class="pill ready">Not started</span></td></tr>' for s, n, o in STANDARDS)

    rows = "".join(f'<tr data-k="{t["k"]}"><td class="num">{t["n"]}</td><td>{esc(t["title"])}</td><td><span class="pill {t["k"]}">{LABEL[t["k"]]}</span></td><td class="st">{esc(t["status"][:160])}</td></tr>' for t in tasks)
    dec_html = "".join(f"<li>{esc(re.sub(r'[*`]', '', d))[:420]}</li>" for d in reversed(decisions))

    page = TEMPLATE
    for k, v in {"%BUILT%": built, "%COMMIT%": esc(commit), "%TOTAL%": str(total), "%BAR%": bar, "%LEGEND%": legend,
                 "%NEEDS%": needs_html, "%EXP%": exp_html, "%STEPS%": steps_html, "%STD%": std_html,
                 "%ROWS%": rows, "%DEC%": dec_html, "%ACTIVE%": str(counts["active"]), "%READY%": str(counts["ready"]),
                 "%STEVEN%": str(len(needs)), "%DONE%": str(counts["done"] + counts["review"])}.items():
        page = page.replace(k, v)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT}: {total} tasks from {QUEUE}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kindling: engine development</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..800&display=swap" rel="stylesheet">
<style>
:root{--ash:#E3E6E3;--ash-2:#D5D9D5;--card:#EEF0EE;--slag:#22292E;--slag-2:#4A545B;
--done:#2A8F55;--review:#6FB98A;--active:#D9622B;--ready:#3B6E8F;--blocked:#9AA5AD;--steven:#C98A12;--parked:#B9BFC3}
*{box-sizing:border-box}body{margin:0;background:var(--ash);color:var(--slag);font:400 15.5px/1.5 "Archivo",system-ui,sans-serif}
a{color:inherit}button:focus-visible,a:focus-visible{outline:3px solid var(--active);outline-offset:2px}
.wrap{max-width:1240px;margin:0 auto;padding:0 24px}
header{padding:36px 0 8px;display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap}
h1{font-variation-settings:"wdth" 125;font-weight:800;font-size:44px;line-height:1;margin:0}
h2{font-variation-settings:"wdth" 120;font-weight:750;font-size:22px;margin:0 0 12px}
.meta{font-size:13.5px;color:var(--slag-2);text-align:right}
.meta a{font-weight:600}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;background:var(--slag);border:2px solid var(--slag);margin:22px 0 0}
.kpis div{background:var(--card);padding:14px 16px}
.kpis b{display:block;font-variation-settings:"wdth" 125;font-weight:800;font-size:38px;line-height:1}
.kpis span{font-size:14px;color:var(--slag-2)}
.kpis .a b{color:var(--active)} .kpis .s b{color:var(--steven)} .kpis .d b{color:var(--done)}
.bar{display:flex;height:14px;margin:16px 0 10px;border:2px solid var(--slag)}
.seg{display:block}.seg.done{background:var(--done)}.seg.review{background:var(--review)}.seg.active{background:var(--active)}.seg.ready{background:var(--ready)}.seg.blocked{background:var(--blocked)}.seg.steven{background:var(--steven)}.seg.parked{background:var(--parked)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{font:inherit;font-size:13.5px;background:var(--card);border:1px solid #B8BFBA;padding:4px 10px;cursor:pointer;color:var(--slag)}
.chip i{display:inline-block;width:10px;height:10px;margin-right:6px;vertical-align:0}
.chip[aria-pressed="true"]{background:var(--slag);color:#fff;border-color:var(--slag)}
.chip.done i{background:var(--done)}.chip.review i{background:var(--review)}.chip.active i{background:var(--active)}.chip.ready i{background:var(--ready)}.chip.blocked i{background:var(--blocked)}.chip.steven i{background:var(--steven)}.chip.parked i{background:var(--parked)}
.grid{display:grid;grid-template-columns:1.35fr 1fr;gap:28px;margin-top:36px}
@media (max-width:900px){.grid{grid-template-columns:1fr}.kpis{grid-template-columns:1fr 1fr}}
section{margin-top:36px}
.exps{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
@media (max-width:900px){.exps{grid-template-columns:1fr 1fr}}
.exp{background:var(--card);border-top:5px solid var(--k,var(--blocked));padding:10px 12px 12px}
.exp.done{--k:var(--done)}.exp.active{--k:var(--active)}.exp.ready{--k:var(--ready)}.exp.steven{--k:var(--steven)}.exp.review{--k:var(--review)}
.eh{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.eh b{font-variation-settings:"wdth" 125;font-weight:800;font-size:22px}
.eh span{font-size:12.5px;color:var(--slag-2);text-align:right}
.exp p{margin:4px 0 6px;font-weight:600;font-size:15px;line-height:1.3}
.exp small{font-size:12.5px;color:var(--slag-2)}
ol.steps{list-style:none;margin:0;padding:0;border-top:2px solid var(--slag)}
ol.steps li{display:grid;grid-template-columns:34px 1fr;gap:0 10px;padding:8px 0;border-bottom:1px solid #C3C9C5}
ol.steps b{font-variation-settings:"wdth" 125;font-weight:800;font-size:20px;grid-row:span 2}
ol.steps li.done b{color:var(--done)} ol.steps li.active b{color:var(--active)} ol.steps li.ready b{color:var(--ready)}
ol.steps small{font-size:12.5px;color:var(--slag-2)}
ul.needs{list-style:none;margin:0;padding:0;border-top:2px solid var(--slag)}
ul.needs li{padding:9px 0;border-bottom:1px solid #C3C9C5;display:grid;grid-template-columns:36px 1fr;gap:0 8px;font-size:14.5px}
ul.needs .n{font-weight:800;color:var(--steven);grid-row:span 2}
ul.needs em{font-style:normal;font-size:12.5px;color:var(--slag-2)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:7px 10px 7px 0;border-bottom:1px solid #C3C9C5;vertical-align:top}
th{font-size:13px;color:var(--slag-2);font-weight:600;border-bottom:2px solid var(--slag)}
td.num{font-weight:700;width:40px}td.st{color:var(--slag-2);font-size:13px}
.pill{display:inline-block;font-size:12px;padding:1px 8px;white-space:nowrap;color:#fff;background:var(--k)}
.pill.done{--k:var(--done)}.pill.review{--k:#4C9A69}.pill.active{--k:var(--active)}.pill.ready{--k:var(--ready)}.pill.blocked{--k:#7E8A93}.pill.steven{--k:#A87208}.pill.parked{--k:#8D959A}
.tablewrap{overflow-x:auto}
ul.dec{margin:0;padding-left:18px;font-size:14px}ul.dec li{margin-bottom:8px}
.caveat{font-size:13px;color:var(--slag-2);max-width:80ch}
footer{margin:48px 0 40px;font-size:13px;color:var(--slag-2)}
</style></head><body><div class="wrap">
<header><div><h1>Engine development</h1><p class="caveat">Snapshot of the Kindling task queue in git. Claude Code's own status edits stay uncommitted on the PC, so rows it is working on can lag here.</p></div>
<div class="meta">Built %BUILT%<br>Queue commit %COMMIT%<br><a href="index.html">Home</a> · <a href="engine.html">Engine overview</a></div></header>

<div class="kpis"><div class="a"><b>%ACTIVE%</b><span>In progress</span></div><div><b>%READY%</b><span>Ready to start</span></div><div class="s"><b>%STEVEN%</b><span>Need Steven</span></div><div class="d"><b>%DONE%</b><span>Done (of %TOTAL% tasks)</span></div></div>
<div class="bar" aria-hidden="true">%BAR%</div>

<section><h2>AAA PBR experiments</h2><div class="exps">%EXP%</div></section>

<div class="grid">
<section style="margin-top:0"><h2>Needs Steven</h2><ul class="needs">%NEEDS%</ul></section>
<section style="margin-top:0"><h2>Engine build order</h2><ol class="steps">%STEPS%</ol></section>
</div>

<section><h2>Standards</h2><div class="tablewrap"><table><thead><tr><th>#</th><th>Standard</th><th>Owner</th><th>State</th></tr></thead><tbody>%STD%</tbody></table></div></section>

<section><h2>All tasks</h2><div class="chips" role="group" aria-label="Filter by status">%LEGEND%</div>
<div class="tablewrap" style="margin-top:12px"><table id="tasks"><thead><tr><th>#</th><th>Task</th><th>State</th><th>Status line</th></tr></thead><tbody>%ROWS%</tbody></table></div></section>

<section><h2>Latest decisions</h2><ul class="dec">%DEC%</ul></section>
<footer>Built by tools/build_dev_dashboard.py in KindlingDashboard from KindlingEngine handover/queue/kindling-task-queue.md and reports/.</footer>
</div>
<script>
const chips=[...document.querySelectorAll('.chip')];const rows=[...document.querySelectorAll('#tasks tbody tr')];
chips.forEach(c=>c.addEventListener('click',()=>{const on=c.getAttribute('aria-pressed')!=='true';chips.forEach(x=>x.setAttribute('aria-pressed','false'));c.setAttribute('aria-pressed',on?'true':'false');rows.forEach(r=>r.hidden=on&&r.dataset.k!==c.dataset.k);}));
</script></body></html>"""

if __name__ == "__main__":
    main()
