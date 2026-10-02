# spec-design-plan breakdown

How to turn a requirement into design pieces. The requirement is text; its source (a tracker issue, a pasted ticket, a spoken description) does not change the method.

## 1. State check

Run before breaking anything down. DESIGN.md is trusted when all three hold:

1. `DESIGN.md` exists at the project root.
2. `npx @google/design.md lint DESIGN.md` reports zero errors.
3. The Audit (`../../_shared/spec-design/checks.md`) reports no live color defined in code but missing from DESIGN.md. Apply the Liveness check before counting one as live.

If any fails, report which one and hand off to `spec-design-establish`. Resume the breakdown when it hands back.

## 2. Slice the requirement

1. List the UI surfaces the requirement touches: screens, sections, dialogs, components.
2. For each surface, list its states: default, hover/focus, loading, empty, error, disabled, and the responsive breakpoints the project supports.
3. Reuse first: match each surface to existing components (the project's component inventory, design-system docs, or Storybook when present). A new component is a piece of its own.
4. For every piece, name the tokens it needs by role: text, surface, border, state colors, type scale step, spacing step, radius.
5. Mark a gap wherever no token or component covers the need. Do not invent a value to fill it.

Leave backend, data, and logic work out; list it once under "Outside design scope" so the project's own planning flow picks it up.

## 3. Route each piece

| Piece | Route | Blocked until |
|---|---|---|
| Covered by existing tokens and components | `spec-design-apply`, Use | — |
| Needs a new or changed token | `spec-design-apply`, Evolve, then Use | The user approves the DESIGN.md change |
| Contradicts DESIGN.md prose (a Don't, a role rule) | Back to the user | The user decides: change the requirement or change DESIGN.md |
| No design impact | Outside design scope | — |

Order the handoffs: Evolve pieces first, so every Use piece builds on final tokens. When the project has Storybook, each built piece then goes to `spec-design-stories`, which turns its states and visual acceptance criteria into stories.

## 4. Output

```markdown
## Design breakdown: <requirement title>

State: DESIGN.md trusted | handed off to spec-design-establish (<reason>)

| # | Piece | Surface and states | Tokens and components | Gap | Route |
|---|---|---|---|---|---|

### Token changes to approve
- <token>: <value or change> — <why>, <where it applies>

### Acceptance criteria (visual)
- <piece>: <observable result, including states and contrast where relevant>

### Outside design scope
- <item>

### Open decisions
- <question for the user>
```
