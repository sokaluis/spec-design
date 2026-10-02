---
name: spec-design-apply
description: "Trigger: spec-design-apply, change design token, add design token, regenerate tokens from DESIGN.md. Build UI with DESIGN.md tokens and evolve them."
license: Apache-2.0
metadata:
  author: "sokaluis"
  version: "0.6"
---

## Activation Contract

Load on handoff from `spec-design-plan` or `spec-design-establish`, or directly when the user names a token change or a small UI edit in a project whose DESIGN.md is trusted. Applies to any stack.

## Hard Rules

- Load `../_shared/spec-design/rules.md` first; its rules apply here.
- DESIGN.md leads and the code follows. If DESIGN.md is missing or not trusted, stop and hand off to `spec-design-establish`.
- Use generated tokens only; never add a literal color, font size, spacing, or radius. If no token fits, stop and propose a DESIGN.md change.
- Change a token only in DESIGN.md, after the user approves it; then lint and regenerate. Never edit a generated file.
- Never redefine a token from what the code happens to contain; that is `spec-design-establish` work.
- A requirement that has not been broken down goes to `spec-design-plan` first.

## Decision Gates

| Task | Mode |
|---|---|
| Builds or restyles UI | Use |
| A token value must change or a token must be added | Evolve, then Generate |
| DESIGN.md changed, or generated consumers are missing or stale | Generate |

## Execution Steps

1. Read DESIGN.md: front matter for values, prose for intent.
2. Run that mode's workflow from `references/workflows.md`.
3. After any DESIGN.md change: lint, regenerate consumers, and review the generated diff.
4. Scan the changed files for new literals before finishing.
5. Run the project's tests, typecheck, and lint for the files touched.
6. When a component was created or visibly changed and the project has Storybook, hand off to `spec-design-stories`.

## Output Contract

Return: mode, files created or changed, tokens used or changed, lint result, the generated diff and the before/after value comparison when consumers were regenerated, values left hand-written and why, the result of the new-literals scan, and open decisions for the user.

## References

- `../_shared/spec-design/rules.md` — rules shared by the spec-design skills, boundaries, and handoff.
- `../_shared/spec-design/checks.md` — Role check and ΔE bands for any literal replacement.
- `references/workflows.md` — step-by-step Use, Evolve, and Generate.
