# spec-design-plan breakdown

How to turn a requirement into design pieces. The requirement is text; its source (a tracker issue, a pasted ticket, a spoken description) does not change the method.

## 1. Get the requirement

| The user gives | Do |
|---|---|
| The text | Use it as is |
| A tracker key, and a tool for that tracker exists | Read the issue through the tool |
| A request to pick a ticket, and a tracker tool exists | Search for an open item that touches UI, pick one, and say which one and why |
| A key or a pick request, but no tracker tool | Ask for the text |

Reading a tracker is read-only: never transition, comment on, or edit the issue from this skill.

## 2. State check

Run before breaking anything down. DESIGN.md is trusted when all three hold:

1. `DESIGN.md` exists at the project root.
2. `npx @google/design.md lint DESIGN.md` reports zero errors.
3. The Audit (`../../_shared/spec-design/checks.md`) reports no live color defined in code but missing from DESIGN.md. Apply the Liveness check before counting one as live.

If any fails, report which one and hand off to `spec-design-establish`. Resume the breakdown when it hands back.

This check is project-wide and only covers color definitions. A trusted DESIGN.md does not mean the surface a requirement touches follows it; section 4 checks that.

## 3. Slice the requirement

1. List the UI surfaces the requirement touches: screens, sections, dialogs, components.
2. For each surface, list its states: default, hover/focus, loading, empty, error, disabled, and the responsive breakpoints the project supports.
3. Reuse first: match each surface to existing components. Build the inventory from Storybook's tools when Storybook is running; when it is not, or the project has none, from the story files and the component folders. Say which source was used. A new component is a piece of its own.
4. For every piece, name the tokens it needs in every dimension, not only color: text, surface, border, and state colors; type scale step; spacing step; radius.
5. Read the styles the piece touches and compare each font size, spacing value, and radius with the DESIGN.md scales. The audit only measures color distance; for the other properties it counts literals without telling which are off scale.
6. Mark a gap wherever no token or component covers the need. A value between two steps of a scale is a gap; when DESIGN.md prose forbids it, it is a contradiction. Do not invent a value to fill either.

Leave backend, data, and logic work out; list it once under "Outside design scope" so the project's own planning flow picks it up.

## 4. Surface readiness

Run the audit on each folder the pieces touch, not on the whole project (`<shared>` is `../../_shared/spec-design/`):

```bash
python3 <shared>/audit.py --src <folder of the feature or component>
```

Report, per folder, the token/literal coverage of color, font size, spacing, and radius, and the framework-palette uses.

| Coverage of the properties the pieces touch | Readiness | Consequence |
|---|---|---|
| Tokens outnumber literals | Ready | Route the pieces as usual |
| Literals outnumber tokens | Literal-dominated | Add a preparatory piece: Unify scoped to that folder, routed to `spec-design-establish`. The user decides whether it runs first or is skipped |

When the preparatory piece is skipped, `spec-design-apply` still replaces the literals in the rules it touches and adds none; the rest of the folder stays as it is. Say so in the breakdown.

## 5. Route each piece

| Piece | Route | Blocked until |
|---|---|---|
| Covered by existing tokens and components | `spec-design-apply`, Use | — |
| Needs a new or changed token | `spec-design-apply`, Evolve, then Use | The user approves the DESIGN.md change |
| Contradicts DESIGN.md prose (a Don't, a role rule, an off-scale value it forbids) | Back to the user | The user decides: change the requirement or change DESIGN.md |
| Unify of a literal-dominated folder | `spec-design-establish`, Unify | The user decides to run it |
| No design impact | Outside design scope | — |

Order the handoffs: the Unify piece when approved, then Evolve pieces, so every Use piece builds on final tokens. When the project has Storybook, each built piece then goes to `spec-design-stories`, which turns its states and visual acceptance criteria into stories.

## 6. Output

```markdown
## Design breakdown: <requirement title>

Source: <pasted text | tracker key, and why it was picked when the skill chose it>
State: DESIGN.md trusted | handed off to spec-design-establish (<reason>)
Component inventory from: <Storybook tools | story files and component folders>

### Surface readiness
| Folder | Color | Font size | Spacing | Radius | Readiness |
|---|---|---|---|---|---|

### Pieces
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
