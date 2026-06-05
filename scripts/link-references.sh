#!/usr/bin/env bash

set -euo pipefail

# Copies all reference markdown files in the repository to ~/.claude/references,
# so that they can be used by the local Claude CLI.

REPO="$(cd "$(dirname "$0")/.." && pwd)"

DEST="$HOME/.claude/references"

resolve_path() {
  python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$1"
}

# If ~/.claude/references is a symlink that resolves into this repo, we'd end up
# copying files back into the repo's own references/ tree. Detect and bail out
# instead of polluting the working copy.
if [ -L "$DEST" ]; then
  resolved="$(resolve_path "$DEST")"
  case "$resolved" in
    "$REPO"|"$REPO"/*)
      echo "error: $DEST is a symlink into this repo ($resolved)." >&2
      echo "Remove it (rm \"$DEST\") and re-run; the script will copy files into a real dir." >&2
      exit 1
      ;;
  esac
fi

mkdir -p "$DEST"

find "$REPO/references" -type f -name '*.md' -print0 |
while IFS= read -r -d '' reference_md; do
  name="$(basename "$reference_md")"
  target="$DEST/$name"

  cp -f "$reference_md" "$target"
  echo "copied $name -> $target"
done