#!/usr/bin/env python3
"""Style audit for the spec-design skills. Read-only; Python stdlib only.

Measures how much of a frontend's UI is governed by design tokens:
literal colors and their CIE76 distance to the nearest token, framework
default palettes, duplicated token definitions, and literal vs token usage
for font sizes, spacing, and radii. Shadows are excluded (code-owned).

A literal color is a hex value, an rgb()/rgba() call, or a CSS named color
written as the value of a color-like property. Translucent colors (alpha < 1)
are reported in their own rows with band "translucent": they composite over
whatever is behind them, so they are never compared with opaque tokens.
Each row lists the roles (text, surface, border, icon) the literal is used in.

Usage:
  python3 audit.py [--root .] [--design DESIGN.md] [--src src]
                   [--token-source PATH ...] [--exclude REGEX ...]
                   [--json OUT.json]

Candidate tokens are the DESIGN.md front-matter colors when the file exists,
otherwise the colors defined in detected token sources.
"""
import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

EXTS = ("css", "scss", "sass", "less", "ts", "tsx", "js", "jsx", "mjs", "cjs",
        "vue", "svelte", "html", "svg")
STYLE_EXTS = ("css", "scss", "sass", "less", "vue", "svelte")
SKIP_DIRS = re.compile(r"(^|/)(node_modules|dist|build|coverage|\.next|\.nuxt|\.svelte-kit|"
                       r"storybook-static|out|vendor|\.git)(/|$)")
SKIP_FILES = re.compile(r"\.(test|spec|stories|min)\.|\.d\.ts$|generated|\.gen\.")
TOKEN_SOURCE_NAME = re.compile(
    r"(^|[/_.-])(variables|tokens?|theme|palette|colou?rs?|design-tokens)"
    r"([._-][\w-]*)?\.(s?css|sass|less|[cm]?[jt]sx?|json)$", re.I)
TAILWIND_CONFIG = re.compile(r"(^|/)tailwind\.config\.[cm]?[jt]s$")
SHADOW = re.compile(r"shadow", re.I)

HEX = re.compile(r"(?<![\w&/])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*"
                 r"(?:[,/]\s*([^)]*?)\s*)?\)")
HEX_ALPHA = re.compile(r"(?:rgba?|alpha)\(\s*['\"]?#([0-9a-fA-F]{3,8})\b['\"]?\s*,\s*([^)]*?)\s*\)")
NAMED = {k: v for k, v in json.loads((HERE / "named-colors.json").read_text()).items() if k != "_meta"}
NAMED_RX = re.compile(
    r"(?<![\w$@.#-])(" + "|".join(sorted(NAMED, key=len, reverse=True)) + r")(?![\w(.\[-])", re.I)
CUSTOM_PROP_DEF = re.compile(r"--[\w-]+\s*:\s*[^;]*(#[0-9a-fA-F]{3,8}\b|rgba?\()")
COLOR_DECL = re.compile(r"(?:color|background|border|fill|stroke|outline)[\w-]*\s*:\s*([^;]+);")
OTHER_DECL = {
    "font-size": re.compile(r"font-size\s*:\s*([^;]+);"),
    "spacing": re.compile(r"(?:padding|margin|gap|row-gap|column-gap)(?:-[a-z]+)?\s*:\s*([^;]+);"),
    "radius": re.compile(r"border-(?:[a-z]+-)*radius\s*:\s*([^;]+);"),
}
TOKEN_REF = re.compile(r"var\(--|\$[\w-]+|@[\w-]+|theme\(")

# A color-like property and the role its value plays. Order matters: `borderColor` is a border.
PROP = re.compile(r"([\w$@-]*(?:color|background|border|fill|stroke|outline)[\w-]*)['\"]?\s*([:=])\s*", re.I)
ROLES = (("border", re.compile(r"border|outline", re.I)),
         ("surface", re.compile(r"background|bg", re.I)),
         ("icon", re.compile(r"fill|stroke", re.I)),
         ("text", re.compile(r"color", re.I)))
QUOTED = re.compile(r"""(['"`])([^'"`\n]*)\1""")
VALUE_END = {True: re.compile(r"[;{}]"), False: re.compile(r"[;{},]")}


def norm(raw):
    h = raw.lower()
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    return "#" + h[:6], len(h) == 8 and h[6:] != "ff"


def opaque(alpha):
    """True when an alpha argument is absent or equal to 1. Unreadable alphas count as translucent."""
    a = (alpha or "").strip()
    if not a:
        return True
    try:
        return (float(a[:-1]) / 100 if a.endswith("%") else float(a)) >= 1
    except ValueError:
        return False


