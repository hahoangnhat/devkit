# Fix Bug Workflow

## Goal

Check whether a reported bug still exists and whether the system behaves as expected. **Do not change code unless there is a clear reason.** A task may end with a new fix, an earlier fix, no change, or a report of what could not be confirmed.

## Roles

- **Orchestrator:** Leads the task, reviews evidence, chooses next steps, and reports the result. Does not edit application code.
- **Tester:** Tries to reproduce the bug and checks real behavior. Does not edit application code.
- **Developer:** Finds the cause and makes needed code changes.
- **Reviewer:** Checks the final code change for mistakes and risks. Does not edit application code.

Skip Developer and code review when no code change is needed. Follow `agents/orchestrator.md` for task handoffs and permissions. Use real subagents through the platform adapter; never claim an agent ran when it did not.

## 1. Understand the bug — Orchestrator

Record:

- **Expected:** What should happen, based on requirements or an agreed product rule, not just current code.
- **Reported:** What went wrong, how it happens, how often, and its impact.
- **Conditions:** App and code version, environment, account, data, settings, and platform.
- **Key check:** What result would show the bug, or show correct behavior.
- **Success check:** What must be tested and what proof is needed.

Pass the bug report and any existing evidence to Tester. Ask Tester or Developer to check relevant logs, code history, and pull requests when needed. Ask the user only for a missing product decision or required permission.

## 2. Try to reproduce the bug — Tester

1. Set up conditions as close to the report as possible. Record any differences.
2. Try the reported steps in the running UI, API, CLI, or service. Save steps, results, and useful logs or screenshots.
3. If the bug does not appear, check whether the running system meets **Expected** in the relevant conditions. Passing unit tests or reading code is not enough.
4. Check logs, past changes, open pull requests, data, settings, timing, and environment differences for clues or signs that the bug still happens.

**Do not set a fixed number of attempts.** Try again when a new test can answer a useful question or check a new possible cause. Stay within the allowed time, cost, and tool limits. Record what each test showed. Do not repeat tests without a reason, except when measuring a bug that happens only sometimes.

**Stop** when the evidence answers the question, there is no useful next test, the budget is used up, a needed environment cannot be used, or permission is required. Do not keep trying forever.

Return `REPRODUCED`, `NOT_REPRODUCED`, or `BLOCKED`, with the conditions, evidence, and missing checks. These are **Tester observations**, not final task results.

## 3. Decide whether to change code — Orchestrator

Use the first case supported by evidence:

| Situation | Action |
| --- | --- |
| A past pull request or commit may have fixed the bug | **Check the existing fix** first. Do not create a second fix yet. |
| The bug is reproduced | Ask Developer to investigate and propose the files to change. Approve the change scope before any code edits. Respect any current fix owner. |
| The bug is not reproduced; **Expected** is confirmed in relevant conditions; no signs of failure remain | End as `COMPLETED / NO_CHANGE_NEEDED`. State what was tested. Do not claim the bug never existed. |
| The bug is not reproduced, but important conditions were missed or signs of failure remain | Run another useful check if possible. Otherwise end as `BLOCKED / INCONCLUSIVE`. |
| A needed environment, tool, or permission is missing | Try safe recovery within scope. Otherwise end as `BLOCKED / ENVIRONMENT_BLOCKED`. |
| The expected behavior needs a product decision | End as `NEEDS_HUMAN / DECISION_REQUIRED` with one clear question. |

A few passing tests do not cancel evidence of a real failure. Never ask Developer to make a guessed fix.

### Check an existing fix — Tester

1. Identify the pull request or commit and the code versions **before** and **after** it.
2. If possible, run the same test in the same conditions on both versions. Check that the bug appears before and correct behavior appears after.
3. Report `ALREADY_FIXED_VERIFIED` only when the before-and-after evidence supports it. Orchestrator then decides whether to end as `COMPLETED / ALREADY_FIXED`. Do not edit the existing fix or open a competing pull request.
4. If both versions still fail, report `DEFECT_PRESENT` with evidence. Do not take over a fix already owned by someone else.
5. If the older version cannot be tested or does not show the bug, report `INCONCLUSIVE` for the earlier fix and give the current evidence. Orchestrator decides whether `NO_CHANGE_NEEDED` or `INCONCLUSIVE` fits the task.

A commit message, ticket status, or passing test alone is not proof of an earlier fix.

## 4. Investigate, approve scope, and fix — Developer and Orchestrator

