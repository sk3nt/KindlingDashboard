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
DL = re.search(r"^DESIGN LANGUAGE \(paste into every vehicle prompt\): (.*)$", TXT, re.M).group(1)
P = dict(re.findall(r"^(QB-[A-Z]+): (.*)$", TXT, re.M))
NEXT = [(re.split(r"[:(]| for ", n, maxsplit=1)[0].strip().removeprefix("A ").capitalize(), n.strip()) for n in re.findall(r"^- (A [^.(]+)", TXT.split("## Next vehicles", 1)[1].split("##", 1)[0], re.M)]
STEPS = [("CONCEPT", "Concept"), ("SHEET", "Sheet"), ("ACTION", "In action"), ("DETAILS", "Details")]


def snip(t, n=140):
    t = re.sub(r"\s+", " ", re.sub(r"\[DESIGN LANGUAGE\]\s*", "", t)).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def im(key, alt):
    if (IMG / f"{key}.webp").exists():
        return (f'<a class="im" href="img/vehicles/{key}-full.webp" target="_blank" rel="noopener" title="Open full size in a new window">'
                f'<img src="img/vehicles/{key}.webp" alt="{E(alt)}" loading="lazy"></a>')
    return '<div class="im gen" role="img" aria-label="Not generated yet"><span>Generate</span></div>'


cards = "".join(
    f'<li class="cc"><div class="cl">{E(lab)}</div>{im("quad-" + st.lower(), "Quad bike, " + lab.lower())}'
    f'<details class="pr"><summary><span class="snip">{E(snip(P["QB-" + st]))}</span><span class="more">Full prompt</span></summary>'
    f'<pre>{E(P["QB-" + st].replace("[DESIGN LANGUAGE]", DL))}</pre></details></li>' for st, lab in STEPS)
refs = "".join(f'<li class="cc"><div class="cl">{E(l)}</div><a class="im" href="img/characters/{k}-full.webp" target="_blank" rel="noopener" title="Open full size in a new window"><img src="img/characters/{k}.webp" alt="{E(l)}" loading="lazy"></a></li>'
               for k, l in [("tally-plate", "Tally plate: design language"), ("tally-poster", "Tally poster: photoreal look"), ("tally-concept", "Tally concept")])
nexts = "".join(f'<div class="crow next"><h3>{E(n)} <small>Proposed</small></h3><p class="o">{E(d)}</p><ol class="cstrip vstrip">'
                + "".join(f'<li class="cc"><div class="cl">{E(l)}</div><div class="im gen" role="img" aria-label="Not generated yet"><span>Generate</span></div></li>' for _, l in STEPS)
                + "</ol></div>" for n, d in NEXT)

SECTION = f'''<!--vehicles:start-->
<section id="vehicles"><div class="wrap">
  <h2>Look development: vehicles</h2>
  <p class="lede">Vehicles are alien-built and supplied through the orbiting space station; only Tomas and Ines ride them (Steven, 2026-11-25). They share Tally's design language and run on Ora. The quad bike comes first. Prompts in the game repo, <code>Production/Design/prompts/vehicle-prompts.md</code>.</p>
  <h3 class="ch3">Design references: Tally</h3>
  <ol class="cstrip envref">{refs}</ol>
  <h3 class="ch3">Design language</h3>
  <ol class="cprompts"><li><details class="pr cp"><summary><b>Pasted into every vehicle prompt</b><span class="snip">{E(snip(DL, 220))}</span><span class="more">Full text</span></summary><pre>{E(DL)}</pre></details></li></ol>
  <div class="crow" id="v-quad"><h3>Quad bike <small>First vehicle</small></h3><ol class="cstrip vstrip">{cards}</ol></div>
  {nexts}
  <div class="todo"><h3 class="ch3">Next to do</h3><ol class="nexts">
    <li><b>Generate the quad bike concept</b> with the Tally plate, the Tally poster and the village square attached.</li>
    <li><b>The sheet</b> once Steven approves the concept; Theo checks it for modelling, Daniel for scale in the lanes.</li>
    <li><b>Nora, for Steven:</b> are these the same aliens who made Tally, and how does a vehicle reach the ground from a station without power?</li>
    <li><b>Steven picks the next vehicle</b> from the proposals.</li>
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
print("vehicles section:", len(P), "quad prompts,", len(NEXT), "proposed vehicles")
