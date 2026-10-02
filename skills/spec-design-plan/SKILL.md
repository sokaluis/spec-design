---
name: spec-design-plan
description: "Trigger: UI ticket, requirement, user story, issue, UI task, design breakdown. Break UI work down against DESIGN.md and route it to the spec-design skills."
license: Apache-2.0
metadata:
  author: "sokaluis"
  version: "0.5"
---

## Activation Contract

Load when a requirement, ticket, or user story involves UI, before any code is written. This is the entry point of the spec-design skills; it coordinates `spec-design-establish`, `spec-design-apply`, and `spec-design-stories`.

## Hard Rules

- Load `../_shared/spec-design/rules.md` first; its rules apply here.
- Plan only: write no code and do not edit DESIGN.md. Every piece is handed to the skill that owns it.
- Take the requirement as text from any source. Never require a specific tracker; read one through its tool only when the user gives a key and the tool exists, otherwise ask for the text.
- Break down design impact only. List backend, data, and logic work under "Outside design scope".
- Never fill a gap with an invented value. A piece that needs a new or changed token stays blocked until the user approves the DESIGN.md change.
- If DESIGN.md is not trusted, stop and hand off to `spec-design-establish` before breaking down.

## Decision Gates

| DESIGN.md state | Action |
|---|---|
| Missing | Hand off to `spec-design-establish` (Extract, or Seed when there is no UI) |
| Lint errors, or live code colors missing from it | Hand off to `spec-design-establish` (Reconcile) |
| Trusted | Break the requirement down |

| Piece | Route |
|---|---|
| Covered by existing tokens and components | `spec-design-apply`, Use |
| Needs a new or changed token | `spec-design-apply`, Evolve then Use, after approval |
| Contradicts DESIGN.md prose | Back to the user |
| No design impact | Outside design scope |

## Execution Steps

1. Get the requirement text and restate its goal in one sentence.
2. Run the state check in `references/breakdown.md`; hand off and stop if it fails.
3. Read DESIGN.md (front matter and prose) and the project's component inventory.
4. Slice the requirement into pieces and route each one, following `references/breakdown.md`.
5. Present the breakdown and collect approval for token changes and open decisions.
6. Hand off the approved pieces to `spec-design-apply`, Evolve pieces first; each built piece then goes to `spec-design-stories` with its acceptance criteria.

## Output Contract

Return the breakdown in the format of `references/breakdown.md`: state check result, one row per piece with its route, token changes to approve, visual acceptance criteria, items outside design scope, and open decisions.

## References

- `../_shared/spec-design/rules.md` — rules shared by the spec-design skills, boundaries, and handoff.
- `../_shared/spec-design/checks.md` — Audit, Liveness check, Role check, ΔE bands.
- `references/breakdown.md` — state check, slicing method, routing, and output template.
