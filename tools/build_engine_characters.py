#!/usr/bin/env python3
r"""Builds the "Characters" section of engine.html (look development) and writes it between
<!--characters:start--> and <!--characters:end--> markers.

Prompts are read from the game repo's prompt files (never copied by hand):
  python tools/build_engine_characters.py [path-to-game-repo]
Game repo path: argument, KINDLING_GAME env var, or ../KindlingDiscovery.
Images: img/characters/<character>-<step>.webp (thumb) and -full.webp (opens in a new window).
A missing image shows a "Generate" placeholder."""
import html, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KINDLING_GAME", ROOT.parent / "KindlingDiscovery"))
PR = GAME / "Production" / "Design" / "prompts"

STEPS = [("concept", "Concept"), ("plate", "Plate"), ("intro", "Photoreal intro"), ("turntable", "Turntable (PBR)"), ("clay", "Turntable (clay)"), ("poster", "Poster"), ("closeup", "4K close-up")]
CHARS = [("tomas", "Tomas", "The hero"), ("ines", "Ines", "His twin sister"), ("king", "The King", "Episode 1 boss"), ("tally", "Tally", "The Charge-walker companion")]
NOTE = {
    ("ines", "concept"): "Prompt not recorded in the repo.",
}


def read(name):
    return (PR / name).read_text(encoding="utf-8")


def line(text, prefix):
    for ln in text.splitlines():
        if ln.startswith(prefix):
            return ln[len(prefix):].strip()
    raise KeyError(prefix)


def section(text, heading_start, stop="\n## "):
    i = text.index(heading_start)
    j = text.find(stop, i + 5)
    return text[i:j if j != -1 else None]


def edit_block(sec):
    m = re.search(r"^(EDIT[^\n]*\n?.*?)(?=\n\n|\n## |\Z)", sec, re.S | re.M)
    return m.group(1).strip() if m else sec.strip()


plates = read("character-plates-prompt-pack.md")
closeup = read("closeup-prompts.md")
def cline(prefix):
    for ln in closeup.splitlines():
        if ln.startswith(prefix):
            return ln.split("): ", 1)[1].strip() if ")" in prefix or "(" in ln.split(":")[0] else ln[len(prefix):].strip()
    raise KeyError(prefix)
intro = read("character-intro-prompts.md")
poster = read("live-action-poster-prompts.md")
hero = read("hero-plate-prompt-pack.md")
turn = read("turntable-prompts.md")
TURN = line(turn, "TURNTABLE v4 (standard; Steven approved the King result 2026-11-27, \"good\"; inputs: poster, then 4K close-up; Nano Banana):")
CLAY = line(turn, "CLAY (attach the chosen PBR turntable; edit, not a new image):")

TAIL = line(plates, "TAIL:")
APOSE = line(plates, "APOSE:")
FRAME = line(intro, "COMMON FRAME:")

# --- common prompts, one per step -----------------------------------------------------
a2 = line(hero, "A2:")
concept_common = ("Cinematic portrait, original character concept art, painterly, in the style of the canon style master (ConceptTomas). "
                  + re.search(r"(Large-format cinema camera look.*)$", a2).group(1)
                  + " Rule: Ora light is green (lantern, Tally, the King's gadget); ordinary fire and village window light stay amber.")
tomas_clean = line(poster, "TOMAS:") if False else None
clean = poster[poster.index("## REALISM-FIRST CLEAN SET"):]
tomas_poster = line(clean, "TOMAS:")
poster_open = tomas_poster.split(". ")[0] + "."
poster_close = re.search(r"(Natural soft light, soft shadows.*)$", tomas_poster).group(1)
_ct = next(ln for ln in closeup.splitlines() if ln.startswith("TOMAS:")).split(":", 1)[1].strip()
COMMON = {
    "concept": concept_common,
    "plate": "APOSE: " + APOSE + "\n\nTAIL: " + TAIL,
    "intro": FRAME,
    "poster": poster_open + " [character and scene] " + poster_close,
    "turntable": "Attach the poster (body) and the 4K close-up (face). " + TURN,
    "clay": "Edit of the chosen PBR turntable. " + CLAY,
    "closeup": "Using the [character] in the reference image, create a tight, full-frame close-up of the head and shoulders, shot like a live-action feature film still. [Same character: face, hair, costume.] Calm, focused expression, eyes locked on the camera, eyes in the upper third, sharp with clear catchlights. Real skin: pores, freckles, natural uneven tone. Low golden sun as a warm rim light, soft cool fill. Background softly out of focus. Large-format cinema lens, shallow depth of field, fine film grain, true-to-life colour, no beauty retouching look. (Ines and the King also attach the Tomas close-up as a second reference: same look, framing, lens, lighting and grade.) The 4K file is then a local upscale, with no prompt.",
}

