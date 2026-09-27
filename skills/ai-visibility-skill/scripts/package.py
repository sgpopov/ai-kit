#!/usr/bin/env python3
"""Package this skill for the platform you want to install it on.

Two archive layouts exist, and picking the wrong one is the usual reason an
upload is rejected:

  nested — SKILL.md sits under a top-level folder (`ai-visibility/SKILL.md`).
           Claude Code, Claude Desktop, claude.ai, ChatGPT, Codex. OpenAI
           states the requirement explicitly: "upload a .zip that contains a
           single top-level folder".
  flat   — SKILL.md sits at the archive root. Perplexity Computer requires
           this; it derives the skill folder from the `name` in frontmatter.

The nested archives are structurally identical — `--openai` exists so the
download is obvious to someone installing into ChatGPT, not because the bytes
differ.

Usage:
    python scripts/package.py                 # build every target
    python scripts/package.py --flat          # Perplexity only
    python scripts/package.py --openai        # ChatGPT / Codex only
    python scripts/package.py --out ../dist

Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git", "evals"}
EXCLUDE_GLOBS = ("*.pyc", "*.zip", "*.skill", ".DS_Store", "Thumbs.db", ".gitignore")

SKILL_ROOT = Path(__file__).resolve().parent.parent


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        raise SystemExit("error: SKILL.md has no YAML frontmatter block")
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            fields[km.group(1)] = km.group(2).strip()
    return fields


def validate(skill_root: Path) -> str:
    """Check the things every platform agrees on before building anything."""
    skill_md = skill_root / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit(f"error: no SKILL.md in {skill_root}")

    fm = read_frontmatter(skill_md)
    name = fm.get("name", "")
    desc = fm.get("description", "")

    if not name:
        raise SystemExit("error: frontmatter is missing `name`")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise SystemExit(f"error: name {name!r} must be lowercase with hyphens, no spaces")
    if name != skill_root.name:
        raise SystemExit(f"error: name {name!r} must match the folder name "
                         f"{skill_root.name!r} — several platforms require this")
    if not desc:
        raise SystemExit("error: frontmatter is missing `description` — it is what "
                         "makes the skill trigger")
    if len(desc) < 40:
        print(f"  warning: description is only {len(desc)} chars; a thin "
              f"description triggers unreliably")

    print(f"  name: {name}")
    print(f"  description: {len(desc)} chars")
    return name


def collect_files(skill_root: Path) -> list[Path]:
    out = []
    for p in sorted(skill_root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(skill_root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if any(rel.match(g) for g in EXCLUDE_GLOBS):
            continue
        out.append(p)
    return out


def build(skill_root: Path, files: list[Path], target: Path, nested: bool) -> Path:
    prefix = skill_root.name + "/" if nested else ""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            arc = prefix + f.relative_to(skill_root).as_posix()
            z.write(f, arc)
    return target


def verify(archive: Path, nested: bool, skill_name: str) -> None:
    """Open what we just wrote and confirm it is actually installable."""
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        bad = z.testzip()
        if bad:
            raise SystemExit(f"error: corrupt entry {bad} in {archive.name}")
        expected = f"{skill_name}/SKILL.md" if nested else "SKILL.md"
        if expected not in names:
            raise SystemExit(f"error: {archive.name} has no {expected} "
                             f"(found: {names[:3]})")
        if any("\\" in n for n in names):
            raise SystemExit(f"error: {archive.name} contains Windows path "
                             f"separators; it will not extract on Linux")
        size_mb = archive.stat().st_size / 1_048_576
        if size_mb > 10:
            print(f"  warning: {size_mb:.1f} MB exceeds the 10 MB limit some "
                  f"platforms enforce")
    print(f"  {archive.name:34} {len(names):2} files  "
          f"{archive.stat().st_size / 1024:6.1f} KB  ok")


TARGETS = {
    "nested": ("{name}.zip", True, "claude.ai — Settings › Capabilities › Skills"),
    "skill": ("{name}.skill", True, "Claude Code / Desktop — install file"),
    "openai": ("{name}-chatgpt-codex.zip", True,
               "ChatGPT / Codex — sidebar › Skills › Upload"),
    "flat": ("{name}-perplexity.zip", False,
             "Perplexity Computer — perplexity.ai/computer/skills"),
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(SKILL_ROOT.parent),
                    help="output directory (default: alongside the skill folder)")
    for key in TARGETS:
        ap.add_argument(f"--{key}", action="store_true",
                        help=f"build only this target ({TARGETS[key][2]})")
    args = ap.parse_args()

    selected = [k for k in TARGETS if getattr(args, k)] or list(TARGETS)
    out_dir = Path(args.out).resolve()

    print(f"packaging {SKILL_ROOT.name}")
    name = validate(SKILL_ROOT)
    files = collect_files(SKILL_ROOT)
    print(f"  {len(files)} files\n")

    for key in selected:
        pattern, nested, purpose = TARGETS[key]
        archive = build(SKILL_ROOT, files, out_dir / pattern.format(name=name), nested)
        verify(archive, nested, name)
        print(f"  {'':34} → {purpose}\n")

    print(f"written to {out_dir}")


if __name__ == "__main__":
    main()
