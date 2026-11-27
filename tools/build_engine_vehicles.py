#!/usr/bin/env python3
r"""Builds the "Look development: vehicles" section of engine.html between <!--vehicles:start--> and
<!--vehicles:end--> (after the environment section). Prompts come from the game repo:
Production/Design/prompts/vehicle-prompts.md.
  python tools/build_engine_vehicles.py [path-to-game-repo]
Images: img/vehicles/<id>.webp and <id>-full.webp; a missing image shows a Generate box."""
import html, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KINDLING_GAME", ROOT.parent / "KindlingDiscovery"))
TXT = (GAME / "Production" / "Design" / "prompts" / "vehicle-prompts.md").read_text(encoding="utf-8")
E = html.escape
IMG = ROOT / "img" / "vehicles"
FS = "in a woodland clearing south of the river, the village terraces and the castle cliff far behind"
DL = next(l for l in TXT.splitlines() if l.startswith("DESIGN LANGUAGE (paste into every vehicle prompt")).split("): ", 1)[1]
P = {}
for _k, _v in re.findall(r"^((?:QB|SB|CW|BT|GL)-[A-Z]+)(?: \([^)]*\))?: (.*)$", TXT, re.M):
    P.setdefault(_k, _v)
VEH = [("CW", "walker", "Ribbon craft", "The Hollow: desert mesa and crater"), ("QB", "quad", "Crystal craft", "The Deepwood: east forest"), ("GL", "glider", "Ring craft", "The Lampwrights: sea cliffs and coves"), ("SB", "scout", "Flower craft", "The crown: parked at the castle gate"), ("BT", "boat", "Stone-shard craft", "The Snowline: mountains and pass")]
STEPS = [("CONCEPT", "Concept"), ("SHEET", "Sheet"), ("ACTION", "In action"), ("DETAILS", "Details")]


def snip(t, n=140):
    t = re.sub(r"\s+", " ", re.sub(r"\[DESIGN LANGUAGE\]\s*", "", t).replace("[FOUND SETTING]", "in a faction's woodland")).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def im(key, alt):
    if (IMG / f"{key}.webp").exists():
        return (f'<a class="im" href="img/vehicles/{key}-full.webp" target="_blank" rel="noopener" title="Open full size in a new window">'
                f'<img src="img/vehicles/{key}.webp" alt="{E(alt)}" loading="lazy"></a>')
    return '<div class="im gen" role="img" aria-label="Not generated yet"><span>Generate</span></div>'


def row(code, key, name, sub):
    cards = "".join(
        f'<li class="cc"><div class="cl">{E(lab)}</div>{im(key + "-" + st.lower(), name + ", " + lab.lower())}'
        f'<details class="pr"><summary><span class="snip">{E(snip(P[code + "-" + st]))}</span><span class="more">Full prompt</span></summary>'
        f'<pre>{E(P[code + "-" + st].replace("[DESIGN LANGUAGE]", DL).replace("[FOUND SETTING]", FS))}</pre></details></li>' for st, lab in STEPS if code + "-" + st in P)
    return f'<div class="crow" id="v-{key}"><h3>{E(name)} <small>{E(sub)}</small></h3><ol class="cstrip vstrip">{cards}</ol></div>'


rows = "".join(row(*v) for v in VEH)
refs = "".join(f'<li class="cc"><div class="cl">{E(l)}</div><a class="im" href="img/characters/{k}-full.webp" target="_blank" rel="noopener" title="Open full size in a new window"><img src="img/characters/{k}.webp" alt="{E(l)}" loading="lazy"></a></li>'
               for k, l in [("tally-plate", "Tally plate: design language"), ("tally-poster", "Tally poster: photoreal look"), ("tally-concept", "Tally concept")])

SECTION = f'''<!--vehicles:start-->
<section id="vehicles"><div class="wrap">
  <h2>Look development: vehicles</h2>
  <p class="lede">Vehicles are alien-built, once supplied through the orbiting space station; only Tomas and Ines ride them. They share Tally's design language and hover on Ora: no wheels or legs; the glider is powered too (Steven, 2026-11-26). The hover quad comes first, then the hover bike, cargo hover sled, hover skiff and powered glider, one in each woodland faction. Prompts in the game repo, <code>Production/Design/prompts/vehicle-prompts.md</code>.</p>
  <h3 class="ch3">Design references: Tally</h3>
  <ol class="cstrip envref">{refs}</ol>
  <h3 class="ch3">Design language</h3>
  <ol class="cprompts"><li><details class="pr cp"><summary><b>Pasted into every vehicle prompt</b><span class="snip">{E(snip(DL, 220))}</span><span class="more">Full text</span></summary><pre>{E(DL)}</pre></details></li></ol>
  <p class="o"><b>Lore (Steven, 2026-11-25):</b> left behind on Earth by the same aliens who made Tally. One is found in each woodland faction's land, south of the river. The station is still without power in Episode 1, so nothing new comes down: Tomas and Ines find each vehicle where it was left, its core dark until charged at a tide pool. Concepts show a vehicle as found; sheets show it restored.</p>
  {rows}
  <div class="todo"><h3 class="ch3">Next to do</h3><ol class="nexts">
    <li><b>Generate the hover quad concept</b> with the Tally plate, the Tally poster and the village square attached.</li>
    <li><b>The sheet</b> once Steven approves the concept; Theo checks it for modelling, Daniel for scale in the lanes.</li>
    <li><b>Then the hover bike, cargo sled, hover skiff and glider concepts,</b> each as found in the world.</li>
    <li><b>Glider added</b> so each of the five factions holds one vehicle (integrator's choice, reversible until the factions are written).</li>
  </ol></div>
</div></section>
<!--vehicles:end-->'''
CSS = '''/*vehicles:start*/
ol.vstrip{grid-template-columns:repeat(4,minmax(0,1fr))}
#vehicles code{word-break:break-all}
@media (max-width:900px){ol.vstrip{grid-template-columns:repeat(2,minmax(0,1fr))}}
/*vehicles:end*/'''

p = ROOT / "engine.html"
s = p.read_text(encoding="utf-8")
if "<!--vehicles:start-->" in s:
    s = re.sub(r"<!--vehicles:start-->.*?<!--vehicles:end-->", lambda m: SECTION, s, flags=re.S)
else:
    s = s.replace("<!--environment:end-->", "<!--environment:end-->\n" + SECTION, 1)
if "/*vehicles:start*/" in s:
    s = re.sub(r"/\*vehicles:start\*/.*?/\*vehicles:end\*/", lambda m: CSS, s, flags=re.S)
else:
    s = s.replace("/*environment:end*/", "/*environment:end*/\n" + CSS, 1)
if 'href="#vehicles"' not in s:
    s = s.replace('<li><a href="#environment">Environment</a></li>', '<li><a href="#environment">Environment</a></li><li><a href="#vehicles">Vehicles</a></li>', 1)
    s = s.replace('<a href="#environment">environment</a></dd>', '<a href="#environment">environment</a>; <a href="#vehicles">vehicles</a></dd>', 1)
p.write_text(s, encoding="utf-8")
print("vehicles section:", len(P), "prompts")
