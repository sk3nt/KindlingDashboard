#!/usr/bin/env python3
r"""Builds the "Look development: style guide" section of engine.html between
<!--style:start--> and <!--style:end--> (placed before the characters section).
Palette values were measured from the village square film frame (median of a 10 px patch per swatch).
Draft: Steven approves; the repo style guide (docs/style-guide.md, gated) is not changed by this."""
import html, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
E = html.escape

GROUPS = [
    ("Base: sky, stone and ground", "Most of every frame. Warm, muted, never pure white or black.", [
        ("Dawn sky", "#E6C3D1"), ("Sun haze", "#FDD2D0"), ("Honey stone, lit", "#B2816B"), ("Honey stone, mid", "#986953"),
        ("Terracotta", "#74402A"), ("Cobble", "#6C5956")]),
    ("Greens: paint and plants", "Deep, desaturated greens. Teal paint belongs to the square only (props list, L3).", [
        ("Shutter teal", "#254144"), ("Door green", "#3D402E"), ("Clipped shrub", "#2F2E16")]),
    ("Accents: textiles and flowers", "Small, saturated, and few. In the square they cover about 8 percent of the frame.", [
        ("Cloth teal", "#0F4B52"), ("Cloth orange", "#AF571A"), ("Cloth magenta", "#8E1449"), ("Cloth mustard", "#BE8610"),
        ("Cloth blue", "#204E77"), ("Banner red", "#9A2329"), ("Bougainvillea", "#541C2D"), ("Paper lantern", "#B88E67")]),
    ("Ora: the one magic colour", "Only for Ora light: Tomas's lantern, Tally's core and LED, the Mayor's gem. Measured from the canon lantern plate.", [
        ("Ora green", "#7EE41E")]),
]
RULES = [
    ("Render", "Fully photoreal, with a stylised post-process on top (decided 2026-11-25). The palette here is the target after the post-process."),
    ("Light", "Dawn: a low warm sun behind the scene, pink and peach sky, thin haze, soft shadows. Ordinary fire and window light are amber."),
    ("Proportion", "Warm stone and sky carry the frame. Saturated accents stay small, about a tenth of the frame at most, and cluster where the eye should go."),
    ("Ora green", "Green light means Ora and nothing else. No green lamps, no green sky, no green glow on distant walls."),
    ("Per location", "Each location keeps its own accent colour pair and signature props (props list). The same textile hue is never the main accent in two neighbouring locations."),
    ("Materials", "Honey limestone, lime plaster, terracotta roofs and pots, weathered timber, worn stone steps and cobbles. Clean and lived-in, never grimy."),
    ("Characters", "Costumes read against the stone: Tomas in teal stripes, Ines in cream, the Mayor in red, orange and gold patchwork, Tally in olive and orange."),
]
import os, sys
GAME = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KINDLING_GAME", ROOT.parent / "KindlingDiscovery"))
LTXT = (GAME / "Production" / "Design" / "prompts" / "look-direction-prompts.md").read_text(encoding="utf-8")
LCOMMON = re.search(r"^COMMON: (.*)$", LTXT, re.M).group(1)
LOOKS = [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(r"^([A-D]): ([^.]+)\. (.*)$", LTXT, re.M)]
_s1 = re.search(r"^S1 \(([^)]*)\): (.*)$", LTXT, re.M)
if _s1:
    LOOKS.append(("S1", "Ora optics test", _s1.group(2) + " (" + _s1.group(1).split(";", 1)[-1].strip() + ")"))
LNOTE = {"A": "Recommended base: cheap in Unity (bloom, halation, grade, grain).", "C": "Recommended story layer on top of A: the struggling and thriving village.",
         "B": "Risk: washed out on bright screens; ledges lose contrast.", "D": "Strongest identity, hardest to build.", "S1": "Tests the Ora signature, not a grade."}
