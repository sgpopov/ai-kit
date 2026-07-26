---
name: to-tickets
description: Breaks a PRD into independently-grabbable issues using tracer-bullet vertical slices. Use when user wants to convert a PRD to issues/tickets, create implementation tickets, or break down a PRD into work items. Works with both GitHub issues and local markdown files.
---

# To Tickets

## Overview

Break a plan, spec, or conversation into a set of tickets — tracer-bullet vertical slices, each declaring the tickets that block it.

Supports two backends:
- **GitHub** — read/create real GitHub issues via `gh` CLI
- **Local** — read/write markdown files inside a project directory

## When to Use

- The user wants to convert a PRD into issues/tickets or break it into work items
- Work is ready to be parallelized across contributors

---

## Step 1 — Detect or ask for the backend

Infer the backend from context if possible:
- If the user provides a GitHub issue number, URL, or mentions `gh` / GitHub → **GitHub mode**
- If the user provides a file path, mentions a `docs/`, `prds/`, or similar local directory → **Local mode**
- If ambiguous, ask:

> "Should I work with GitHub issues or with local markdown files?"

Then read the matching reference file for backend-specific instructions **before continuing**:

| Mode   | Reference file         |
|--------|------------------------|
| GitHub | `references/github.md` |
| Local  | `references/local.md`  |

---

## Step 2 — Locate the PRD

Follow the instructions in the reference file to fetch or read the PRD content.

---

## Step 3 — Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code and avoid proposing work that is already done.

---

## Step 4 — Draft vertical slices

Break the PRD into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be **HITL** or **AFK**:
- **HITL** — requires human interaction (e.g. architectural decision, design review)
- **AFK** — can be implemented and merged without human interaction

Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests) — vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first
</vertical-slice-rules>

Give each ticket its **blocking edges** — the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket — green is promised only there.

---

## Step 5 — Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other tickets (if any) must complete first
- **User stories covered**: which user stories from the PRD this addresses

Ask the user:
- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any ticket be merged or split further?
- Are the correct ticket marked as HITL and AFK?

Iterate until the user approves the breakdown.

---

## Step 6 — Create the issues

Follow the backend-specific instructions in the reference file to create the issues.

Create issues in **dependency order** (blockers first) so you can reference real issue numbers / filenames in the "Blocked by" field.

Use this issue body template for both backends:

<issue-template>
## Parent PRD

<link or reference to the parent PRD — format per backend>

## What to build

A concise description of this ticket. Describe the end-to-end behavior, not layer-by-layer implementation. Reference specific sections of the parent PRD rather than duplicating content.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- Blocked by <issue reference> (if any)

Or "None - can start immediately" if no blockers.

## User stories addressed

Reference by number from the parent PRD:

- User story 3
- User story 7
</issue-template>

Do NOT modify or close the parent PRD.

## Verification

Before finishing, confirm: every user story in the PRD is covered by at least one ticket, each ticket is a complete vertical path (not a single layer), `Blocked by` references resolve to real issue numbers/filenames created in dependency order, and the user approved the breakdown in Step 5.