def lab(hexv):
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(int(hexv[i:i + 2], 16) / 255) for i in (1, 3, 5))
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(a, b):
    return math.dist(lab(a), lab(b))


def band(d):
    return "exact" if d == 0 else "<2" if d < 2 else "2-10" if d < 10 else ">=10"


def literals(text):
    """Yield (position, hex, translucent) for every hex and rgb() literal."""
    wrapped = []
    for m in HEX_ALPHA.finditer(text):
        hv, has_alpha = norm(m.group(1))
        wrapped.append(m.span())
        yield m.start(), hv, has_alpha or not opaque(m.group(2))
    for m in HEX.finditer(text):
        if any(s <= m.start() < e for s, e in wrapped):
            continue
        hv, has_alpha = norm(m.group(1))
        yield m.start(), hv, has_alpha
    for m in RGB.finditer(text):
        hv = "#%02x%02x%02x" % tuple(min(int(v), 255) for v in m.groups()[:3])
        yield m.start(), hv, not opaque(m.group(4))


def contexts(text, style):
    """Value spans of color-like properties as (start, end, role)."""
    spans = []
    for m in PROP.finditer(text):
        start = m.end()
        if m.group(2) == "=":  # JSX/HTML attribute or assignment: only the string right after it
            q = QUOTED.match(text, start + 1 if text[start:start + 1] == "{" else start)
            end = q.end() if q else start
        else:
            stop = VALUE_END[style].search(text, start)
            end = min(stop.start() if stop else len(text), start + 400)
        role = next((name for name, rx in ROLES if rx.search(m.group(1))), "other")
        spans.append((start, end, role))
    return spans


def color_uses(text, kind):
    """Every literal color in `text` as (hex, translucent, css_name_or_None, role)."""
    style = kind in STYLE_EXTS
    spans = contexts(text, style)
    found = {pos: (hv, translucent, None) for pos, hv, translucent in literals(text)}
    for start, end, _ in spans:
        chunk = text[start:end]
        # Scripts only name a color inside a string; stylesheets write it bare.
        parts = [(0, chunk)] if style else [(q.start(2), q.group(2)) for q in QUOTED.finditer(chunk)]
        for offset, part in parts:
            for m in NAMED_RX.finditer(part):
                name = m.group(1).lower()
                found.setdefault(start + offset + m.start(), (NAMED[name], False, name))
    uses = []
    for pos in sorted(found):
        hv, translucent, name = found[pos]
        inside = [s for s in spans if s[0] <= pos < s[1]]
        uses.append((hv, translucent, name, max(inside)[2] if inside else "other"))
    return uses


def design_md_colors(path):
    """Parse `colors:` from DESIGN.md front matter without a YAML dependency."""
    text = path.read_text(encoding="utf-8")
    parts = text.split("---")
    if len(parts) < 3:
        return {}
    tokens, inside = {}, False
    for line in parts[1].splitlines():
        if re.match(r"^colors\s*:", line):
            inside = True
            continue
        if inside and re.match(r"^\S", line):
            inside = False
        if inside:
            m = re.match(r"^\s+([\w.-]+)\s*:\s*['\"]?#([0-9A-Fa-f]{3,8})\b", line)
            if m:
                tokens[m.group(1)] = norm(m.group(2))[0]
    return tokens


SHADOW_DECL = re.compile(r"[\w-]*shadows?[\w-]*['\"]?\s*[:=]\s*(?:\[[^\]]*\]|[^;,}\n]*)[;,]?", re.I)
NAMED_DEF = re.compile(r"(--[\w-]+|\$[\w-]+|@[\w-]+|[\w-]+)['\"]?\s*:\s*['\"]?#([0-9a-fA-F]{3,8})\b")


def strip_shadows(text):
    """Drop shadow declarations only; the rest of the line stays."""
    return SHADOW_DECL.sub("", text)


