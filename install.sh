#!/usr/bin/env bash
# Install the spec-design skills into a project.
# Usage: ./install.sh [--copy] [--dir <skills-dir>] <project-dir>
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mode="link"
skills_dir=".claude/skills"
project=""

while [ $# -gt 0 ]; do
  case "$1" in
    --copy) mode="copy" ;;
    --dir) skills_dir="${2:?--dir needs a path}"; shift ;;
    -h|--help) echo "Usage: ./install.sh [--copy] [--dir <skills-dir>] <project-dir>"; exit 0 ;;
    *) project="$1" ;;
  esac
  shift
done

[ -n "$project" ] || { echo "error: project directory missing" >&2; exit 1; }
[ -d "$project" ] || { echo "error: $project is not a directory" >&2; exit 1; }

target="$(cd "$project" && pwd)/$skills_dir"
mkdir -p "$target"

for skill in _shared spec-design-plan spec-design-establish spec-design-apply spec-design-stories; do
  dest="$target/$skill"
  # _shared may already exist for other skills: install only our subfolder there.
  if [ "$skill" = "_shared" ]; then
    mkdir -p "$dest"
    dest="$dest/spec-design"
    src="$here/skills/_shared/spec-design"
  else
    src="$here/skills/$skill"
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    echo "skip: $dest already exists" >&2
    continue
  fi
  if [ "$mode" = "copy" ]; then
    cp -R "$src" "$dest"
  else
    ln -s "$src" "$dest"
  fi
  echo "$mode: $dest"
done