# --- per character --------------------------------------------------------------------
def p_plate(key):
    t = line(plates, key + ":") if key != "INES" else re.search(r"^INES \([^)]*\): (.*)$", plates, re.M).group(1)
    return t.replace("[APOSE]", APOSE).replace("+ TAIL", TAIL).strip(), t.replace("[APOSE]", "").replace("+ TAIL", "").replace("  ", " ").replace("Same for", "Model sheet for").strip()


def p_intro(key):
    t = line(intro, key + ":")
    return t.replace("[COMMON FRAME, machine: head and chest fill the left half]", FRAME).replace("[COMMON FRAME]", FRAME), re.sub(r"^\[[^\]]*\]\s*", "", t)


P = {}
lines_tomas_edit = edit_block(section(hero, "## Hero key art: lantern turns green"))
P[("tomas", "concept")] = (a2 + "\n\nThen, edit round: " + lines_tomas_edit, a2)
m11 = edit_block(section(hero, "## King round 11"))
P[("king", "concept")] = ("(Final of eleven rounds; base is the previous round's image.)\n" + m11, m11)
t5 = edit_block(section(hero, "## Tally round 5, simplified"))
P[("tally", "concept")] = (t5 + "\n(The canon image has no ears.)", t5)
for ch, key in (("tomas", "HERO"), ("ines", "INES"), ("king", "KING"), ("tally", "TALLY")):
    nk = {"tomas": "TOMAS", "ines": "INES", "king": "THE KING", "tally": "TALLY"}[ch]
    P[(ch, "plate")] = p_plate(key)
    if ch != "tomas":
        base = p_plate("HERO")[0]
        P[(ch, "plate")] = ("Base sheet prompt (written for Tomas):\n" + base + "\n\nAdapt it for this character:\n" + P[(ch, "plate")][0], P[(ch, "plate")][1])
    P[(ch, "intro")] = p_intro(nk)
    ck = {"tomas": "TOMAS", "ines": "INES", "king": "KING", "tally": "TALLY"}[ch]
    ct = next(ln for ln in closeup.splitlines() if ln.startswith(ck + " ") or ln.startswith(ck + ":"))
    ct = ct.split("): ", 1)[1] if "): " in ct.split(":")[0] + "):" and ct.startswith(ck + " (") else ct.split(":", 1)[1]
    ct = ct.strip()
    P[(ch, "closeup")] = (ct, ct)
    tk = {"tomas": "TOMAS", "ines": "INES", "king": "KING", "tally": "TALLY"}[ch]
    tx = next(ln for ln in turn.splitlines() if ln.startswith("- " + tk + ":")).split(":", 1)[1].strip()
    P[(ch, "turntable")] = ("TURNTABLE: " + TURN + "\n\n" + tk + ": " + tx, tx)
    P[(ch, "clay")] = (CLAY, CLAY)
    ptxt = line(clean, nk + ":")
    P[(ch, "poster")] = (ptxt, ptxt)


def snip(t, n=150):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


E = html.escape


def card(ch, st, label, gen_hint=False):
    f = ROOT / "img" / "characters" / f"{ch}-{st}.webp"
    full = f"img/characters/{ch}-{st}-full.webp"
    name = dict((c[0], c[1]) for c in CHARS).get(ch, ch)
    if (ch, st) in P:
        full_p, short = P[(ch, st)]
        pr = (f'<details class="pr"><summary><span class="snip">{E(snip(short))}</span><span class="more">Full prompt</span></summary>'
              f'<pre>{E(full_p)}</pre></details>')
    else:
        pr = f'<p class="np">{E(NOTE.get((ch, st), "Prompt not recorded in the repo."))}</p>'
    if f.exists():
        im = (f'<a class="im" href="{full}" target="_blank" rel="noopener" title="Open full size in a new window">'
              f'<img src="img/characters/{ch}-{st}.webp" alt="{E(name)}, {E(label.lower())}" loading="lazy"></a>')
    else:
        im = '<div class="im gen" role="img" aria-label="Not generated yet"><span>Generate</span></div>'
    k4 = '<p class="np">4K file: local upscale, no prompt.</p>' if st in ("poster", "closeup") and f.exists() else ""
    return f'<li class="cc"><div class="cl">{E(label)}</div>{im}{pr}{k4}</li>'


