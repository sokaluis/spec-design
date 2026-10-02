---
name: spec-design-stories
description: "Trigger: spec-design-stories, Storybook story, write stories, story coverage. Decide which stories the UI needs from DESIGN.md; Storybook writes them."
license: Apache-2.0
metadata:
  author: "sokaluis"
  version: "0.6"
---

## Activation Contract

Load on handoff from `spec-design-apply` after a piece creates or changes a component, from `spec-design-plan` when acceptance criteria need stories, or directly when the user asks for stories or story coverage.

## Hard Rules

- Load `../_shared/spec-design/rules.md` first; its rules apply here.
- Own the what, not the how. Decide which components and states get a story; take imports, patterns, tests, and the review workflow from `npx storybook skills write-story` and `npx storybook skills stories`. Never override them.
- Write stories only for live components (Liveness check).
- One concept per story; cover only states that look or behave differently.
- Stories are UI code: generated tokens only, no literal color, font size, spacing, or radius in stories or decorators.
- Do not change a component's behavior or styles; JSDoc on the component and its props is the only edit allowed in its file.
- Never copy token values or DESIGN.md prose into stories or MDX; a token reference page is a generated consumer (`spec-design-apply`, Generate).
- Never install, upgrade, or reconfigure Storybook without the user's approval.

## Decision Gates

| Situation | Action |
|---|---|
| Storybook is not installed | Stop; propose `npx storybook skills setup` and wait for approval |
| Installed but not running | Start it with the project's own script; say it was left running |
| No story test runner | Do not install one; report the interactions as not executed |
| Component is dead | No story; report it |
| Component created or changed by a piece | Add or update the stories for the states that piece touches |
| Coverage request | Inventory live components against existing stories, propose a prioritized list, wait for approval |
| Story exposes a missing token, state, or defect | Hand off to `spec-design-apply` or `spec-design-plan`; do not patch it |

## Execution Steps

1. Run `npx storybook skills stories` and `npx storybook skills write-story`; follow their output for every mechanical decision.
2. Pick the target components and run the Liveness check on each.
3. Derive each component's state list with `references/stories.md`.
4. Write or update the stories through Storybook's workflow, with the agent-facing documentation `references/stories.md` requires.
5. Verify with the Verification steps in `references/stories.md`.

## Output Contract

Return: components covered, stories added or changed with the IDs and review link Storybook's tools returned, whether the interactions were executed, states left out and why, components skipped as dead, and gaps handed off.

## References

- `../_shared/spec-design/rules.md` — rules shared by the spec-design skills, boundaries, and handoff.
- `../_shared/spec-design/checks.md` — Liveness check.
- `references/stories.md` — coverage inventory, state selection, agent-facing documentation, and verification.
