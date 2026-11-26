#!/usr/bin/env python3
r"""Builds two look-development sections of engine.html, laid out like the characters section
(one row per item, left to right: reference crop, production sheet, live-action film still):
  <!--structures:start--> ... <!--structures:end-->  from prompts/structure-prompts.md
  <!--props:start--> ... <!--props:end-->            from prompts/prop-prompts.md
Both sit after the environment section. Reference crops are read from the game repo
(Production/Design/structure-refs, prop-refs) and written as web images to img/structures, img/props.
  python tools/build_engine_assets.py [path-to-game-repo]"""
import html, os, re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KINDLING_GAME", ROOT.parent / "KindlingDiscovery"))
DES = GAME / "Production" / "Design"
E = html.escape


def snip(t, n=140):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def webimg(src, dst_dir, key):
    dst_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    for suf, L in (("", 720), ("-full", 2200)):
        r = im.copy(); r.thumbnail((L, L)); r.save(dst_dir / f"{key}{suf}.webp", "WEBP", quality=82)


def details(label, text, short=None):
    return (f'<details class="pr"><summary><span class="snip">{E(snip(short or text))}</span><span class="more">{E(label)}</span></summary><pre>{E(text)}</pre></details>')


def build(kind, md, refdir, imgdir, title, lede, anchor):
    txt = (DES / "prompts" / md).read_text(encoding="utf-8")
    common = {k: v for k, v in re.findall(r"^COMMON (SHEET|FILM|REF): (.*)$", txt, re.M)}
    prule = re.search(r"^PHOTO SHEET RULE: (.*)$", txt, re.M)
    prule = prule.group(1) if prule else ""
    items = re.findall(r"^([SP][-A-Z]*\d+) ([^|]+?) \| REF: ([^|]+?) \| (.*)$", txt, re.M)
    rows = []
    for iid, name, ref, desc in items:
        key = iid.lower()
        m = re.match(r"(\S+\.png) \(([^)]*)\)", ref)
        ph = re.match(r"photo (\S+) \(([^)]*)\)", ref)
        sheet_extra = ""
        if ph:
            sheet_extra = "\n\n" + prule
            local = next((DES / refdir / f"{iid}{ext}" for ext in (".jpg", ".png", ".jpeg") if (DES / refdir / f"{iid}{ext}").exists()), None)
            if local:
                webimg(local, ROOT / "img" / imgdir, key)
                refcell = (f'<a class="im" href="img/{imgdir}/{key}-full.webp" target="_blank" rel="noopener" title="Open full size in a new window">'
                           f'<img src="img/{imgdir}/{key}.webp" alt="{E(name)}, real photo reference" loading="lazy"></a>')
            else:
                refcell = '<div class="im gen photo" role="img" aria-label="Real photo, not downloaded yet"><span>Real photo</span></div>'
            refcell += (f'<p class="np">Real photo reference, for shape and materials only. <a href="{E(ph.group(1))}" target="_blank" rel="noopener">Open it on Wikimedia Commons</a> '
                        f'and attach it to the sheet prompt; licence and author are on that page.</p>')
        elif m and (DES / refdir / m.group(1)).exists():
            webimg(DES / refdir / m.group(1), ROOT / "img" / imgdir, key)
            refcell = (f'<a class="im" href="img/{imgdir}/{key}-full.webp" target="_blank" rel="noopener" title="Open full size in a new window">'
                       f'<img src="img/{imgdir}/{key}.webp" alt="{E(name)}, reference crop" loading="lazy"></a>'
                       f'<p class="np">Crop from the film frame: {E(m.group(2))}. Attach it to the sheet prompt.</p>')
        else:
            place = re.sub(r"^none \(|\)$", "", ref)
            refcell = ('<div class="im gen" role="img" aria-label="No reference yet"><span>Generate</span></div>'
                       f'<p class="np">No reference in the film frames yet ({E(place)}). Generate one, then crop it.</p>'
                       + details("Reference prompt", common["REF"] + "\n\nPlace: " + place + ".\n" + kind.capitalize() + ": " + desc, "Reference in " + place + ": " + desc))
        gen = '<div class="im gen" role="img" aria-label="Not generated yet"><span>Generate</span></div>'
        sheet = common["SHEET"] + sheet_extra + "\n\n" + kind.capitalize() + ": " + desc
        film = common["FILM"] + "\n\n" + kind.capitalize() + ": " + desc
        rows.append(f'<div class="crow" id="{anchor}-{key}"><h3>{E(iid)} {E(name)}</h3><ol class="cstrip astrip">'
                    f'<li class="cc"><div class="cl">Reference</div>{refcell}</li>'
                    f'<li class="cc"><div class="cl">Sheet</div>{gen}{details("Full prompt", sheet, "Sheet from the crop: " + desc)}</li>'
                    f'<li class="cc"><div class="cl">Live-action film still</div>{gen}{details("Full prompt", film, "In place, film quality: " + desc)}</li></ol></div>')
    have = sum(1 for _, _, r, _ in items if ".png" in r.split(" (")[0])
    photos = sum(1 for _, _, r, _ in items if r.startswith("photo "))
    return (f'<!--{anchor}:start-->\n<section id="{anchor}"><div class="wrap">\n  <h2>{E(title)}</h2>\n'
            f'  <p class="lede">{E(lede)} {have} of {len(items)} have a reference crop from our film frames, {photos} a real photo from Wikimedia Commons, and {len(items) - have - photos} still need one generated. Prompts in the game repo, <code>Production/Design/prompts/{md}</code>.</p>\n'
            + "".join(rows) + f'\n</div></section>\n<!--{anchor}:end-->')


STRUCT = build("structure", "structure-prompts.md", "structure-refs", "structures", "Look development: key structures",
               "Each structure runs left to right: a reference crop from our film frames, the production sheet for modelling, then a live-action film still of it in place.", "structures")
PROPS = build("prop", "prop-prompts.md", "prop-refs", "props", "Look development: props",
              "Each prop runs left to right: a reference crop from our film frames, the production sheet for modelling, then a live-action film still of it in place. No stock game props: no barrels, crates, sacks or chests.", "props")
CSS = '''/*assets:start*/
ol.astrip{grid-template-columns:repeat(3,minmax(0,1fr))}
.im.gen.photo{background:repeating-linear-gradient(45deg,#E6E1D6 0 10px,#DAD3C4 10px 20px)}
#structures code,#props code{word-break:break-all}
@media (max-width:700px){ol.astrip{grid-template-columns:1fr}}
/*assets:end*/'''

p = ROOT / "engine.html"
s = p.read_text(encoding="utf-8")
for anchor, sec, after in (("structures", STRUCT, "<!--environment:end-->"), ("props", PROPS, "<!--structures:end-->")):
    if f"<!--{anchor}:start-->" in s:
        s = re.sub(rf"<!--{anchor}:start-->.*?<!--{anchor}:end-->", lambda m: sec, s, flags=re.S)
    else:
        s = s.replace(after, after + "\n" + sec, 1)
if "/*assets:start*/" in s:
    s = re.sub(r"/\*assets:start\*/.*?/\*assets:end\*/", lambda m: CSS, s, flags=re.S)
else:
    s = s.replace("/*environment:end*/", "/*environment:end*/\n" + CSS, 1)
if 'href="#structures"' not in s:
    s = s.replace('<li><a href="#environment">Environment</a></li>', '<li><a href="#environment">Environment</a></li><li><a href="#structures">Key structures</a></li><li><a href="#props">Props</a></li>', 1)
p.write_text(s, encoding="utf-8")
print("structures and props sections written")
