# GitHub Backend

## Locating the PRD

Ask the user for the PRD GitHub issue number or URL if not already provided.

Fetch the issue (including comments) with:

```bash
gh issue view <number> --comments
```

## Creating issues

For each approved slice, create a GitHub issue with:

```bash
gh issue create \
  --title "<slice title>" \
  --body "<issue body from template>"
```

### Parent PRD reference format

In the issue body, reference the parent PRD as:

```
#<prd-issue-number>
```

### Blocked-by reference format

```
- Blocked by #<issue-number>
```

Use real issue numbers — create blockers first so their numbers are available.

### Labels (optional)

If the repo uses labels, apply:
- `hitl` or `afk` based on slice type
- Any relevant area labels (e.g. `backend`, `frontend`)

Add labels with `--label` flag on `gh issue create`.

## Constraints

- Do NOT close or edit the parent PRD issue.
- Do NOT add comments to the parent PRD issue unless the user explicitly asks.