SIGNATURE = [
    ("First light", "The world lives mostly in dawn and the golden hour, because Tomas carries the first light. Midday and night are rare and meaningful."),
    ("Ora has its own optics", "Ora green is the only saturated light, with its own halo, flicker and green caustics on nearby stone; nothing else glows like it."),
    ("Filmed, not rendered", "Halation, grain and a gentle lens roll-off on every frame: the camera has a personality."),
    ("Colour as progress", "Faded and dusty where life has gone out of a place; bright cloth and flowers where it comes back."),
    ("Hand-made world", "Crooked, patched, repaired surfaces and textiles; nothing factory-clean or symmetrical."),
]
KEYS = [
    ("Village dawn (base key)", "The square as measured above. Warm, pink and peach, accents bright.", "Have it"),
    ("Midday", "Higher contrast, shorter shadows, bluer sky, stone near white. Accents look flatter.", "To write"),
    ("Dusk", "Deeper orange sun, long shadows, windows and lanterns turn on in amber.", "To write"),
    ("Night", "Stone drops to blue grey, accents almost vanish; amber windows and Ora green carry the frame.", "To write"),
    ("Weather: overcast and rain", "Soft light, wet dark stone with reflections, accents become the brightest thing.", "To write"),
    ("Castle", "Cooler grey stone, the Mayor's red and gold only, harder shadows, wider sky.", "To write"),
    ("Beach and tide pools", "Pale sand, sea teal, Ora glow in the pools at dawn.", "To write"),
    ("Woodland areas 1 to 5", "One key each, so the five feel different: light through canopy, own accent.", "To write"),
    ("Village struggling, then thriving", "Story state: at first, faded cloth, empty stalls, few lit windows. As the village thrives and farms Ora: fresh colour, busy stalls, more light.", "To write"),
    ("Interiors", "Window light as key, warm bounce, darker corners.", "To write"),
]
CONST = ["Ora green means Ora, in every key", "The materials and the shape language", "Gameplay cues: climbable edges, interactables and hazards read the same everywhere",
         "The accent cap: saturated colour stays a small share of the frame", "Character costume colours"]
MISSING = [
    ("Shape language", "Soft, crooked, hand-made shapes for the village; straight, heavy, angular shapes for the castle; each character's silhouette readable at game distance."),
    ("Value and readability", "Where the darkest and lightest values sit, so the player, the path and the next climbable edge always read first."),
    ("Gameplay cues", "One visual language for what can be climbed, used or picked up, and for danger, so no on-screen markers are needed."),
    ("Scale", "Doors, steps, ledges and ropes sized to the 1.80 m hero and the parkour moves (with Daniel)."),
    ("Materials", "The material library (S6): which stone, plaster, timber, metal and cloth, wear levels and texel density per tier."),
    ("Camera and lens", "Game camera field of view and height versus the cinematic look of the film frames."),
    ("VFX", "How Ora glow, dust, water, fire and impacts look (Vera)."),
    ("Bystanders", "Villagers dressed in muted colours so the four main characters stand out."),
    ("Reference boards", "Approved and rejected images for each rule, side by side."),
    ("UI and type", "Later, once there is a game to put it on."),
]
DONT = ["Stock game props: barrels, crates, sacks, chests (Steven, 2026-11-25)", "Neon or fully saturated colour over large areas", "Grey, cold or blue-hour light", "Green used for anything that is not Ora",
        "Repeated banner sets across locations", "Text, signs or logos in the world"]


def sw(name, hx):
    return (f'<li class="sw"><span class="chip" style="background:{hx}"></span><b>{E(name)}</b><code>{hx}</code></li>')


groups = "".join(f'<div class="swg"><h4>{E(t)}</h4><p class="o">{E(d)}</p><ul class="sws">{"".join(sw(*s) for s in ss)}</ul></div>' for t, d, ss in GROUPS)
rules = "".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in RULES)
signature = "".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in SIGNATURE)
looks = "".join(
    f'<li class="cc"><div class="cl">{E(k)}. {E(t)}</div><div class="im gen" role="img" aria-label="Not generated yet"><span>Generate</span></div>'
    f'<p class="np">{E(LNOTE.get(k, ""))}</p><details class="pr"><summary><span class="snip">{E(d[:130])}…</span><span class="more">Full prompt</span></summary><pre>{E("COMMON: " + LCOMMON + chr(10) + chr(10) + k + ": " + t + ". " + d)}</pre></details></li>'
    for k, t, d in LOOKS)
keys = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in KEYS)
consts = "".join(f"<li>{E(x)}</li>" for x in CONST)
missing = "".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in MISSING)
donts = "".join(f"<li>{E(x)}</li>" for x in DONT)

