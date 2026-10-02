# spec-design-establish workflows

Inputs are the codebase and the user's answers. No design tool is required in any mode. The Audit, Liveness check, Role check, and ΔE bands live in `../../_shared/spec-design/checks.md`.

## Extract — UI code exists, no DESIGN.md

Goal: turn what the code actually ships into a consolidated DESIGN.md, then make it the source of truth.

1. Read `package.json` and pick the guide in `frameworks/` that matches the stack. Theme and token files show intent; component styles show what shipped. Read both.
2. Run the Audit.
3. Run the Liveness check on every cluster, then treat live colors by ΔE band after the Role check.
4. Treat framework-palette matches and duplicated definitions as consolidation targets, not as tokens to keep.
5. Propose the token set: one name per cluster, named by role (`primary`, `surface`, `text-muted`), not by hue. Do the same for type sizes, spacing steps, and radii. Show it to the user before writing.
6. Ask the user for the qualitative language: brand personality, mood, what the UI must not feel like. This fills Overview and the Do's and Don'ts.
7. Write DESIGN.md from `../assets/DESIGN.template.md`. Values in the front matter; rules and rationale in prose. Keep shadows, breakpoints, z-index, and motion out of the front matter.
8. Lint. Fix every error; review warnings.
9. From this point DESIGN.md owns the values. Hand off to `spec-design-apply` for Generate, then run Unify.

## Reconcile — DESIGN.md exists but does not match the UI

Goal: make the existing DESIGN.md represent the real UI before anyone trusts it. Edit it; never replace it wholesale without asking.

1. Run the Audit against the existing DESIGN.md.
2. Report the gap: bands, translucent colors, stylesheet coverage per property, framework-palette uses, duplicated and near-duplicate definitions, and `defined_in_code_missing_in_design_md`.
3. Run the Liveness check on each token defined in code but missing in DESIGN.md. For each live one, ask: add it to DESIGN.md, or retire it and point its uses to an existing token of the same role.
4. For live clusters at ΔE ≥ 10, ask the same question, largest cluster first.
5. Propose the DESIGN.md diff (new or renamed tokens only) and apply it after approval. Lint.
6. Hand off to `spec-design-apply` for Generate, then run Unify. When DESIGN.md is trusted, hand back to the caller.

## Seed — no UI code yet

Goal: a DESIGN.md exists before the first component, so the agent never falls back to framework defaults.

1. Interview the user in one round: product and audience, brand personality (3 adjectives), anti-references, primary color or brand asset, type preference (serif, sans, mono; one or two families), density (compact, comfortable, spacious), corner style (sharp, soft, pill).
2. Derive a minimal token set: `primary` plus its on-color, surface and text roles, success/warning/error, one type scale (display, headline, title, body, label), a 4 px or 8 px spacing ladder, two or three radii.
3. Check contrast of every text/background pair against WCAG AA before writing.
4. Write DESIGN.md from the template and mark it `<!-- SEED -->` under the title.
5. Lint, then hand off to `spec-design-apply` for Generate. The first components are built there in Use mode.
6. A seed is refined by editing DESIGN.md (Evolve, in `spec-design-apply`), never by re-extracting from code.

## Unify (after Extract or Reconcile, once consumers are generated)

1. Replace opaque literals at ΔE < 2 with the matching generated token, only when the Role check passes.
2. List everything else with file, value, roles, nearest token, and ΔE for the user. Translucent literals are listed, never replaced by an opaque token.
3. Run the project's tests, typecheck, and lint; visual changes should be imperceptible.

When `spec-design-plan` hands over a single folder, scope both the audit (`--src <folder>`) and the replacements to it, and hand back when done.
