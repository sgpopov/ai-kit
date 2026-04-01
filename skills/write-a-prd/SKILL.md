---
name: write-a-prd
description: Create a PRD through user interview, codebase exploration, and module design, then submit as a GitHub issue or save as a local markdown file. Use when user wants to write a PRD, create a product requirements document, or plan a new feature.
---

# Write a PRD

This skill guides you through creating a PRD via user interview, codebase exploration, and module design.

You may skip steps if you don't consider them necessary.

---

## Step 0 — Detect or ask for the backend

Infer the output format from context if possible:
- User mentions a GitHub issue, `gh`, or a repo URL → **GitHub mode**
- User mentions a file path, local directory, or `docs/`/`prds/` folder → **Local mode**
- If ambiguous, ask:

> "Should I submit the PRD as a GitHub issue or save it as a local markdown file?"

Then read the matching reference file before continuing:

| Mode | Reference file |
|------|---------------|
| GitHub | `references/github.md` |
| Local | `references/local.md` |

---

## Step 1 — Problem description

Ask the user for a long, detailed description of the problem they want to solve and any potential ideas for solutions.

---

## Step 2 — Explore the repo

Explore the repo to verify their assertions and understand the current state of the codebase.

---

## Step 3 — Interview

Interview the user relentlessly about every aspect of this plan until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

---

## Step 4 — Module design

Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A **deep module** (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

---

## Step 5 — Write and submit the PRD

Once you have a complete understanding of the problem and solution, write the PRD using the template below. Then follow the backend reference file to save or submit it.

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>