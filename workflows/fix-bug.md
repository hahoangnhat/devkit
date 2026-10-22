# Workflow: Fix Bug

## Purpose

Resolve a reported defect by verifying **expected versus observed behavior**, not by forcing a code change. A valid result may be a verified fix, an existing fix, no change needed, or an evidence-backed inconclusive/blocker report.

## Roles and authority

- **Orchestrator:** Owns the goal, stage routing, evidence assessment, correction budget, and final disposition. Never edits application code.
- **Tester:** Reproduces the reported behavior and independently verifies outcomes on the appropriate runtime surface. Does not edit application source.
- **Developer:** Makes only an evidence-justified, scoped fix; adds regression coverage when appropriate.
- **Reviewer:** Independently reviews the latest code change and its risks. Does not edit application source.
- **No-change paths:** Do not invoke Developer or a code-diff Reviewer solely to satisfy a fixed sequence. Orchestrator assesses the evidence and reports the outcome.

Follow `agents/orchestrator.md` for delegation contracts, autonomy, access boundaries, and truthful reporting. Platform adapters must perform actual subagent invocations; instructions alone do not count as execution.

## 1. Define the behavior contract — Orchestrator

Before reproduction, identify:

- **Expected:** Observable outcome derived from requirements, product behavior, or a confirmed specification. Do not infer it merely from what current code does.
- **Reported actual:** Observable failure, trigger, frequency, affected versions, and impact.
- **Scope:** User path/API, environment, account/data state, feature flags, platform, and relevant code revision.
- **Discriminator:** The specific observation that would distinguish a correct result from the reported defect.
- **Acceptance / evidence:** What must be observed, where, and with which commands or tools to resolve the report.

Inspect available reports, logs, history, and linked PRs before asking the user. Escalate an unresolved product expectation or necessary missing authorization; never invent one.

## 2. Reproduce and assess the current behavior — Tester

1. Confirm the test environment and application revision. Record meaningful differences from the reported conditions.
2. Exercise the reported path on the closest accessible **real execution surface** (UI, API, CLI, service), and capture the discriminator, actual values, commands/actions, and evidence.
3. If the failure does not appear, independently check whether **current behavior meets the expected contract** under the relevant conditions. Passing unit tests or plausible source code alone is not sufficient.
4. Inspect available production signals, recent code/PR history, feature flags, data, timing, permissions, and environment differences for conflicting evidence or an existing fix.
5. Do not repeatedly retry the same conditions without a new hypothesis or new evidence.

**Evidence-driven reproduction policy (no fixed attempt count):** Do not impose an arbitrary maximum number of reproduction attempts. Continue while each next experiment has a concrete, testable hypothesis or newly available evidence, can meaningfully distinguish possible causes, and fits the authorized time/cost/tool budget. Record the hypothesis, setup, observation, and what was learned for every meaningful attempt. After a failed attempt, change the conditions, instrumentation, or hypothesis rather than blindly repeating the same actions. For intermittent failures, repeated runs are justified only when they measure a defined frequency/timing hypothesis.

**Stop or change course** when the reported behavior is sufficiently resolved by evidence; no informative next experiment remains; the relevant environment is unavailable and cannot safely be restored; the authorized budget is exhausted; or further investigation requires missing access or a genuine human decision. If the evidence remains insufficient, report `NOT_REPRODUCED` / `INCONCLUSIVE` with explicit coverage and limitations, rather than claiming the bug is fixed or trying indefinitely. Environment repair is permitted only within scope; never simulate a successful reproduction.

Tester reports `REPRODUCED`, `NOT_REPRODUCED`, or `BLOCKED`, with evidence and limitations. These are **observation states**, not final task outcomes.

## 3. Decide before editing — Orchestrator

Apply the first supported route below. **Never send an unverified hypothesis to Developer as an instruction to patch.**

| Evidence | Next action / outcome |
| --- | --- |
| A specific PR/commit plausibly contains an earlier fix | Enter **Verify existing fix** first; do not create a competing patch. |
| Failure reproduced on the relevant surface with no existing fix artifact/owner | Investigate the mechanism, then proceed to **Implement** only with a justified fix and a way to verify it. |
| Failure not reproduced; expected behavior is directly verified under relevant reported conditions; no unresolved contradictory evidence | Finish **`COMPLETED / NO_CHANGE_NEEDED`**, without application code changes. State exactly which environments/versions and scenarios were covered. Do **not** claim it was previously broken or fixed. |
| Failure not reproduced; current checks pass but reported conditions are not covered, or relevant error signals remain | Finish **`BLOCKED / INCONCLUSIVE`** when no informative next experiment remains or the authorized investigation budget is exhausted. State the missing discriminatory evidence and the most useful next check. |
| Required environment/tool/access is unavailable | Attempt only safe, scoped recovery; otherwise finish **`BLOCKED / ENVIRONMENT_BLOCKED`** with the precise requirement. |
| Expected behavior cannot be determined from authoritative evidence | Finish **`NEEDS_HUMAN / DECISION_REQUIRED`** with one concrete product decision; do not implement an invented expectation. |

A no-change outcome is a **scoped conclusion**, not proof the bug never existed or cannot recur. Evidence of ongoing failures takes precedence over a few passing checks.

