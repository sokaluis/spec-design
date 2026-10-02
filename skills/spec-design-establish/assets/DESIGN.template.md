---
version: alpha
name: TODO Product Name
description: TODO One sentence on what the product is and who uses it.
colors:
  # `primary` is required by the spec. Keys are open-ended; keep the project's own names.
  primary: '#000000'
  on-primary: '#ffffff'
  surface: '#ffffff'
  text: '#000000'
typography:
  body-md:
    fontFamily: TODO
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
spacing:
  xs: 4px
  sm: 8px
  md: 16px
rounded:
  sm: 4px
  md: 8px
components:
  # Known sub-tokens: backgroundColor, textColor, typography, rounded, padding, size, height, width.
  # Variants are sibling keys: button-primary, button-primary-hover.
  button-primary:
    backgroundColor: '{colors.primary}'
    textColor: '{colors.on-primary}'
    rounded: '{rounded.md}'
    padding: '{spacing.sm}'
---

# DESIGN.md

<!-- Section order is fixed by the spec. Remove a section only by listing it under `omitted`. -->

## Overview

TODO Brand personality, audience, and the feel of the UI. This is the fallback agents use when no token or rule covers a case.

## Colors

TODO Palette roles and when to use each. Refer to tokens by name; never restate a value that differs from the front matter.

## Typography

TODO Type roles, hierarchy, and pairing rules.

## Layout

TODO Spacing rhythm, grid, containment, and breakpoint behavior.

## Elevation & Depth

TODO Shadow or tonal-layer philosophy. Shadow values live in code, not in the front matter.

## Shapes

TODO Corner radius usage and shape language.

## Components

TODO Per-component guidance: states, variants, and composition rules.

## Do's and Don'ts

- Do TODO
- Don't TODO
