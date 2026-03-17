# Visual Explainers

This directory holds the self-contained HTML reading surfaces for Context Spine.

These files are not decorative screenshots. They are part of the project's legibility layer.
Use them when a system, workflow, or boundary is easier to absorb visually than through prose alone.

## What This Directory Is For

Use a visual explainer here when it helps someone:

- restart work faster
- understand the shape of the system
- audit a workflow or boundary
- see how a new capability fits into the whole
- hand the project to another person without a long oral recap

Each explainer should stay paired with real project truth:

- code
- docs
- durable notes
- evidence

The preferred pattern is:

1. generate the visual artifact
2. create or update the durable note or runbook
3. link both into the project graph
4. let bootstrap surface recent explainers as part of project reading

## Start Here

If you only open one diagram first, use this order:

1. `context-spine-overview-2026-03-11.html`
   - best first read for overall system shape
2. `context-spine-human-review-2026-03-11.html`
   - best read for human/operator value and design stance
3. `context-spine-doctor-2026-03-15.html`
   - best read for hygiene and drift control
4. `context-spine-runtime-contract-2026-03-16.html`
   - best read when you need to understand the new runtime manifest, skill verification, and run-state model
5. `context-spine-upgrade-path-2026-03-15.html`
   - best read when updating an older install
6. `context-spine-pi-extension-points-2026-03-15.html`
   - best read when deciding what belongs in `.pi/`
7. `context-spine-skill-stack-2026-03-15.html`
   - best read when deciding how the maintenance, promotion, and rollout skills fit together
8. `context-spine-agent-working-set-2026-03-15.html`
   - best read when deciding how an agent should open the repo without guessing
9. `context-spine-elon-doctrine-2026-03-15.html`
   - best read when deciding whether a change is actually valuable or just more complexity

## Current Catalog

| File | Primary audience | Open when you need to understand | Core question it answers | Status |
| --- | --- | --- | --- | --- |
| `context-spine-overview-2026-03-11.html` | new reader, maintainer | the whole model | "What is Context Spine and how is it shaped?" | current |
| `context-spine-human-review-2026-03-11.html` | human operator, reviewer | why this exists and why it matters | "Why is this worth using in a real project?" | current |
| `context-spine-doctor-2026-03-15.html` | maintainer, lead | repo hygiene and drift control | "How do we know the memory spine still maps to project truth?" | current |
| `context-spine-runtime-contract-2026-03-16.html` | maintainer, agent user | the new runtime guarantees | "How did Context Spine become more auditable and deterministic?" | current |
| `context-spine-upgrade-path-2026-03-15.html` | maintainer of older installs | existing-project upgrades | "How do we move older repos forward safely?" | current |
| `context-spine-pi-extension-points-2026-03-15.html` | maintainer, agent user | optional extension design | "What should `.pi/` contain, and what should stay out?" | current |
| `context-spine-skill-stack-2026-03-15.html` | maintainer, agent user | the new orchestration layer | "How do maintenance, promotion, and rollout fit around the core scripts?" | current |
| `context-spine-agent-working-set-2026-03-15.html` | maintainer, agent user | opening the repo correctly | "How does the memory spine reduce blind inference for the next agent?" | current |
| `context-spine-elon-doctrine-2026-03-15.html` | maintainer, builder | value discipline | "Does this change actually improve Context Spine or just add more shape?" | current |

## Curation Rules

Keep this directory small and intentional.

Add a new explainer only when it does one of these jobs:

- clarifies a subsystem that is otherwise hard to hold in working memory
- explains a new workflow that changes how the repo should be operated
- improves handoff for future maintainers or operators
- makes a review or audit materially easier to understand

Avoid:

- one-off vanity visuals
- diagrams that duplicate an existing explainer without adding a new question or audience
- stale explainers that no longer match the repo

If an older explainer is superseded, either:

- remove it, or
- mark the newer file as the preferred reading surface here

## Maintenance

When a meaningful workflow or system boundary changes:

1. update the corresponding explainer if it is still current
2. update the linked durable note or runbook
3. make sure bootstrap still surfaces the right reading order

The goal is not to accumulate diagrams. The goal is to keep a small, trustworthy visual layer that makes the project easier to resume and hand off.