rows = []
for ch, name, role in CHARS:
    cards = "".join(card(ch, st, lab) for st, lab in STEPS)
    rows.append(f'<div class="crow" id="c-{ch}"><h3>{E(name)} <small>{E(role)}</small></h3><ol class="cstrip">{cards}</ol><div class="rp" aria-live="polite" hidden></div></div>')
blank = "".join(f'<li class="cc"><div class="cl">{E(lab)}</div><div class="im gen" role="img" aria-label="Placeholder, not generated yet"><span>Generate</span></div><p class="np">Common prompt for this step, plus the new character\'s brief.</p></li>' for _, lab in STEPS)
rows.append(f'<div class="crow next" id="c-next"><h3>Next character <small>Placeholder</small></h3><ol class="cstrip">{blank}</ol></div>')

common_html = "".join(
    f'<li><details class="pr cp"><summary><b>{E(lab)}</b><span class="snip">{E(snip(COMMON[st], 210))}</span><span class="more">Full prompt</span></summary><pre>{E(COMMON[st])}</pre></details></li>'
    for st, lab in STEPS)

SECTION = f'''<!--characters:start-->
<section id="characters"><div class="wrap">
  <h2>Look development: characters</h2>
  <p class="lede">Every character goes through seven steps: concept, plate, photoreal intro, a PBR turntable and its clay render (the input for 3D mesh generation, new and experimental), poster and 4K close-up. Click an image to open it full size in a new window. Click "Full prompt" under it to read the prompt.</p>
  <h3 class="ch3">Common prompts</h3>
  <p class="o">Each step starts from one shared prompt. A character adds only its own description.</p>
  <ol class="cprompts">{common_html}</ol>
  {"".join(rows)}
  <div class="todo"><h3 class="ch3">Next to do: sharpen the images</h3>
  <p class="o">The posters and close-ups were generated at about 843 by 1264 to 1024 by 1536 pixels. The 4K files are a local upscale: they are 4K by size but soft at 100% zoom, and cannot invent detail.</p>
  <ol class="nexts">
    <li><b>Make the Tally close-up.</b> The prompt is written and shown above. The poster prompt was blocked earlier, so it avoids the words "robot" and "visor".</li>
    <li><b>Run the quality-pass prompt.</b> Attach each poster or close-up in the image generator and ask for an IMAX-quality, HDR-look re-render that keeps the pose, face and props. Then run the 4K and HDR10 pass on the result. The prompt is in <code>Production/Design/prompts/closeup-prompts.md</code>.</li>
    <li><b>Test a generative upscaler on one face.</b> Magnific and Topaz can add real detail where the local pass cannot. Compare both against the local pass at 100% on Tomas's close-up. Both are paid, so the spend cap is Steven's to set.</li>
    <li><b>Test a free local upscaler.</b> Real-ESRGAN is the free option. It is not installed in the workspace yet. Same one-face comparison.</li>
    <li><b>Generate larger originals where the tool allows it.</b> More native pixels beat any upscaler. Check the maximum output size in each generator.</li>
    <li><b>Pick one method and write it down as a standard.</b> The winner becomes the 4K step for every character, so the Next character row follows the same path.</li>
  </ol></div>
</div></section>
<!--characters:end-->'''

