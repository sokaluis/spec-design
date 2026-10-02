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
- Give each prop a JSDoc line in the component's types. Say what a default does when it surprises (a `loading` that starts as `true`).
- These comments are the only edit this skill makes in a component file. Touch no code there.
- Give each story a description that says why someone would use that state, not what is on screen.
- Write content literally in the story or MDX file; values computed at runtime or imported from elsewhere do not reach the manifest.
- Exclude from the manifest, with `tags: ['!manifest']`, anything an agent must not imitate: anti-pattern demonstrations, deprecated components, human-only reference. Propose it for existing stories of dead components instead of deleting them.

## Verification

1. Storybook must be running for previews and the review. When it is installed but not running, start it with the project's own script without changing its configuration, and say in the output that it was left running.
2. Get the story IDs from Storybook's tools. Never trust an empty `stories changed` right after writing a story: in Storybook 10.6 the CLI attached to a running server returned nothing for new stories that `--no-attach` and the MCP tool both reported. Confirm with `stories find-by-component` and the component's path.
3. Run the interactions. `npx storybook tools --help` lists a test tool only when the project has a story test runner.

   | Project | Do |
   |---|---|
   | Has a story test runner | Run it on the stories written or changed |
   | Has none | Do not install one. Optionally check the same assertions with the project's own test runner, leaving no test file behind. Report that Storybook did not execute the interactions and offer the runner as an open decision |

4. Run the project's lint and typecheck on the files touched, and scan them for literals.
5. Publish the review with `review create`, including every story created in this run. Looking at the rendering is the user's check unless a browser tool is available; say which one happened.
6. Report any defect the stories exposed (a wrong `colSpan`, a missing state) as a gap handed off, with file and line. Do not fix it here.

## What a story must not do

- Introduce a literal color, font size, spacing, or radius, in the story or in a decorator.
- Restyle the component to make the story look right; report the gap instead.
- Document tokens by hand. Token values belong to DESIGN.md and reach Storybook only through generated consumers.
- Invent props. Verify every prop with Storybook's documentation tools before using it.
