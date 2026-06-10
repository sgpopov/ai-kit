# agent-skills

This is the agent-skills project — a collection of production-grade engineering skills for AI coding agents.

## Project Structure

```
skills/       → Core skills (SKILL.md per directory)
agents/       → Reusable agent personas (code-reviewer, test-engineer, security-auditor, seo/)
prompts/      → Standalone prompt files (code-review, review-plan, ux-review)
references/   → Shared cross-skill checklists (testing, performance, security, accessibility)
scripts/      → Install/link helpers (link-skills.sh, link-agents.sh, link-references.sh, list-skills.sh)
docs/         → Setup guides for different tools
```

## Skills

Grouped by genre — the genre determines which sections a skill needs (see Conventions).

**Process / discipline** (step-by-step procedures or quality gates):
code-review, improve-codebase-architecture, write-a-prd, prd-to-plan, prd-to-issues, ubiquitous-language, write-a-skill, find-skills, git-guardrails-claude-code

**Reference catalogs** (prioritized rule sets applied during build/review):
nestjs-best-practices, react-best-practices

**Prompt / interactive** (drive a conversation, minimal scaffolding):
grill-me, grill-with-docs

## Conventions

- Every skill lives in `skills/<name>/SKILL.md` — flat, no intermediate directories
- YAML frontmatter with `name` and `description` fields
- Description: third person, what the skill does first, then triggers ("Use when…"). Max 1024 chars
- **Required of every skill:** `Overview`; the **core procedure** (`## Process`/`## Steps` for process skills, or the rule tables for reference catalogs); `When to Use` (triggers, plus when *not* to fire); and a `Verification` step (how to confirm the output is correct)
- **Conditional sections, by genre:**
  - *Process / discipline:* add `Red Flags`, and `Common Rationalizations` when the agent is tempted to cut corners (e.g. code-review)
  - *Reference catalogs:* the rule tables are the body — no Red Flags / Rationalizations
  - *Prompt / interactive:* Overview + When to Use + the prompt itself — keep minimal
- Keep SKILL.md under ~100 lines; move depth into bundled files in the skill's own directory
- Shared, cross-skill checklists live in top-level `references/`; skill-specific supporting files (REFERENCE.md, FORMAT docs, `rules/`, `scripts/`) live in the skill's own directory

## Commands

- `npm test` — Not applicable (this is a documentation project)
- Validate: Check that all SKILL.md files have valid YAML frontmatter with name and description

## Boundaries

- Always: Follow the `write-a-skill` skill and the genre templates above when creating new skills
- Never: Add skills that are vague advice instead of actionable processes
- Never: Duplicate content between skills — reference other skills instead
