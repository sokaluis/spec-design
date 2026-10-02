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

A project that already has a generator runs it and goes straight to step 6. The other steps set the generator up the first time.

1. Export from DESIGN.md with `npx @google/design.md export --format <format> DESIGN.md`, pinned to one CLI version: `css-vars` for CSS custom properties, `css-tailwind` or `json-tailwind` for Tailwind, `dtcg` for everything else. Feed the output to the generator; do not commit an intermediate `tokens.json` that nothing reads.
2. Emit every consumer the CLI does not produce (SCSS variables, UI-library theme, CSS-in-JS theme) with a small generator script that has tests, or with Style Dictionary. Compare the export with DESIGN.md first: when the export drops a value (DTCG loses unitless line heights), leave that group hand-written and report it instead of generating a lossy copy.
3. Every generated file starts with a "generated from DESIGN.md — do not edit" header, and comes out already formatted: run the project's formatter and linter on it. If a pre-commit hook would rewrite a generated file, fix the generator, not the file, or the check in step 7 fails after every commit.
4. Give each token one owner without renaming the codebase:

   | Hand-written definition | Do |
   |---|---|
   | Same name as a generated token | Delete it |
   | Another name, same value, same role (Role check) | Keep the name and make it an alias of the generated token |
   | Same value but another role, or no token for it | Leave the literal and report it as an open decision |

5. Prove the wiring is value-neutral. Before it, record the resolved value of every existing custom property and of the theme the app builds; after it, compare. Expect zero differences, ignoring letter case in hex values.
6. When the run follows an Evolve, the differences must be exactly the approved token changes; anything else is a defect of the wiring.
7. Give the generator a check mode that regenerates in memory and fails when a file on disk differs, and prove it catches a hand edit. Propose it for CI together with the generator's tests; do not edit the CI workflow without asking.
