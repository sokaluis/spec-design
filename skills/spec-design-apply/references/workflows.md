# spec-design-apply workflows

DESIGN.md is trusted here: it leads and the code follows. The Role check lives in `../../_shared/spec-design/checks.md`.

## Use — the task builds or restyles UI

1. Read DESIGN.md before writing UI code: front matter for values, prose for intent and for cases no token covers.
2. Consume only the generated tokens (CSS vars, SCSS vars, theme keys). Never write a literal color, font size, spacing, or radius.
3. For a case DESIGN.md does not cover, apply the Overview and Do's and Don'ts. If a new value is really needed, stop and propose it as a DESIGN.md change (Evolve).
4. Before finishing, scan the changed files for new literals.

## Evolve — a token must change or be added

1. State the change and its reason to the user; wait for approval.
2. Edit the value in DESIGN.md, never in a generated file. A new token is named by role and gets a line of prose saying where it applies.
3. Lint.
4. Regenerate every consumer (Generate).
5. Review the diff of generated files; it is the change's visual blast radius.

## Generate (after any DESIGN.md change, or on handoff from spec-design-establish)

1. `npx @google/design.md export --format dtcg DESIGN.md > tokens.json`.
2. Emit every consumer the project needs that the CLI does not produce (SCSS variables, UI-library theme, CSS-in-JS theme), with a small generator script or Style Dictionary. Tailwind v3/v4 can come straight from the CLI.
3. Every generated file starts with a "generated from DESIGN.md — do not edit" header.
4. Remove the hand-written definitions they replace, so each token has one owner.
5. Propose a CI check that regenerates consumers and fails on diff.