**First, investigate — Developer (no code edits).** Orchestrator sends the bug report, evidence, success checks, and any known limits or forbidden paths. Developer may read other files to find the cause, but must not edit code yet.

- Find the cause, not just the visible problem. Do not suggest guessed workarounds.
- Propose the files that need changes. Explain why each file is needed and how the fix can be tested.
- If no code change is supported by the evidence, report that finding. Do not create a patch.

**Then, approve the change scope — Orchestrator.** Review Developer's proposed files against the user's permissions and repository rules. Approve the files Developer may edit, or ask Developer to explain an unclear part. Do not choose the technical fix yourself. Ask the user only when a change needs permission beyond the allowed limits.

**Finally, implement — Developer.** Edit only after Orchestrator approves the scope and only within that scope.

- Make the smallest needed change. When practical, add a test that fails before the fix and passes after it; otherwise explain why not.
- If another file needs a change, explain why and request an updated scope **before editing that file**.
- Do not change unrelated files. Report changed paths, code version, tests actually run, and known risks.

## 5. Test the result — Tester

Check the **latest code version** independently:

- Test the original bug steps and expected behavior in the running system. If those steps cannot show whether the fix works, use another clear behavior check.
- Run relevant tests and check nearby behavior that might be affected.
- Record the code version, environment, commands or steps, results, and evidence.
- Return `PASS`, `FAIL`, or `BLOCKED`. Only use `PASS` with suitable behavior evidence; green CI, code reading, or Developer's claim is not enough.
- If you cannot tell whether the fix works, return `BLOCKED` with reason `INCONCLUSIVE`.

## 6. Review the code change — Reviewer

After Tester returns `PASS`, review the **same latest change**. Check the cause, correctness, new bugs, security risks, scope, and test quality. Give file locations and reasons for any problems.

No code review is needed when no code changed. Orchestrator may ask for a separate read-only check if specific evidence is missing.

## 7. Handle failures and stop — Orchestrator

- **Tester `FAIL`:** Give Developer the failure evidence, then test the updated code again.
- **Reviewer finds a serious problem:** Give Developer the finding, then repeat the affected tests and review.
- **Tool or environment fails:** Try safe recovery. Never call an unrun test `PASS`.
- Allow up to **two rounds of code corrections after the first fix**. Reproduction attempts have **no fixed count**.
- When code changes after testing or review, repeat any checks made out of date by the change.
- If required tests or review still fail when corrections stop, use `BLOCKED / CHECKS_FAILED`. Do not call a known failure `INCONCLUSIVE`.
- Stop when the result is supported, no useful next test remains, the budget is used up, or permission is needed. Never lower the success requirements just to finish.

## Deliver the verified change — Orchestrator and Developer

For verified file changes, follow `agents/orchestrator.md` → **Deliver verified changes** before reporting `COMPLETED`. If publishing fails, report `BLOCKED / DELIVERY_BLOCKED`. No change means no commit or PR.

## Final result — Orchestrator

Choose **one** result:

| Result | Meaning |
| --- | --- |
| `COMPLETED / FIXED` | Latest fix passed behavior checks and independent code review, and its PR was delivered. |
| `COMPLETED / ALREADY_FIXED` | A past fix is confirmed by before-and-after evidence. |
| `COMPLETED / NO_CHANGE_NEEDED` | Current behavior meets **Expected** in relevant conditions, with no open signs of failure. |
| `BLOCKED / CHECKS_FAILED` | Required tests or code review still fail after corrections stop. |
| `BLOCKED / INCONCLUSIVE` | Not enough evidence to say the bug is fixed or no change is needed. |
| `BLOCKED / DELIVERY_BLOCKED` | Required checks passed, but the verified change could not be committed, pushed, or delivered as a PR. |
| `BLOCKED / ENVIRONMENT_BLOCKED` | A needed environment, tool, or permission is unavailable. |
| `NEEDS_HUMAN / DECISION_REQUIRED` | A product decision or new permission is needed. |

Report what was expected and reported; what was tested and on which code version; results and evidence; cause or unknowns; code changes (**or none**); Tester and Reviewer results; remaining risks; and a PR link **only if one exists**.

**Safety:** Tester and Reviewer do not edit application code. Developer stays within the allowed scope. Merging, deploying, deleting important data, or other hard-to-undo actions need the required human approval and platform permission. Never make a guessed fix or unnecessary pull request.
