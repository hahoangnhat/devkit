# Review Change Workflow

## Goal

Review an existing code change and report clear, useful findings. The target may be a pull request, commit, branch diff, or uncommitted change. **Do not edit code or fix issues in this workflow.** A review can finish even when it finds problems.

## Roles

- **Orchestrator:** Defines the review target, assigns agents, tracks their reports, and gives the final result. Does not review code.
- **Reviewer:** Owns the technical review and its findings. Does not edit code.
- **Tester:** Checks specific behavior when the review needs runtime evidence. Does not edit code.
- **Developer:** Not needed by default. Do not start a fix through this workflow.

Follow the agent role files for how to work and what is allowed. Use real subagents through the platform adapter.

## 1. Set the review target — Orchestrator

Record:

- **Target:** Repository and PR, commit, branch diff, or local changes to review.
- **Change:** Base and latest version, or enough details for Reviewer to identify the full diff.
- **Goal:** What the change is meant to do, with requirements or acceptance checks if known.
- **Focus:** Any risks or parts the user wants checked first.
- **Limits:** Permissions, time budget, and checks that must not run.

Give these facts to Reviewer. Do not choose the findings or require an approved code-change scope: **this is review-only work**. If the target is unclear, ask for the missing detail instead of guessing which change to review.

## 2. Review the change — Reviewer

Identify the exact change and read its full relevant diff. For uncommitted work, include staged, unstaged, and relevant untracked files. Check the code around the change, tests, and known requirements as needed.

If a PR or commit is not available in the current checkout, Reviewer may prepare an **isolated, temporary checkout or detached worktree** for that exact version, when tools and permissions allow it. Do not switch the user's current branch or change an existing worktree. Do not create a task branch or change the submitted code. Report the workspace path and code version to Orchestrator. If a safe checkout is not possible, report `BLOCKED` instead of reviewing a different version.

Use the review rules in `agents/reviewer.md`. Focus on real bugs, broken behavior, security risks, missing important tests, and unwanted changes. Give each supported finding a location, impact, evidence, and a useful next action.

Do not invent a cause or test result. Do not block for personal style choices. State what you did not check. If the diff cannot be identified or important parts cannot be reviewed, return `BLOCKED` with the reason; **do not call a partial review a full pass**.

If runtime evidence is needed to judge an important risk, report the exact behavior that needs checking so Orchestrator can ask Tester. Do not change code or publish PR comments or approvals.

## 3. Check behavior when needed — Tester (optional)

Skip this step when Reviewer can reach a sound result from the code and available evidence.

Otherwise Orchestrator asks Tester to check a **specific behavior** on the same code version being reviewed. Pass along the exact checkout or worktree when one was prepared. Tester may use that workspace or prepare a separate safe, temporary checkout of the same version if needed. Tester runs safe, allowed checks on the right UI, API, CLI, or service and reports `PASS`, `FAIL`, or `BLOCKED` with actual results and checks not run.

Orchestrator sends Tester's report back to Reviewer. **Reviewer owns the review verdict.** A failed runtime check is evidence for review, not permission to start a fix.

## 4. Return the review verdict — Reviewer

Return the report format defined in `agents/reviewer.md`, including the exact reviewed version and coverage.

- `PASS`: No supported blocking findings remain. Advisory findings may still be present.
- `FAIL`: At least one supported blocking finding needs action.
- `BLOCKED`: Missing target, access, key evidence, or checks prevent a sound verdict.

If the change has moved since the review began, identify the new version and repeat any review or Tester checks affected by it. **Never reuse an old verdict for changed code.** Stop when there is enough evidence for a verdict, no useful safe check remains, or a limit is reached.

## 5. Report the result — Orchestrator

Use the latest Reviewer verdict. If reports conflict or evidence is missing, ask the right specialist for a focused check. Do not settle technical disagreements by reviewing code yourself.

| Result | Meaning |
| --- | --- |
| `COMPLETED / REVIEWED` | Review finished with a `PASS` or `FAIL` verdict and evidence. A `FAIL` means changes are needed, not that the review task failed. |
| `BLOCKED / INCONCLUSIVE` | The review cannot reach a sound verdict with the evidence available. |
| `BLOCKED / ENVIRONMENT_BLOCKED` | A required diff, tool, environment, or permission is unavailable. |
| `NEEDS_HUMAN / DECISION_REQUIRED` | The user must choose the target, clarify an important requirement, or grant permission. |

Report the **review verdict first**, then blocking and advisory findings, exact PR/commit/diff version, coverage, checks run or not run, and remaining risks. Do not claim that `PASS` means a PR was approved or merged.

**Review-only rule:** Do not edit code, create commits or task branches, change the submitted PR, merge, or deploy. A temporary checkout or detached worktree is allowed only to read or test the exact review target safely. Do not overwrite existing work or remove a workspace you do not own. Do not publish PR review comments or approvals without separate permission. If a fix is needed, report it; use a separate change workflow only when the user asks for a fix.