def is_token_source(rel, text, forced, found):
    if rel in forced:
        return True
    if TAILWIND_CONFIG.search(rel) or TOKEN_SOURCE_NAME.search(rel):
        return bool(found)  # a name match alone is not enough (e.g. payment "token" types)
    return len(CUSTOM_PROP_DEF.findall(text)) >= 5


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--design", default="DESIGN.md")
    ap.add_argument("--src", default="src", help="directory to scan, relative to root ('.' for all)")
    ap.add_argument("--token-source", action="append", default=[], help="force a file to count as a token source")
    ap.add_argument("--exclude", action="append", default=[], help="regex of relative paths to skip")
    ap.add_argument("--json", help="write the full report as JSON here")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    palettes = {k: set(v) for k, v in json.loads((HERE / "palettes.json").read_text()).items() if k != "_meta"}
    design_path = root / args.design
    design = design_md_colors(design_path) if design_path.exists() else {}
    excludes = [re.compile(x) for x in args.exclude]
    forced = {str(Path(p)) for p in args.token_source}

    base = root / args.src
    files = []
    for ext in EXTS:
        for p in base.rglob(f"*.{ext}"):
            rel = str(p.relative_to(root))
            if SKIP_DIRS.search(rel) or SKIP_FILES.search(p.name) or any(x.search(rel) for x in excludes):
                continue
            if SHADOW.search(p.name):
                continue
            files.append((p, rel))
    tw = [p for p in root.glob("tailwind.config.*")]
    files += [(p, str(p.relative_to(root))) for p in tw]

    uses = defaultdict(list)  # keyed by (hex, translucent)
    names = defaultdict(Counter)
    roles = defaultdict(Counter)
    defs = defaultdict(set)
    translucent_defs = defaultdict(set)
    by_type = Counter()
    color_decl = Counter()
    other = {k: Counter() for k in OTHER_DECL}
    sources = []
    def_names = {}

    for path, rel in files:
        text = strip_shadows(path.read_text(errors="ignore"))
        kind = path.suffix[1:]
        found = color_uses(text, kind)
        if is_token_source(rel, text, forced, found):
            sources.append(rel)
            for hv, translucent, _, _ in found:
                (translucent_defs if translucent else defs)[hv].add(rel)
            for m in NAMED_DEF.finditer(text):
                def_names.setdefault(norm(m.group(2))[0], m.group(1))
            continue
        for hv, translucent, name, role in found:
            key = (hv, translucent)
            uses[key].append(rel)
            roles[key][role] += 1
            by_type[kind] += 1
            if name:
                names[key][name] += 1
        if kind in STYLE_EXTS:
            for m in COLOR_DECL.finditer(text):
                v = m.group(1)
                if HEX.search(v) or RGB.search(v) or NAMED_RX.search(v):
                    color_decl["literal"] += 1
                elif TOKEN_REF.search(v):
                    color_decl["token"] += 1
            for name, rx in OTHER_DECL.items():
                for m in rx.finditer(text):
                    v = m.group(1)
                    if TOKEN_REF.search(v):
                        other[name]["token"] += 1
                    elif re.search(r"\d(px|rem|em)\b", v):
                        other[name]["literal"] += 1

    for name, hv in design.items():
        defs[hv].add(args.design)

    if design:
        candidates, candidate_origin = design, args.design
    else:
        candidates = {def_names.get(hv, hv): hv for hv in defs}
        candidate_origin = "token sources" if candidates else "none"

    rows = []
    for key, where in uses.items():
        hv, translucent = key
        if candidates:
            name, thex = min(candidates.items(), key=lambda kv: delta_e(hv, kv[1]))
            d = delta_e(hv, thex)
        else:
            name, thex, d = None, None, float("inf")
        foreign = sorted(k for k, v in palettes.items() if hv in v and hv not in candidates.values())
        rows.append({
            "hex": hv, "uses": len(where), "files": sorted(set(where)),
            "nearest": name, "nearest_hex": thex,
            "de": None if d == float("inf") else round(d, 1),
            "band": "translucent" if translucent else "no-candidates" if d == float("inf") else band(d),
            "foreign": [] if translucent else foreign, "alpha": translucent,
            "roles": dict(roles[key]),
            "named": sorted(names[key]), "named_uses": sum(names[key].values()),
        })
    rows.sort(key=lambda r: (-r["uses"], r["hex"], r["alpha"]))

    far = [r for r in rows if r["band"] in (">=10", "no-candidates")]
    clusters = []
    for r in far:
        for c in clusters:
            if delta_e(r["hex"], c["hex"]) < 5:
                c["members"].append(r["hex"])
                c["uses"] += r["uses"]
                break
        else:
            clusters.append({"hex": r["hex"], "members": [r["hex"]], "uses": r["uses"]})
    clusters.sort(key=lambda c: -c["uses"])

    duplicated = {hv: sorted(s) for hv, s in defs.items() if len(s) > 1}
    all_defs = sorted(defs)
    near_duplicates = [
        {"a": a, "a_in": sorted(defs[a]), "b": b, "b_in": sorted(defs[b]), "de": round(delta_e(a, b), 1)}
        for i, a in enumerate(all_defs) for b in all_defs[i + 1:] if 0 < delta_e(a, b) < 2
    ]
    missing_in_design = []
    if design:
        for hv, where in defs.items():
            if args.design in where:
                continue
            d = min(delta_e(hv, t) for t in design.values())
            if d >= 2:
                missing_in_design.append({"hex": hv, "defined_in": sorted(where), "de_to_design": round(d, 1)})
        missing_in_design.sort(key=lambda x: -x["de_to_design"])

    bands_unique = Counter(r["band"] for r in rows)
    bands_uses = Counter()
    for r in rows:
        bands_uses[r["band"]] += r["uses"]
    foreign_uses = Counter()
    for r in rows:
        for k in r["foreign"]:
            foreign_uses[k] += r["uses"]
    translucent_rows = [r for r in rows if r["alpha"]]

    report = {
        "design_md": str(design_path.relative_to(root)) if design_path.exists() else None,
        "candidate_tokens": {"origin": candidate_origin, "count": len(candidates)},
        "files_scanned": len(files),
        "token_sources": sorted(sources),
        "literal_colors": {"unique": len(rows), "uses": sum(r["uses"] for r in rows),
                           "by_filetype": dict(by_type), "with_alpha": len(translucent_rows),
                           "named_uses": sum(r["named_uses"] for r in rows),
                           "translucent": {"unique": len(translucent_rows),
                                           "uses": sum(r["uses"] for r in translucent_rows)}},
        "bands": {"unique": dict(bands_unique), "uses": dict(bands_uses)},
        "far_color_clusters": {"count": len(clusters),
                               "used_once": sum(1 for c in clusters if c["uses"] == 1),
                               "top": clusters[:15]},
        "stylesheet_coverage": {"color": dict(color_decl), **{k: dict(v) for k, v in other.items()}},
        "foreign_palette_uses": dict(foreign_uses),
        "duplicated_definitions": duplicated,
        "near_duplicate_definitions": near_duplicates,
        "defined_in_code_missing_in_design_md": missing_in_design,
        "translucent_definitions": [{"hex": hv, "defined_in": sorted(where)}
                                    for hv, where in sorted(translucent_defs.items())],
        "rows": rows,
    }
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1))

    print_summary(report)


