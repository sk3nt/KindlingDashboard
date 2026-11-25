#!/usr/bin/env python3
r"""Builds the "Look development: environment" section of engine.html between
<!--environment:start--> and <!--environment:end--> (placed after the characters section).
Prompts come from the game repo: Production/Design/prompts/environment-prompts.md.
  python tools/build_engine_environment.py [path-to-game-repo]
Game repo path: argument, KINDLING_GAME env var, or ../KindlingDiscovery.
Images: img/environment/<id>.webp and <id>-full.webp (opens full size in a new window)."""
import html, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KINDLING_GAME", ROOT.parent / "KindlingDiscovery"))
WTXT = (GAME / "Production" / "Design" / "prompts" / "world-map-prompts.md").read_text(encoding="utf-8")
WMAP = re.findall(r"^(MAP-[A-Z0-9-]+): (.*)$", WTXT, re.M)
WLAYOUT = re.findall(r"^- ([^:]+): (.*)$", WTXT.split("## The layout I chose", 1)[1].split("## Prompt 1", 1)[0], re.M)
TXT = (GAME / "Production" / "Design" / "prompts" / "environment-prompts.md").read_text(encoding="utf-8")
E = html.escape
IMG = ROOT / "img" / "environment"


def common(name):
    m = re.search(r"^" + name + r": (.*)$", TXT, re.M)
    return m.group(1).strip()


STYLE = common("STYLE REFS")
COMMONS = [("Location plate", common("COMMON PLATE")), ("Isolated structure sheet", common("COMMON STRUCTURE SHEET")), ("Prop sheet (S7)", common("COMMON PROP SHEET"))]
items = []
for m in re.finditer(r"^((?:V|C)\d|S-[VC]\d+|P\d+)( \([^)]*\))?: (.*)$|^((?:S-[VC]\d+|P\d+)) ([^:]+): (.*)$", TXT, re.M):
    if m.group(1):
        iid, paren, body = m.group(1), (m.group(2) or "").strip(" ()"), m.group(3)
        title = body.split(".")[0] if iid in ("V0", "C0") else ""
    else:
        iid, paren, body = m.group(4), "", m.group(6)
        title = m.group(5)
    items.append((iid, paren, title, body))

NAMES = {"V0": "Village establishing", "V1": "Village square", "V2": "Narrow alley", "V3": "Village steps", "V4": "Harbour lane",
         "V5": "Back lanes", "V6": "Rooftop routes", "V7": "Bridge and river", "C0": "Castle establishing", "C1": "Castle stairs",
         "C2": "Castle gate and ramparts", "C3": "Castle terrace, view south", "C4": "Castle courtyard", "C5": "The Mayor's hall"}
HAVE = {"v0": "Layout of record (painted canon art); the photoreal plate is next.",
        "v1": "Film frame, empty plate. Style reference for every village prompt.",
        "v2": "Film frame with Tomas; the clean plate is next.",
        "v3": "Poster background; the clean plate is next.",
        "c1": "Film frame with Ines. Style reference for every castle prompt; the clean plate is next.",
        "c2": "Poster background; the clean plate is next.",
        "c3": "Intro background; the clean plate is next."}


def snip(t, n=140):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def image(key, alt):
    if (IMG / f"{key}.webp").exists():
        return (f'<a class="im" href="img/environment/{key}-full.webp" target="_blank" rel="noopener" title="Open full size in a new window">'
                f'<img src="img/environment/{key}.webp" alt="{E(alt)}" loading="lazy"></a>')
    return '<div class="im gen" role="img" aria-label="Not generated yet"><span>Generate</span></div>'


def card(iid, paren, title, body):
    name = NAMES.get(iid) or title or iid
    key = iid.lower()
    note = HAVE.get(key)
    lid = re.match(r"L\d", paren or "")
    loc = f' <span class="loc">{lid.group(0)}</span>' if lid else ""
    pr = (f'<details class="pr"><summary><span class="snip">{E(snip(re.sub(r"^\[[^\]]*\]\s*", "", body)))}</span><span class="more">Full prompt</span></summary><pre>{E(body)}</pre></details>')
    return (f'<li class="cc" id="env-{key}"><div class="cl">{E(iid)} {E(name)}{loc}</div>{image(key, name)}'
            + (f'<p class="np">{E(note)}</p>' if note else "") + pr + "</li>")


def group(prefix):
    return "".join(card(*it) for it in items if re.match(prefix, it[0]))


REFS = re.findall(r"^REF ([^:]+): (.*)$", TXT, re.M)
refhtml = "".join(f"<li><b>{E(n)}</b> {E(t)}</li>" for n, t in REFS)
refs = "".join(f'<li class="cc"><div class="cl">{E(lab)}</div>{image(k, lab)}</li>' for k, lab in [
    ("v1", "Village square, empty plate"), ("v1b", "Market stall"), ("v2", "Narrow alley"), ("v3", "Village steps and coast"),
    ("c1", "Castle stairs"), ("c2", "Castle gate"), ("c3", "Castle terrace, view south")])
commons = "".join(f'<li><details class="pr cp"><summary><b>{E(lab)}</b><span class="snip">{E(snip(t, 210))}</span><span class="more">Full prompt</span></summary><pre>{E(t)}</pre></details></li>' for lab, t in COMMONS)

