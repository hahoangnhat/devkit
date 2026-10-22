# Workflow: Investigate

## Purpose

Answer a bounded engineering question by tracing the real system and presenting evidence. This workflow is read-only: its deliverable is an explanation, diagnosis, or recommendation, not a code change.

Use it for questions such as how a behavior works, why a design exists, where a failure may originate, whether an approach is feasible, or what evidence is missing. If the requested outcome is to change behavior, route to Fix Bug or Implement Feature after the question is answered.

## Roles and authority

- **Orchestrator:** Owns the question, evidence boundary, synthesis, and final answer. Usually investigates directly.
- **Tester:** Runs a bounded read-only runtime check when source inspection cannot answer the question. Does not edit application code or tracked tests.
- **Developer:** Not used; this workflow does not authorize implementation.
- **Reviewer:** Not used unless Orchestrator requests a specific independent read-only assessment of conflicting evidence.

Follow **agents/orchestrator.md** for handoffs, permissions, and truthful reporting. Do not create parallel work merely to use more agents. Delegate only when the questions are independent, the evidence can be gathered separately, and parallel work is likely to shorten the path to a reliable answer.

## 1. Define the question and boundary — Orchestrator

Record:

- The question that must be answered and the intended reader.
- Repository and relevant revision, product surface, affected paths, and known constraints.
- Whether the user needs an explanation, a diagnosis, a feasibility assessment, or a recommendation.
- What evidence would answer the question and what would remain uncertain.

Inspect the available repository guidance, feature documentation, tests, logs, history, and project verification instructions before asking the user for information already available. Separate authoritative requirements from assumptions in tickets or reports.

If the request also asks for a change, keep this investigation read-only and identify the appropriate follow-up workflow. Do not silently broaden the assignment.

## 2. Trace the system and gather evidence — Orchestrator, Tester when needed

1. Start at the observed behavior or named entry point. Follow the relevant callers, state, data shape, and external boundaries until the mechanism is clear or evidence runs out.
2. Prefer existing project verification commands, feature maps, tests, logs, and control surfaces. Do not invent commands or claim a test was run when it was only inspected.
3. Use runtime evidence when the question is about behavior that source reading cannot establish. Tester records the exact revision, environment, action or command, result, and artifact.
4. Keep experiments read-only and within the given permissions. Do not alter shared, production, or user data. Use temporary diagnostics only when authorized and safe.
5. For each material hypothesis, record the evidence that supports or contradicts it. Stop repeating an inspection or experiment when it cannot produce new information.

**Parallel work:** First identify blocking questions, genuinely independent evidence streams, shared files or systems, and whether one investigator is the smallest effective approach. Keep a single owner for overlapping investigation; parallelize only separable evidence gathering.

## 3. Synthesize the answer — Orchestrator

Lead with the answer. Support it with precise file and line references, commands, logs, runtime observations, or other inspectable artifacts. Label each conclusion as:

- **Observed:** Directly established from the inspected artifact or runtime.
- **Inferred:** The best explanation of observed evidence, with the reasoning stated.
- **Unknown:** Not established, with the missing evidence named.

For a choice between alternatives, give the real tradeoffs and a recommendation. Do not pad the report with speculative possibilities or call a hypothesis a root cause without discriminating evidence.

## Stop conditions and outcome

Finish when the question is answered to the requested scope, no useful read-only evidence source remains, the authorized investigation budget is exhausted, or further progress requires access or a decision.

- **COMPLETED / ANSWERED:** The requested explanation is supported by cited evidence.
- **COMPLETED / RECOMMENDATION:** Feasibility or alternatives were assessed with evidence and tradeoffs.
- **BLOCKED / INCONCLUSIVE:** Evidence is insufficient or the required runtime surface is unavailable. State the exact gap and the most useful next check.
- **NEEDS_HUMAN / DECISION_REQUIRED:** An unresolved product decision or authorization prevents a sound conclusion.

Do not report **BLOCKED** merely because source inspection found no issue. Do not report an answer as verified when only a proxy or assumption supports it.

## Required report

Include the question and scope; repository/revision; concise answer; evidence with file/line references or runtime artifacts; observed facts versus inference; checks actually run and not run; confidence and limitations; explicit code changes (**none**); and one useful next action when the question remains open.
