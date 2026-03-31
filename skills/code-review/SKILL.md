---
name: code-review
description: Perform a code review of branch changes comparing against a base branch. Reviews for code clarity, consistency, and maintainability while preserving exact functionality. Use when user asks for a "code review", "review my changes", "review this branch", or "review PR".
---

# Code Review

## Quick start

If the base branch was provided as an argument, use it. Otherwise, ask:
> "Which branch should I compare against? (e.g. `main`, `develop`)"

## Workflow

1. **Get the diff**
   - List commits: `git log <base>...HEAD --oneline`
   - Get changed files: `git diff <base>...HEAD --name-only`
   - Get full diff: `git diff <base>...HEAD`

2. **Read changed files in full** — don't rely solely on the diff; read the surrounding context using the Read tool for each modified file.

3. **Understand the change**:

4. **Analyze for improvements**: Look for opportunities to:
   - Reduce unnecessary complexity and nesting
   - Eliminate redundant code and abstractions
   - Improve readability through clear variable and function names
   - Consolidate related logic
   - Remove unnecessary comments that describe obvious code
   - Avoid nested ternary operators - prefer switch statements or if/else chains
   - Choose clarity over brevity - explicit code is often better than overly compact code

5. **Maintain balance**: Avoid over-simplification that could:
   - Reduce code clarity or maintainability
   - Create overly clever solutions that are hard to understand
   - Combine too many concerns into single functions or components
   - Remove helpful abstractions that improve code organization
   - Make the code harder to debug or extend

6. **Review each change for**:
   - **Clarity** — naming, readability, intent
   - **Consistency** — follows patterns used elsewhere in the codebase
   - **Maintainability** — no dead code, no unnecessary complexity, no magic values
   - **Correctness** — logic errors, edge cases, off-by-ones
   - **No functionality changes** — flag anything that looks like a behavioral change

7. **Present findings** grouped by file, using this format per issue:
   ```
   `path/to/file.ts:42` — [severity: suggestion|warning|blocker]
   Issue: <what's wrong>
   Suggestion: <concrete fix>
   ```

5. **Close with a summary** — overall assessment, count of blockers/warnings/suggestions.

## Severity guide

| Level | Meaning |
|---|---|
| blocker | Must fix — correctness, security, or data integrity issue |
| warning | Should fix — likely bug or breaks consistency |
| suggestion | Nice to have — clarity or style improvement |
