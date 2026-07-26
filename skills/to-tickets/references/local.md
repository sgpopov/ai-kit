# Local Markdown Backend

## Directory convention

Issues live alongside PRDs in a shared directory. The default layout is:

```
<issues-root>/
├── prds/
│   └── my-feature.md        ← PRD file
└── issues/
    ├── 001-slice-title.md
    ├── 002-another-slice.md
    └── ...
```

If the project uses a different layout (e.g. a single flat `docs/` folder, or `tickets/` instead of `issues/`), ask the user to confirm the paths before proceeding.

## Locating the PRD

Ask the user for the path to the PRD file if not already provided, or list candidate files:

```bash
find . -type f -name "*.md" | grep -i prd | head -20
```

Read the file contents before drafting slices.

## Numbering issues

Use a zero-padded incrementing prefix for filenames so issues sort correctly:

```
001-<slug>.md
002-<slug>.md
```

Determine the next available number by listing existing issue files:

```bash
ls <issues-dir>/ | sort | tail -5
```

## Creating issues

Write each approved slice as a markdown file at `<issues-dir>/<NNN>-<slug>.md`.

### Parent PRD reference format

In the issue body, reference the parent PRD as a relative markdown link:

```markdown
## Parent PRD

[my-feature](../prds/my-feature.md)
```

### Blocked-by reference format

Use relative markdown links to the blocker files:

```markdown
## Blocked by

- Blocked by [001-slice-title](./001-slice-title.md)
```

### Filename slug rules

- Lowercase, hyphen-separated
- Derived from the slice title
- No special characters

Example: "Add user authentication endpoint" → `003-add-user-auth-endpoint.md`

## Constraints

- Do NOT modify the parent PRD file.
- Create the `issues/` directory if it does not exist yet.
- After creating all files, print a summary list of created files with their titles.