SECTION = f'''<!--style:start-->
<section id="style"><div class="wrap">
  <h2>Look development: style guide</h2>
  <p class="lede">The look in one place: palette, light and rules for every character, location and prop. Paper-Ink is retired; this is the photoreal direction. The palette is measured from the village square film frame. This is a draft for Steven; the repo style guide changes only when he accepts it.</p>
  <h3 class="ch3">What makes the photoreal look ours</h3>
  <p class="o">Photoreal alone is not a look, so these five signatures carry the identity, whatever the grade.</p>
  <ul class="srules">{signature}</ul>
  <h3 class="ch3">Grade directions: generate, then pick one</h3>
  <p class="o">Each direction is an image-generator edit of the same village square plate, so they compare like for like. Prompts in the game repo, <code>Production/Design/prompts/look-direction-prompts.md</code>. My recommendation: A as the base grade, with C as the story layer.</p>
  <ol class="cstrip lookdirs">{looks}</ol>
  <h3 class="ch3">Palette</h3>
  <div class="stylehero"><a class="im" href="img/environment/v1-full.webp" target="_blank" rel="noopener" title="Open full size in a new window"><img src="img/environment/v1.webp" alt="The village square at dawn, the palette source" loading="lazy"></a>
  <p class="o">Palette source: the empty village square plate. Click to open full size.</p></div>
  {groups}
  <h3 class="ch3">Rules</h3><ul class="srules">{rules}</ul>
  <h3 class="ch3">Never</h3><ul class="srules">{donts}</ul>
  <h3 class="ch3">Variation: look keys</h3>
  <p class="o">The world does not look like the square all the time. Each place, time of day, weather and story state gets a look key: one reference frame plus how it shifts from the base key. Astrid, the Art Director, writes the keys, Steven approves them, and Astrid judges every new frame against the key it belongs to.</p>
  <div class="tablewrap"><table class="keys"><thead><tr><th>Key</th><th>How it shifts from the base</th><th>State</th></tr></thead><tbody>{keys}</tbody></table></div>
  <p class="o" style="margin-top:12px"><b>Stays the same in every key:</b></p><ul class="srules">{consts}</ul>
  <h3 class="ch3">Still to write</h3><ul class="srules">{missing}</ul>
  <div class="todo"><h3 class="ch3">Next to do</h3><ol class="nexts">
    <li><b>Steven generates directions A to D and S1</b> on the village square plate, then picks one (or a mix).</li>
    <li><b>Steven approves or changes the palette and rules.</b></li>
    <li><b>Astrid writes the first look keys:</b> night and the castle first (most different from the base), then the struggling and thriving village.</li>
    <li><b>Write it into the repo style guide</b> (a gated file: Steven accepts the change, and earlier gate results are re-run).</li>
    <li><b>Lena builds the post-process grade</b> that turns the photoreal render into this palette, tested on one Unity scene per quality tier.</li>
    <li><b>Astrid adds a palette check</b> to her look gate: accent share and Ora-green misuse, measured on each new frame.</li>
  </ol></div>
</div></section>
<!--style:end-->'''

CSS = '''/*style:start*/
.stylehero{max-width:900px;margin-top:16px}.stylehero .im{height:auto;max-height:420px}
.swg{margin-top:26px}.swg h4{font-size:17px;margin:0 0 2px}
ul.sws{list-style:none;margin:10px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.sw{background:#EEF0EE;padding:8px}.sw .chip{display:block;height:64px;border:1px solid rgba(0,0,0,.15);margin-bottom:6px}
.sw b{display:block;font-size:14px}.sw code{font-size:12.5px;color:var(--slag-2)}
table.keys{border-collapse:collapse;width:100%;max-width:980px;margin-top:10px;font-size:14.5px}table.keys th,table.keys td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--ash-2)}@media (min-width:700px){table.keys td:first-child{white-space:nowrap}}
ul.srules{margin:8px 0 0;padding-left:20px;max-width:900px}ul.srules li{margin:0 0 6px;font-size:15px}
ol.lookdirs{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}ol.lookdirs .im{height:160px}
/*style:end*/'''

p = ROOT / "engine.html"
s = p.read_text(encoding="utf-8")
if "<!--style:start-->" in s:
    s = re.sub(r"<!--style:start-->.*?<!--style:end-->", lambda m: SECTION, s, flags=re.S)
else:
    s = s.replace("<!--characters:start-->", SECTION + "\n<!--characters:start-->", 1)
if "/*style:start*/" in s:
    s = re.sub(r"/\*style:start\*/.*?/\*style:end\*/", lambda m: CSS, s, flags=re.S)
else:
    s = s.replace("/*characters:start*/", CSS + "\n/*characters:start*/", 1)
if 'href="#style"' not in s:
    s = s.replace('<li><a href="#characters">Characters</a></li>', '<li><a href="#style">Style guide</a></li><li><a href="#characters">Characters</a></li>', 1)
    s = s.replace('<dt>See</dt><dd><a href="#characters">', '<dt>See</dt><dd><a href="#style">Style guide</a>; <a href="#characters">', 1)
p.write_text(s, encoding="utf-8")
print("style section written")
