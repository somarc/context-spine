# Flow And Cognition

Use this reference when the spine needs stronger signal flow, better compression, or clearer self-checking.

## Goal

Hydrate from deep evidence, move the right signal upward without distortion, and make the system aware of its own uncertainty.

## Hydration Model

Hydration means sampling the lowest useful evidence tiers before relying on summaries.

Preferred order:

1. runtime checks, command output, and live endpoints
1. code, tests, and configs
1. docs, contracts, and ADRs
1. durable notes, sessions, and observations
1. inference

A segment is dry when a source should have been sampled but was skipped.

## Flow Column

Treat the spine as a column with five distinct stages:

1. source hydration
1. working-set compression
1. decision framing
1. user-facing synthesis
1. durable reconciliation

The system is healthy when evidence can move through all five stages without blockage or distortion.

## Common Flow Failures

- dryness
  - not enough fresh evidence was sampled
- blockage
  - contradictions were found but never resolved or labeled
- backflow
  - stale durable memory dominates current retrieval or planning
- flooding
  - too much undifferentiated context reaches the working set
- compression loss
  - nuance disappears between evidence and summary

## Cognition Loop

For the current task, make these steps explicit:

1. perceive
   - what evidence was actually sampled
1. orient
   - what the objective, topology, and constraints mean
1. decide
   - what conclusion or next action follows
1. act
   - what command, edit, or recommendation should happen
1. reconcile
   - what durable memory must change because of the action

## Metacognition Loop

Ask these questions before closing the loop:

- What do I know directly?
- What am I inferring?
- Which source would most likely falsify this conclusion?
- What changed during the work?
- What would mislead the next operator if left unmarked?
- Where is confidence reduced because evidence is stale, partial, or indirect?

## Output Pattern

When the task is complex, include these fields:

- `SOURCE_HYDRATION`
- `FLOW_STATE`
- `COGNITIVE_FRAME`
- `METACOGNITIVE_CHECK`

These should be short and concrete. They are not essays.

## Promotion Guidance

Promote recurring flow repairs when they keep happening:

- repeated confusion about source precedence
  - update the skill or runbook
- repeated contradiction between durable notes and live code
  - add a supersession pattern or invalidation example
- repeated summary distortion under delivery pressure
  - strengthen the active-delivery working set contract
