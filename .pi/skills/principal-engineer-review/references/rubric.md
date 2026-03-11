# Review Rubric

## How To Judge

Each finding should answer three things:

- what signal is visible now
- why it creates future cost, risk, or confusion
- what durable artifact should absorb the conclusion

Severity guide:

- `High`: likely to cause architectural rework, operational risk, or repeated confusion soon
- `Medium`: not immediately fatal, but compounds quickly or reduces changeability
- `Low`: worth capturing now so it does not become invisible later

## 1. System Shape And Boundaries

Ask:

- Are responsibilities becoming clearer or more blurred?
- Is there a stable source of truth for each concern?
- Can the project be explained in layers without hand-waving?

Signals:

- cross-layer leakage
- orchestration duplicated in multiple places
- code and docs describing different boundaries
- unclear ownership of shared behavior

## 2. Modularity And Coupling

Ask:

- What is getting harder to swap, test, or reason about independently?
- Are abstractions reducing coupling or merely hiding it?
- Are interfaces explicit enough for bounded delegation?

Signals:

- hidden global state
- direct knowledge of internals across modules
- changes that require synchronized edits across unrelated areas
- adapters that are really hard dependencies

## 3. Reliability And Operability

Ask:

- Are failure modes understood and handled intentionally?
- Is important behavior observable through logs, commands, tests, or runbooks?
- Are retries, fallbacks, or recovery steps needed but absent?

Signals:

- silent failure paths
- no operational evidence for critical workflows
- missing runbooks for repeated human intervention
- optimistic assumptions about external systems

## 4. Evidence Alignment

Ask:

- Do code, tests, docs, and notes agree about what is true?
- Is the current design justified by evidence or by narrative confidence?
- What claims are still unverified?

Signals:

- docs ahead of implementation
- code changed without a matching memory update
- tests covering behavior that docs do not mention
- decisions only recoverable from chat history

## 5. Changeability And Scale

Ask:

- If this project grows or changes direction, what becomes expensive first?
- Where are the likely future bottlenecks in ownership, complexity, or throughput?
- What shortcuts are acceptable now, and which are already turning into debt?

Signals:

- one component accumulating too many responsibilities
- coordination-heavy edits for simple changes
- no clear seam for scaling a subsystem or replacing a dependency
- local optimizations obscuring the whole-system model

## 6. Memory Obligations

Ask:

- What was learned that now deserves durable memory?
- Which assumptions should become explicit ADRs, runbooks, or diagrams?
- What repeated explanation can be removed by updating the baseline or evidence?

Signals:

- important context trapped in sessions
- recurring onboarding questions
- delegated work without curated evidence
- system shape easier to show visually than to re-explain verbally

## Review Posture

- prefer high-signal artifacts before broad searching
- flag missing evidence instead of compensating with certainty
- recommend the smallest durable artifact that resolves ambiguity
- tie every architectural concern to a practical next action