### Verify existing fix — Tester

When an identifiable PR/commit may already resolve the issue:

1. Record the fix artifact, baseline revision, patched revision, and comparable environment inputs.
2. Where feasible, reproduce the reported discriminator on the baseline, then verify its absence and the expected outcome on the patched/current revision using comparable conditions.
3. Return **`COMPLETED / ALREADY_FIXED`** only when before-and-after evidence supports attribution to that specific change. Do not edit the existing fix or open a competing PR.
4. If both revisions show the failure, report an **unresolved defect**, not a successful prior fix. Do not create a competing patch while another owner is fixing it; new implementation requires clear ownership, authorization, and a verified failure mechanism.
5. If the baseline cannot be exercised or cannot reproduce, do **not** claim `ALREADY_FIXED`. Reassess under the ordinary `NO_CHANGE_NEEDED` / `BLOCKED / INCONCLUSIVE` rules using current evidence.

Do not treat a commit message, ticket status, or passing test alone as proof that a previous change fixed the report.

## 4. Investigate and implement — Developer (only when justified)

Orchestrator supplies the failure evidence, expected behavior, identified mechanism or bounded investigation goal, permitted paths, and exact verification plan.

- Determine the root cause using evidence; distinguish cause from symptom. When the cause is uncertain, investigate rather than authoring a speculative patch.
- Make the smallest justified fix. Add a regression test that fails for the defect and passes after the fix when feasible; document why it is not feasible otherwise.
- Keep unrelated cleanup out of scope. Report changed paths, revision/commit, checks actually run, and remaining risks.
- If investigation disproves the need for a code change, return the findings to Orchestrator for a no-change or inconclusive decision; do not fabricate work.

## 5. Independently verify the latest artifact — Tester

- Verify the **current code revision/commit** against the original discriminator and acceptance criteria on the relevant execution surface. Use the original failing repro, or another independently discriminating failure signal when an exact repro is impossible.
- With the Codex adapter, read `.agents/skills/devkit-verify/SKILL.md` and the matching completed feature document before running the scenario. `feature.template.md` is an authoring scaffold, not a verification case.
- Run focused regression checks and relevant adjacent behavior checks. Record commands, results, screenshots/logs/artifacts, environment, and revision.
- Return `PASS`, `FAIL`, or `BLOCKED`. `PASS` requires behavior evidence appropriate to the defect; source inspection, green CI, or a verbal assurance alone is insufficient.
- If verification cannot distinguish before from after, return `BLOCKED` with reason `INCONCLUSIVE` to Orchestrator; do not mark the patch fixed.

## 6. Review the latest change — Reviewer

Only after Tester passes, review the latest diff for correctness, root-cause coverage, regressions, security, scope, and test quality. Report findings with file references and severity. Review is not required for a no-code-change outcome unless the Orchestrator identifies a specific evidence gap that an independent read-only assessment can resolve.

## 7. Corrections and stopping — Orchestrator

- **Implementation defect / Tester `FAIL`:** Return concrete failure evidence to Developer, then reverify the new revision.
- **Blocking Reviewer finding:** Return the finding to Developer; rerun verification and review on the resulting revision.
- **Environment/tool failure:** Repair within scope, then rerun the affected check. Do not count environmental failure as a passing test or conceal missing coverage.
- Allow at most **two code-correction cycles total after the initial implementation**. Track reproduction experiments separately; they have **no fixed numeric cap**. Do not repeat attempts without a reason that can produce new information.
- Any material code change invalidates affected verification and review results for older revisions.
- Stop on a supported disposition or when the budget, permissions, or informative investigation options are exhausted. Never weaken acceptance criteria to force `PASS`.

## Final disposition and required report

Report **one** task-level `OUTCOME` compatible with `agents/orchestrator.md`, plus a specific `RESOLUTION`:

| `OUTCOME / RESOLUTION` | Required condition |
| --- | --- |
| `COMPLETED / FIXED` | Latest change passed behavioral verification, and the latest diff passed independent review. |
| `COMPLETED / ALREADY_FIXED` | A specific earlier fix was confirmed by comparable baseline-versus-patched evidence. |
| `COMPLETED / NO_CHANGE_NEEDED` | Current behavior directly meets the expected contract in relevant tested conditions, with no outstanding contradictory evidence. |
| `BLOCKED / INCONCLUSIVE` | No sufficiently discriminating evidence despite permitted attempts; do not claim fixed or no-change. |
| `BLOCKED / ENVIRONMENT_BLOCKED` | Required environment, access, execution, or verification remains unavailable. |
| `NEEDS_HUMAN / DECISION_REQUIRED` | A genuine product choice or authorization is required. |

Final report must include: expected vs. reported behavior; tested surface and revision; reproduction attempts and observations; supporting evidence/commands; root cause or limits of knowledge; code changes (or **explicitly none**); verification and review results or why they did not apply; remaining risks; and PR link only if actually created.

**Safety:** Tester and Reviewer do not modify application code. Developer stays within authorized scope. No agent may merge, deploy, alter protected resources, or perform irreversible actions without the required human authorization and platform permission. A no-change or inconclusive result must never create a speculative PR.
