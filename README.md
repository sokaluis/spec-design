# spec-design

Agent skills that make `DESIGN.md` the design source of truth of a frontend project. They follow the [Google `design.md` spec](https://github.com/google-labs-code/design.md) and need no design tool: the inputs are the codebase, the requirement, and your answers.

## The skills

| Skill | Responsibility | Loads when |
| --- | --- | --- |
| `spec-design-plan` | Entry point. Reads a requirement, checks the state of `DESIGN.md`, breaks the work into design pieces, and routes each one. Writes no code. | A ticket, requirement, or user story involves UI |
| `spec-design-establish` | Makes `DESIGN.md` match the real UI: Extract, Seed, Reconcile, Unify. | `DESIGN.md` is missing or does not represent the UI, or on handoff |
| `spec-design-apply` | Makes the code follow `DESIGN.md`: Use, Evolve, Generate. | On handoff, or for a token change in a project with a trusted `DESIGN.md` |
| `spec-design-stories` | Decides which components and states get a Storybook story; Storybook's own skills write them. | On handoff after a component changes, or for a coverage request |

`skills/_shared/spec-design/` holds what the four skills share: the common rules and boundaries (`rules.md`), the audit, liveness, and role checks (`checks.md`), and the read-only audit script (`audit.py`).

## Layout

```text
skills/
  _shared/spec-design/     rules.md, checks.md, audit.py, data files, tests/
  spec-design-plan/        SKILL.md, references/breakdown.md
  spec-design-establish/   SKILL.md, references/, assets/DESIGN.template.md
  spec-design-apply/       SKILL.md, references/workflows.md
  spec-design-stories/     SKILL.md, references/stories.md
```

The skills reference the shared folder with relative paths (`../_shared/spec-design/`), so the five folders must be installed side by side.

## Install

Clone the repository once, then link the skills into each project:

```bash
git clone git@github.com:sokaluis/spec-design.git
./spec-design/install.sh /path/to/project
```

`install.sh` links the five folders into `<project>/.claude/skills/`, so a `git pull` in the clone updates every project. Pass `--copy` to copy them instead, and `--dir <path>` for another skills directory (for example `.opencode/skills`). It refuses to replace anything that already exists.

## Requirements

- Python 3 for the audit script (standard library only).
- Node.js for `npx @google/design.md lint` and `export`.
- Storybook 10.5 or later for `spec-design-stories`, which relies on `npx storybook skills`.

## Audit script

Run it from a project root; it never writes to the project:

```bash
python3 .claude/skills/_shared/spec-design/audit.py --json /tmp/design-audit.json
```

It reports literal colors and their distance to the nearest token, the role each literal is used in, translucent and named colors, stylesheet coverage, framework palettes, and tokens defined in code but missing from `DESIGN.md`.

Tests:

```bash
cd skills/_shared/spec-design && python3 -m unittest discover -s tests
```

## Status

Version 0.5. `spec-design-establish` has been exercised on a real project; `spec-design-plan`, `spec-design-stories`, and the Generate workflow of `spec-design-apply` have not been run end to end yet.

## License

Apache-2.0. See `LICENSE` and `NOTICE` for third-party material.
