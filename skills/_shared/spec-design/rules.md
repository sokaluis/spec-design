# spec-design shared rules

These rules bind every spec-design skill. Each skill loads this file before acting.

## Ownership

- Inputs are the codebase, the requirement text, and the user's answers. Never require Figma, Stitch, or any design tool.
- Once DESIGN.md exists, it is the design source of truth. Its front matter owns `colors`, `typography`, `spacing`, `rounded`; code consumers are generated from it and never hand-edited.
- Generate in one direction only: DESIGN.md → code. To change a token, edit DESIGN.md, lint, regenerate.
- Shadows, breakpoints, z-index, motion, and component implementation values stay in code.
- DESIGN.md follows the spec's 8 sections in order (`spec-design-establish/assets/DESIGN.template.md`), not Stitch's or impeccable's layouts.

## Safety

- Run `npx @google/design.md lint DESIGN.md` after every DESIGN.md change; `broken-ref` blocks completion.
- Never change a brand color to fix contrast; report it as a product decision.
- Never overwrite an existing DESIGN.md or edit AGENTS.md/CLAUDE.md without asking.
- Propose new or renamed tokens to the user and wait for approval before writing them.

## Trust

- A reference is not a use: confirm a color's consumers are reachable from the app entry or router before treating it as live (`checks.md`, Liveness check).
- ΔE says two colors look alike, not that they mean the same thing: merge or replace only within the same role (`checks.md`, Role check).
- Never map a translucent color to an opaque token.

## Boundaries and handoff

| Skill | Owns | Never does |
|---|---|---|
| `spec-design-plan` | Reading a requirement, checking DESIGN.md state, breaking the work into design pieces, routing each piece | Write code or edit DESIGN.md |
| `spec-design-establish` | Making DESIGN.md match the real UI: Extract, Seed, Reconcile, Unify | Build features |
| `spec-design-apply` | Making code follow DESIGN.md: Use, Evolve, Generate | Redefine tokens from code |
| `spec-design-stories` | Deciding which components and states get a Storybook story, and keeping stories useful to agents | Explain how to write a story (Storybook's own skills do), or change a component |

Source-of-truth layers, never duplicated across each other: rules and token values in DESIGN.md, component API in the code's types, examples in Storybook, process in these skills.

Hand off by loading the target skill and passing it the piece, the mode, and the decisions already approved. A skill that hits work it does not own stops and hands off; it does not continue on its own.

DESIGN.md is trusted when it exists, lints with zero errors, and the audit reports no live color defined in code but missing from it. Anything else goes to `spec-design-establish` first.
