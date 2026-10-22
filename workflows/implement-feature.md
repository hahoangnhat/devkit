# Workflow: Implement Feature

## Purpose

Deliver a requested behavior change in small, verifiable steps. The feature contract is the observable behavior the user asked for; implementation detail should stay as small as the evidence and acceptance criteria allow.

Use this workflow for new or intentionally changed product behavior. Use **Fix Bug** for a reported defect against existing expected behavior, **Refactor** for structure-only changes, and **Investigate** when the requested outcome is an answer rather than a change.

## Roles and authority

- **Orchestrator:** Defines the feature contract, scope, work ownership, evidence gates, and final disposition. Does not edit application code.
- **Developer:** Owns implementation and focused self-checks within the assigned scope.
- **Tester:** Independently verifies the behavior on the relevant surface and exact latest artifact.
- **Reviewer:** Independently reviews the latest diff after applicable behavioral verification.

Follow **agents/orchestrator.md** and the target repository instructions. Use actual adapter subagents when a role is required; Markdown alone does not dispatch agents. Do not parallelize code-coupled work or let multiple writers edit the same surface.

## 1. Define the feature contract — Orchestrator

Before implementation, state:

- **User outcome:** What a user, API client, or operator will observe.
- **Acceptance criteria:** Concrete cases that distinguish success from failure.
- **Domain shape, when material:** The data, state, or interaction boundary that organizes the behavior. Do not invent a new abstraction for a narrow change that needs none.
- **Scope and exclusions:** Affected paths, platform, data, permissions, feature flags, and non-goals.
- **Verification surface:** Existing project commands, tests, feature map, or runtime controls that can prove the behavior.

Inspect the relevant subsystem, callers, types, and existing user path first. Keep the contract concise. If the expected behavior, data semantics, or authorization is genuinely unclear, investigate it or return **NEEDS_HUMAN / DECISION_REQUIRED** rather than filling the gap with an assumption.

## 2. Choose the smallest useful execution shape — Orchestrator

Identify blocking prerequisites, independent workstreams, shared mutable state or files, and the smallest safe ownership split. A single Developer should own code-coupled changes. Parallelize only disjoint work that can be independently reviewed and verified; serialize shared writes.

When multiple implementation shapes are credible and the choice materially affects the result, compare the alternatives or build a cheap, disposable proof before committing to one. Do not create a planning artifact or abstraction layer when a short contract and direct implementation provide enough clarity.

Give each assignment a self-contained brief using the handoff fields in **agents/orchestrator.md**. Pin the relevant paths, domain shape, acceptance criteria, verification commands/surface, budget, and forbidden actions.

## 3. Implement the behavior — Developer

- Inspect the baseline and local conventions before editing.
- Make the smallest change that satisfies the feature contract. Keep the domain shape explicit in the types or structure instead of scattering assumptions.
- Add or update behavior-focused tests when appropriate. Assert outcomes a user or caller observes; avoid tests that merely mirror the implementation.
- Keep unrelated refactors, formatting, dependency changes, and cleanup out of scope.
- Report the exact changed paths and revision, checks actually run, evidence, risks, and anything not verified.

If implementation reveals a missing product decision, a different root-cause bug, or a materially broader design, stop and return the evidence to Orchestrator for routing or a decision.

## 4. Verify the latest behavior — Tester

Tester independently checks the latest artifact against every acceptance criterion on the matching execution surface. Reuse the target project's verification commands and feature map where present; capture the exact revision, environment, actions/commands, outcomes, and artifacts.

**PASS** requires evidence of the requested observable behavior. Type checks, source inspection, or a green test unrelated to the acceptance criteria are not enough. If the real surface or required data is unavailable, report **BLOCKED** with the missing prerequisite. Do not imply a manual or simulated check was automated.

## 5. Review the latest change — Reviewer

After Tester passes, review the exact latest diff for contract coverage, correctness, regressions, security or data risks relevant to the feature, scope, and test quality. Report only specific, actionable findings with location, severity, evidence, and smallest required action. Do not edit the patch.

## 6. Correct and stop — Orchestrator

Return a verified failure or blocking finding to Developer with its evidence. After any material edit, rerun affected Tester verification and review on the new artifact. Do not repeat an unchanged failed approach without a new reason that can add information.

Continue only while an authorized, useful next step remains and the agreed resource budget allows it. Stop when acceptance is met, the next useful action is unavailable, a product decision is needed, or the budget is exhausted. Never weaken acceptance criteria to force a pass.

## Final outcome and report

- **COMPLETED / FEATURE_DELIVERED:** Latest artifact meets the feature contract on the relevant surface and the required review has no unresolved blocking finding.
- **BLOCKED / IMPLEMENTATION_BLOCKED:** Scope, access, tool, environment, or verification prevents responsible completion.
- **BLOCKED / VERIFICATION_INCONCLUSIVE:** Available checks do not distinguish whether the requested behavior works.
- **NEEDS_HUMAN / DECISION_REQUIRED:** A product or authorization decision is required.

Report the feature contract; repository and artifact revision; changed paths; Tester evidence and surface; Reviewer result; commands/checks actually run and not run; remaining risks; and PR link only if one was actually created. Do not merge or deploy unless the user and platform explicitly authorize it.
