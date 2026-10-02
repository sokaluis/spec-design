# spec-design checks

Shared by the spec-design skills. `<shared>` is this directory.

## Audit

Run the bundled script from the project root; it is read-only and needs only Python 3:

```bash
python3 <shared>/audit.py --json /tmp/design-audit.json
```

- It excludes shadows, tests, stories, and build output, and detects token sources (theme, palette, variables, tokens, Tailwind config) that define colors.
- Candidate tokens are DESIGN.md colors when it exists, otherwise the colors defined in token sources.
- Use `--src` for a non-`src` layout, `--token-source` to force a file, `--exclude` to skip generated or vendored paths.
- Review the listed token sources before trusting the numbers; a wrong source skews every band.
- A literal is a hex value, an `rgb()`/`rgba()` call, or a CSS named color (`lightgray`, `black`) written as the value of a color-like property. Named colors in scripts count only inside strings.
- Translucent colors (alpha < 1) get their own rows with band `translucent` and stay out of the ΔE bands and clusters. Never map one to an opaque token; a scrim over black is not the `text` color.
- Each row lists `roles`: how many times the literal is used as `text`, `surface`, `border`, `icon`, or `other`.
- Tests: `cd <shared> && python3 -m unittest discover -s tests`. Run them after changing `audit.py`.

## Liveness check (before any add-or-retire decision)

A reference is not a use. Before calling a color or token live:

1. List the files that reference it (`var(--x)`, `$x`, theme path strings such as `'neutral.400'`, and props that consume theme keys implicitly).
2. Follow the importers of each file up to the app entry or the router. Tests and stories do not count.
3. Classify it as live only when at least one chain reaches a mounted route or component. A lazy route that no router registers is dead.
4. Report dead definitions to the user; do not add them to DESIGN.md and do not delete them without asking.

## Role check (before any merge or replacement)

ΔE measures how close two colors look, not whether they mean the same thing. Compare the row's `roles` with the role of the candidate token (its name and its DESIGN.md prose):

| Literal role vs token role | Treatment |
|---|---|
| Same role | Apply the ΔE band rules |
| Different role, any ΔE | User decides: another token of the right role, or a new token |
| Token has no clear role | Ask before the first replacement, then reuse the answer |

## ΔE bands (opaque colors, same role)

| Band | Treatment |
|---|---|
| exact or < 2 | Same token; merge or replace silently |
| 2 – 10 | Probably the same intent; confirm with the user |
| ≥ 10 | Different color; the user decides: new token or replace. Clusters used once are usually replace |