def print_summary(r):
    lc, b = r["literal_colors"], r["bands"]
    print(f"DESIGN.md: {r['design_md'] or 'absent'} | candidates: {r['candidate_tokens']}")
    print(f"files scanned: {r['files_scanned']} | token sources: {len(r['token_sources'])}")
    for s in r["token_sources"]:
        print(f"  - {s}")
    print(f"literal colors: {lc['unique']} unique, {lc['uses']} uses {lc['by_filetype']} "
          f"| written as CSS names: {lc['named_uses']} uses")
    print("dE bands (unique / uses):")
    for k in ("exact", "<2", "2-10", ">=10", "no-candidates"):
        if k in b["unique"]:
            print(f"  {k:>13}: {b['unique'][k]:>4} / {b['uses'][k]}")
    print(f"translucent (alpha < 1, outside the bands): "
          f"{lc['translucent']['unique']} unique / {lc['translucent']['uses']} uses")
    fc = r["far_color_clusters"]
    print(f"far colors -> {fc['count']} clusters (dE<5), {fc['used_once']} used once")
    print("stylesheet coverage (token / literal):")
    for k, v in r["stylesheet_coverage"].items():
        print(f"  {k:>9}: {v.get('token', 0)} / {v.get('literal', 0)}")
    print(f"foreign palette uses: {r['foreign_palette_uses'] or 'none'}")
    print(f"duplicated definitions: {len(r['duplicated_definitions'])} | "
          f"near-duplicate definitions: {len(r['near_duplicate_definitions'])} | "
          f"defined in code, missing in DESIGN.md: {len(r['defined_in_code_missing_in_design_md'])} | "
          f"translucent definitions: {len(r['translucent_definitions'])}")
    print("top opaque literal colors (uses, band, nearest token, roles):")
    for row in [x for x in r["rows"] if not x["alpha"]][:10]:
        extra = f" [{','.join(row['foreign'])}]" if row["foreign"] else ""
        used_as = ",".join(f"{k}:{v}" for k, v in sorted(row["roles"].items(), key=lambda kv: -kv[1]))
        print(f"  {row['hex']} x{row['uses']:<3} {row['band']:>5} dE {row['de']} ~{row['nearest']}{extra} "
              f"({used_as})")


if __name__ == "__main__":
    main()
