# Local Markdown Backend

## Directory convention

PRDs live in a `prds/` directory at the project root by default:

```
<project-root>/
└── prds/
    ├── my-feature.md
    └── another-feature.md
```

If the project uses a different layout (e.g. `docs/`, `docs/prds/`), ask the user to confirm the path before writing.

## Filename convention

- Lowercase, hyphen-separated slug derived from the feature name
- No special characters

Example: "User authentication redesign" → `prds/user-auth-redesign.md`

## Saving the PRD

1. Create the `prds/` directory if it does not exist.
2. Write the PRD content to `prds/<slug>.md`.
3. Print the relative file path so the user knows where it landed.

## Constraints

- Do NOT modify any existing PRD files.
- After saving, print the file path so the user can find it.