CSS = '''/*characters:start*/
.ch3{font-size:18px;margin:26px 0 4px}
ol.cprompts{list-style:none;margin:10px 0 0;padding:0;border:0;display:grid;gap:8px;max-width:980px}
.pr{font-size:13.5px}.pr summary{cursor:pointer;list-style:none;display:block}.pr summary::-webkit-details-marker{display:none}
.pr .snip{color:var(--slag-2);display:block;line-height:1.4}
.pr .more{display:inline-block;margin-top:3px;font-weight:600;color:var(--slag);text-decoration:underline;text-underline-offset:2px}
.pr[open] .more::after{content:" (open)"}
.pr pre{white-space:pre-wrap;word-break:break-word;font:12.5px/1.5 ui-monospace,Consolas,monospace;background:#fff;border:1px solid var(--ash-2);padding:10px;margin:8px 0 0;max-height:340px;overflow:auto}
.cp{background:#EEF0EE;padding:10px 14px;border-left:6px solid var(--ember)}.cp summary b{display:block;font-size:15px;margin-bottom:2px}
.crow{margin-top:34px}.crow h3{font-size:22px;margin:0 0 10px}.crow h3 small{font-weight:400;font-size:14px;color:var(--slag-2);margin-left:8px}
ol.cstrip{list-style:none;margin:0;padding:0;border:0;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:12px;align-items:start}
.cc{background:#EEF0EE;padding:8px 8px 10px}.cl{font-size:13px;font-weight:700;margin-bottom:6px}
.im{display:flex;align-items:center;justify-content:center;height:170px;background:var(--ash-2);overflow:hidden}
a.im{cursor:zoom-in}a.im:focus-visible{outline:3px solid var(--ember)}
.im img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.im.gen{background:repeating-linear-gradient(45deg,#E3E6E3 0 10px,#D5D9D5 10px 20px);border:2px dashed #9AA5AD}
.im.gen span{font-weight:700;color:var(--slag-2);background:#EEF0EE;padding:6px 14px;border:2px solid var(--slag-2)}
.np{font-size:13px;color:var(--slag-2);margin:8px 0 0}.cc .pr{margin-top:8px}
.crow.next .cl{color:var(--slag-2)}
.todo{margin-top:40px;max-width:900px}.todo ol.nexts{margin:12px 0 0;padding-left:22px;border:0;list-style:decimal}.todo li{margin:0 0 8px;font-size:15px}.todo code{font-size:13px;background:#EEF0EE;padding:1px 5px}
.rp{margin-top:10px;background:#fff;border:1px solid var(--ash-2);border-left:6px solid var(--ember);padding:12px 16px;max-width:980px}
.rp b{display:block;font-size:14px;margin-bottom:6px}
.rp pre{white-space:pre-wrap;word-break:break-word;font:13px/1.55 ui-monospace,Consolas,monospace;margin:0;max-height:420px;overflow:auto}
.js .cc .pr pre{display:none}
.cc .pr[open]{outline:2px solid var(--ember);outline-offset:3px}
@media (max-width:1300px){ol.cstrip{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:900px){ol.cstrip{grid-template-columns:repeat(2,minmax(0,1fr))}}
/*characters:end*/'''

JS = """<script>
(function(){document.documentElement.classList.add('js');
document.querySelectorAll('.crow').forEach(function(row){var panel=row.querySelector('.rp');if(!panel)return;
row.querySelectorAll('.cc details.pr').forEach(function(d){d.addEventListener('toggle',function(){
if(d.open){row.querySelectorAll('.cc details.pr').forEach(function(o){if(o!==d)o.open=false;});
var lab=d.closest('.cc').querySelector('.cl').textContent;var who=row.querySelector('h3').firstChild.textContent.trim();
panel.innerHTML='';var b=document.createElement('b');b.textContent=who+': '+lab+' prompt';var pre=document.createElement('pre');pre.textContent=d.querySelector('pre').textContent;
panel.appendChild(b);panel.appendChild(pre);panel.hidden=false;}
else if(!row.querySelector('.cc details.pr[open]')){panel.hidden=true;}});});});})();
</script>"""

SECTION = SECTION.replace("<!--characters:end-->", JS + "\n<!--characters:end-->")

p = ROOT / "engine.html"
s = p.read_text(encoding="utf-8")
if "<!--characters:start-->" in s:
    s = re.sub(r"<!--characters:start-->.*?<!--characters:end-->", lambda m: SECTION, s, flags=re.S)
else:
    s = s.replace('<section id="pbr">', SECTION + '\n<section id="pbr">', 1)
if "/*characters:start*/" in s:
    s = re.sub(r"/\*characters:start\*/.*?/\*characters:end\*/", lambda m: CSS, s, flags=re.S)
else:
    s = s.replace("</style>\n<script src=\"shared/sitenav.js\"", CSS + "\n</style>\n<script src=\"shared/sitenav.js\"", 1)
# sidebar and page nav
if 'href="#characters"' not in s:
    s = s.replace('<li><a href="#pbr">PBR workflow</a></li>', '<li><a href="#characters">Characters</a></li><li><a href="#pbr">PBR workflow</a></li>', 1)
p.write_text(s, encoding="utf-8")
print("wrote characters section:", sum(1 for c in CHARS for st, _ in STEPS if (c[0], st) in P), "prompts;", len(list((ROOT / 'img' / 'characters').glob('*-full.webp'))), "images")
