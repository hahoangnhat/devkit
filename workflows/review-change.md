# Workflow: Review Change

## Purpose

Independently assess a specified diff or change artifact and return concrete findings. This workflow is read-only: it does not implement fixes, modify tests, approve a merge, or publish a review externally.

Use it when the requested outcome is a review. If implementation is also requested, complete the review first and let Orchestrator route any authorized correction through the appropriate implementation workflow.

## Roles and authority

- **Orchestrator:** Defines the review question and exact artifact, gathers context, and reports the review disposition.
- **Reviewer:** Inspects the assigned change independently and reports evidence-backed findings without editing.
- **Tester:** Used only when a focused, authorized behavioral check is needed to resolve a material review question. A code review does not replace required behavioral verification.
- **Developer:** Not used unless Orchestrator later receives authorization to implement findings in a separate workflow.

Follow **agents/reviewer.md** for finding format, independence, and review boundaries.

## 1. Establish the review artifact — Orchestrator

Before review, provide:

- Repository, intended base and target revisions, branch/worktree, and complete diff or stable patch snapshot.
- The requested contract, acceptance criteria, constraints, and relevant workflow.
- Changed paths, Developer self-checks, Tester evidence and artifact revision when required, and known exclusions.

For an uncommitted change, identify staged, unstaged, and untracked content separately. **Base HEAD alone is not the patch identity.** If the intended change cannot be distinguished from unrelated user work, narrow the assignment before review. Do not ask Reviewer to approve an arbitrary working tree.

## 2. Inspect and assess — Reviewer

Review the complete assigned diff and enough surrounding code, requirements, callers, tests, repository guidance, and history to evaluate it. Check:

1. Does the change meet the stated behavior or maintenance contract?
2. Are important inputs, outputs, state transitions, errors, and boundary conditions handled?
3. Is there a reachable regression, security, privacy, permission, data-integrity, or compatibility risk relevant to this diff?
4. Do tests assert observable behavior and cover the changed path? Are claimed checks tied to this exact artifact?
5. Is the scope focused, and is the verified artifact still the one under review?

Validate a suspected defect by tracing a concrete path or performing an authorized, non-destructive check. Do not produce generic warnings, style-only blockers, duplicate findings, or claims based on an earlier revision. If a question requires live behavior evidence, state that gap or ask Orchestrator to arrange Tester verification.

## 3. Report findings — Reviewer

For each finding include:

- **LOCATION:** Exact file and line or artifact reference.
- **SEVERITY:** **CRITICAL**, **HIGH**, **MEDIUM**, or **LOW**.
- **DISPOSITION:** **BLOCKING** or **ADVISORY**, with the reason.
- **EVIDENCE:** Trigger, reachable failure mechanism, and observed or traced result.
- **ACTION:** Smallest correction or precise check needed.

If there are no findings, say so and state the reviewed scope and evidence gaps. A review with no findings is not merge authorization. Do not fix findings in this workflow.

## Stop conditions and outcome

- **COMPLETED / REVIEWED:** The assigned artifact was reviewed and findings or a no-findings result were reported. This may include blocking findings that require a separate correction.
- **BLOCKED / REVIEW_INCOMPLETE:** The diff, contract, required evidence, or permission is missing, contradictory, or stale enough to prevent a sound review.
- **NEEDS_HUMAN / SCOPE_DECISION:** The review cannot proceed until the intended change or review boundary is clarified.

If the artifact changes during review, report the stale scope and request a fresh review of the new artifact. Do not reuse a prior verdict.

## Required report

Include review scope and artifact identity; **PASS**, **FAIL**, or **BLOCKED** for the review stage; ordered findings in the format above or **None**; checks actually run and not run; evidence gaps; risks; and the next action. Orchestrator owns the task-level outcome.
