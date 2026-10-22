# Workflow: Refactor

## Purpose

Improve code structure while preserving the externally observable behavior that the current implementation already provides. If behavior must change, route that part through **Implement Feature** or **Fix Bug** and keep the structural work separable.

The refactor is worthwhile only when the new structure makes the relevant code easier to understand or change, removes unnecessary branches or invalid states, or reduces repeated work without adding needless indirection.

## Roles and authority

- **Orchestrator:** Pins the behavior contract, defines the target structural outcome, and owns routing and final disposition. Does not edit application code.
- **Developer:** Owns the structural change and focused self-checks.
- **Tester:** Independently checks behavior parity on the relevant surface and latest artifact.
- **Reviewer:** Reviews the exact diff for behavior changes, complexity, missed callers, and regression risk.

Follow **agents/orchestrator.md** and the target repository instructions. Keep one writer for each overlapping code surface.

## 1. Name the structural outcome and pin current behavior — Orchestrator

Record:

- The specific code area and maintenance pain being addressed.
- What structure should exist after the refactor and why it is clearer.
- The observable behavior that must remain unchanged, including relevant inputs, outputs, side effects, errors, and user paths.
- The repository/revision and available behavior-level tests, snapshots, fixtures, or runtime controls.

Inspect the affected subsystem and callers first. Before moving structure, establish a behavior pin using existing tests or a focused characterization/equivalence check. If coverage is missing, ask Developer to create the smallest useful behavior-level pin before changing the structure. Type checking and lint alone do not establish parity.

If the desired structural outcome is unclear or the request would change product behavior, investigate or route the behavior change separately. Do not hide feature work inside a refactor.

## 2. Reshape in verifiable units — Developer

- Remove dead or redundant structure before adding a new abstraction.
- Make the smallest change that reaches the named target shape. Keep code local when its shape is already clear.
- For an API or type reshape, migrate affected callers and remove the obsolete path in the same scoped change when safe. Do not leave compatibility layers without a documented requirement.
- Make one bounded structural move at a time and keep the behavior pin green after each meaningful unit.
- Spot-check renames and references in code, configuration, tests, documentation, and string-based integrations.
- Keep formatting, feature changes, and unrelated cleanup out of scope.

If the target shape cannot be reached without a behavior change or a larger redesign, stop and return the evidence to Orchestrator for a scope decision.

## 3. Prove behavior parity — Tester

Tester verifies the latest artifact against the pinned contract on the matching surface. Prefer existing behavior tests or a replay/equivalence check with comparable inputs. Record revision, environment, commands/actions, outputs, and artifacts.

**PASS** requires evidence that the relevant behavior remains the same. A successful build, type check, or source-only comparison is not a parity proof. If the baseline or matching execution surface is unavailable, report **BLOCKED / PARITY_UNPROVEN** and name the evidence needed.

## 4. Review the structural result — Reviewer

Review the exact latest diff for:

- A clear improvement to the named structural problem.
- Preserved behavior and removal of obsolete paths or redundant branches.
- Missed callers, hidden references, compatibility changes, or new indirection.
- Test quality and scope discipline.

Report only specific, actionable findings. Do not edit the patch or treat a clean diff as proof of runtime parity.

## 5. Correct and stop — Orchestrator

After a correction, rerun the affected behavior pin and review the new artifact. Stop when parity and the structural goal are supported by evidence, when no useful next edit/check remains, or when scope, resources, or access require a decision. Do not keep a refactor whose diff does not deliver the named improvement.

## Final outcome and report

- **COMPLETED / REFACTORED:** The target structure was reached, behavior parity passed on the latest artifact, and the latest review has no unresolved blocking finding.
- **BLOCKED / PARITY_UNPROVEN:** The available evidence cannot establish unchanged behavior.
- **BLOCKED / ENVIRONMENT_BLOCKED:** Required baseline, surface, or tool is unavailable.
- **NEEDS_HUMAN / SCOPE_DECISION:** The requested change needs a behavior or architecture decision outside the brief.

Report the structural pain and target shape; pinned behaviors and parity evidence; repository and artifact revision; changed paths; Reviewer result; checks actually run and not run; remaining risks; and any behavior change split into follow-up work.
