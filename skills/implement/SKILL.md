---
name: implement
description: "Implement work from an existing spec or set of tickets, including testing, independent review, and a commit."
disable-model-invocation: true
---

Implement the work described in the user's spec or tickets. Explicit user
instructions take precedence over this workflow.

Read the spec, relevant repository instructions, and existing code and tests.
Identify the acceptance criteria before editing. Resolve routine details from
context; ask only when an ambiguity materially affects scope or behavior.

Inspect the current branch and working tree. Preserve existing user changes
and keep edits focused on the requested work.

Use the /tdd skill for behavior changes where practical. Use previously agreed
test boundaries when available; otherwise choose appropriate boundaries from
the spec and existing tests. Test observable behavior rather than implementation
details.

Run focused tests and applicable type checks during implementation. Before
finishing, verify each acceptance criterion and run the repository's required
checks, including the full test suite. If a check cannot run or fails for an
unrelated reason, report the limitation explicitly.

Have a subagent use the /code-review skill to review the diff against the spec.
Validate its findings, fix relevant issues, and explain any dismissed or deferred
findings. If independent review is unavailable, perform a self-review and disclose
that limitation.

After review fixes, rerun affected checks. Repeat broader checks when the fixes
could invalidate their earlier results.

Commit only the changes belonging to this task on the current branch, unless
the user instructed otherwise. Inspect the staged diff before committing.
Do not include unrelated changes or push automatically.

Report what was implemented, verification results, any unmet acceptance criteria
or remaining issues, and the commit identifier if created. Do not describe
incomplete or unverified work as fully complete.