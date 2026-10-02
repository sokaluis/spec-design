---
name: spec-design-plan
description: "Trigger: UI ticket, requirement, user story, issue, UI task, design breakdown. Break UI work down against DESIGN.md and route it to the spec-design skills."
license: Apache-2.0
metadata:
  author: "sokaluis"
  version: "0.6"
---

## Activation Contract

Load when a requirement, ticket, or user story involves UI, before any code is written. This is the entry point of the spec-design skills; it coordinates `spec-design-establish`, `spec-design-apply`, and `spec-design-stories`.

## Hard Rules

- Load `../_shared/spec-design/rules.md` first; its rules apply here.
- Plan only: write no code and do not edit DESIGN.md. Every piece is handed to the skill that owns it.
- Take the requirement as text from any source and never require a specific tracker. Read one through its tool, read-only, when the user gives a key or asks you to pick a ticket; without a tool, ask for the text.
- A trusted DESIGN.md does not make a surface ready: check the folders the pieces touch and every dimension (color, type, spacing, radius), not only color.
- Break down design impact only. List backend, data, and logic work under "Outside design scope".
- Never fill a gap with an invented value. A piece that needs a new or changed token stays blocked until the user approves the DESIGN.md change.

## Decision Gates

| DESIGN.md state | Action |
|---|---|
| Missing | Hand off to `spec-design-establish` (Extract, or Seed when there is no UI) |
| Lint errors, or live code colors missing from it | Hand off to `spec-design-establish` (Reconcile) |
| Trusted | Break the requirement down |

Route each piece with the table in `references/breakdown.md`: Use, Evolve then Use, back to the user, a Unify piece for a literal-dominated folder, or outside design scope.

## Execution Steps

Follow `references/breakdown.md` for each step.

1. Get the requirement text and restate its goal in one sentence.
2. Run the state check; hand off and stop if it fails.
3. Read DESIGN.md (front matter and prose) and build the component inventory, from Storybook's tools or, when it is not running, from the files.
4. Slice the requirement into pieces, checking every dimension against DESIGN.md.
5. Run the surface readiness check on the folders the pieces touch.
6. Route each piece, then present the breakdown and collect approval for token changes and open decisions.
7. Hand off the approved pieces in order: Unify when approved, Evolve, Use; each built piece then goes to `spec-design-stories` with its acceptance criteria.

## Output Contract

Return the breakdown in the format of `references/breakdown.md`, with every section of its template filled or marked as empty.

## References

- `../_shared/spec-design/rules.md` — rules shared by the spec-design skills, boundaries, and handoff.
- `../_shared/spec-design/checks.md` — Audit, Liveness check, Role check, ΔE bands.
- `references/breakdown.md` — state check, slicing method, routing, and output template.
