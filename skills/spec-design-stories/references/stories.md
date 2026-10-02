# spec-design-stories reference

Storybook is the executable examples layer of the design system: agents and people read it to learn how a component is used. This file covers what to put in it. How to write a story (imports, CSF format, play functions, mocking, review links) comes from the installed Storybook: `npx storybook skills write-story` and `npx storybook skills stories`.

## Coverage inventory (for a coverage request)

1. List the project's components: shared components first, then feature components reused in more than one place.
2. Run the Liveness check (`../../_shared/spec-design/checks.md`) on each. Drop dead ones from the list and report them.
3. Map each live component to its existing stories with Storybook's tools (find stories by component); never derive story IDs from file names.
4. Prioritize the gaps: components named in DESIGN.md's Components section, then components touched by open work, then the rest by number of importers.
5. Propose the list with one line per component (states to cover, why it ranks there) and wait for approval. Do not write stories for the whole list in one pass.

## State selection

Build the state list from three sources, in this order:

1. The piece's row in the `spec-design-plan` breakdown: its surface, states, and visual acceptance criteria. Each criterion maps to a story.
2. DESIGN.md's Components section and front matter `components`: every variant it names (for example `button-primary`, `button-outlined`) is a story of the owning component.
3. Props and conditions that change what the user sees or can do: loading, empty, error, disabled, long or translated content, permission or role.

Then cut the list down:

| Candidate state | Keep it? |
|---|---|
| Differs in appearance or behavior from every kept story | Yes |
| Differs only by a value that renders the same way (another label, another id) | No |
| Combination of two kept states with no new behavior | No |
| Required by an acceptance criterion | Yes, even if it looks close to another |

Never merge several concepts into one story (`SizesAndVariants`); an agent reading it cannot tell which prop produced which result.

## Agent-facing documentation

A story is read by agents through the component manifest, which is built by static analysis.

- Give the component a JSDoc summary above its export: what it is for and when to use it instead of the neighbouring component.
- Give each prop a JSDoc line in the component's types.
- Give each story a description that says why someone would use that state, not what is on screen.
- Write content literally in the story or MDX file; values computed at runtime or imported from elsewhere do not reach the manifest.
- Exclude from the manifest, with `tags: ['!manifest']`, anything an agent must not imitate: anti-pattern demonstrations, deprecated components, human-only reference. Propose it for existing stories of dead components instead of deleting them.

## What a story must not do

- Introduce a literal color, font size, spacing, or radius, in the story or in a decorator.
- Restyle the component to make the story look right; report the gap instead.
- Document tokens by hand. Token values belong to DESIGN.md and reach Storybook only through generated consumers.
- Invent props. Verify every prop with Storybook's documentation tools before using it.