SECTION = f'''<!--environment:start-->
<section id="environment"><div class="wrap">
  <h2>Look development: environment</h2>
  <p class="lede">The photoreal film frames set the look. Every environment prompt attaches them as the style reference and asks for empty places, isolated structures and props. Village first, then the castle.</p>
  <h3 class="ch3">Style reference: the film frames</h3>
  <p class="o">Village prompts attach the empty village square plate; castle prompts attach the castle stairs frame. Each prompt asks to match their photographic look, light, grade and materials, and to use them only for look: no people.</p>
  <ol class="cstrip envref">{refs}</ol>
  <h3 class="ch3">Common prompts</h3>
  <p class="o">Each prompt below starts from one of these. The full set is in <code>Production/Design/prompts/environment-prompts.md</code> in the game repo.</p>
  <ol class="cprompts">{commons}</ol>
  <h3 class="ch3">Real-world references</h3>
  <p class="o">Places that look like ours, used for ideas only. Prompts describe the feature and never name the place, so the generator does not copy a real landmark.</p>
  <ul class="envrefs">{refhtml}</ul>
  <div class="crow" id="env-world"><h3>World map <small>8 by 8 km, top down</small></h3>
  <p class="o">The Episode 01 sketch is one square kilometre, the north-east corner. The rest is a proposal for Steven, Leo and Nora. Prompts in <code>Production/Design/prompts/world-map-prompts.md</code>.</p>
  <ul class="envrefs">{"".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in WLAYOUT)}</ul>
  <ol class="cstrip envgrid" style="margin-top:12px">{"".join(f'<li class="cc"><div class="cl">{E(k.replace("MAP-", "").replace("-", " ").title())}</div>{image(k.lower(), k)}<details class="pr"><summary><span class="snip">{E(snip(t))}</span><span class="more">Full prompt</span></summary><pre>{E(t)}</pre></details></li>' for k, t in WMAP)}</ol></div>
  <div class="crow"><h3>Village: key locations</h3><ol class="cstrip envgrid">{group(r"V\d")}</ol></div>
  <div class="crow"><h3>Castle: key locations</h3><ol class="cstrip envgrid">{group(r"C\d")}</ol></div>
  <div class="crow"><h3>Isolated key structures</h3><p class="o">Grid modules (house walls, stairs, roofs, terraces) become procedural kits later; their sheets are the look reference. Landmarks can be meshed from the sheet.</p><ol class="cstrip envgrid">{group(r"S-")}</ol></div>
  <div class="crow"><h3>Props</h3><p class="o">Props marked E4 are the first five to build. No stock game props: no barrels, crates, sacks or chests.</p><ol class="cstrip envgrid">{group(r"P\d")}</ol></div>
  <div class="todo"><h3 class="ch3">Next to do</h3><ol class="nexts">
    <li><b>Clean plates</b> for the frames that have a character in them: V2, V3, C1, C2, C3 (same camera, character removed).</li>
    <li><b>The world map:</b> generate the photoreal map first, then the illustrated one from it; Leo checks the layout against the Episode 01 sketch.</li>
    <li><b>V0, the village establishing shot,</b> from the layout of record, with the square plate attached for the look.</li>
    <li><b>Village plates V4 to V7,</b> then castle plates C0, C4 and C5.</li>
    <li><b>Structure sheets,</b> landmarks first: S-V4 market stall, the bridge (S-V5 or S-V10), S-C1 gatehouse, S-C4 keep, S-C6 gate tunnel.</li>
    <li><b>Steven decides</b> whether the timber footbridge becomes a fortified stone bridge with a gate tower (S-V10).</li>
    <li><b>Prop sheets for the five E4 props</b> (P3, P4, P5, P8, P12), then the rest.</li>
    <li><b>Steven approves</b> the 9 locations and caps in the props list (still a draft).</li>
  </ol></div>
</div></section>
<!--environment:end-->'''

CSS = '''/*environment:start*/
ol.envgrid{grid-template-columns:repeat(auto-fill,minmax(200px,1fr))}
ol.envref{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));margin-top:10px}
ol.envref .im{height:120px}
.cc .loc{font-weight:400;color:var(--slag-2)}
#environment code{word-break:break-all}
ul.envrefs{margin:10px 0 0;padding-left:20px;max-width:900px}ul.envrefs li{margin:0 0 8px;font-size:15px}
/*environment:end*/'''

p = ROOT / "engine.html"
s = p.read_text(encoding="utf-8")
if "<!--environment:start-->" in s:
    s = re.sub(r"<!--environment:start-->.*?<!--environment:end-->", lambda m: SECTION, s, flags=re.S)
else:
    s = s.replace("<!--characters:end-->", "<!--characters:end-->\n" + SECTION, 1)
if "/*environment:start*/" in s:
    s = re.sub(r"/\*environment:start\*/.*?/\*environment:end\*/", lambda m: CSS, s, flags=re.S)
else:
    s = s.replace("/*characters:end*/", "/*characters:end*/\n" + CSS, 1)
if 'href="#environment"' not in s:
    s = s.replace('<li><a href="#characters">Characters</a></li>', '<li><a href="#characters">Characters</a></li><li><a href="#environment">Environment</a></li>', 1)
    s = s.replace('<dt>See</dt><dd><a href="#characters">Characters, step by step</a></dd>', '<dt>See</dt><dd><a href="#characters">Characters, step by step</a>; <a href="#environment">environment</a></dd>', 1)
p.write_text(s, encoding="utf-8")
print("environment section:", len(items), "prompts")
