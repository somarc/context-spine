---
name: elon-doctrine
description: Apply the E.L.O.N. doctrine to Context Spine decisions. Use when judging whether a change, feature, note, workflow, or maintenance step makes the memory system more useful, more legible, more grounded in evidence, and less reliant on blind inference.
---

# E.L.O.N. Doctrine

## Overview

Use this skill when the question is not just "can we build this?" but "should this exist in Context Spine at all?"

This skill is about value discipline, not architectural sufficiency by itself.
When the thing being judged changes project shape, boundaries, coupling, reliability, or durable artifact needs, pair this with `principal-engineer-review`.

E.L.O.N. means:

- **Evidence over aspiration**
- **Legibility over lore**
- **Optimize for utility x impact**
- **No blind inference**

This is the doctrine for deciding whether Context Spine is becoming more valuable or just more elaborate.

## Workflow

1. Identify the proposed change or current surface being judged.
2. Evaluate it against all four E.L.O.N. lenses.
3. Separate:
   - demonstrated value
   - likely value
   - ceremonial or ornamental complexity
4. Ask whether the change improves:
   - restart quality
   - handoff quality
   - correctness under context reset
   - drift resistance
5. If the issue is also architectural, operational, or durability-shaping, invoke `principal-engineer-review` alongside this skill.
6. Recommend one of:
   - keep and strengthen
   - simplify
   - defer
   - remove

## Skill Composition

Use `elon-doctrine` with other skills when the question spans more than value judgment:

- pair with `principal-engineer-review`
  when you also need a judgment about system shape, coupling, reliability, or what should become durable
- pair with `context-spine-maintenance`
  when doctor/score findings exist and you need to decide which hygiene work is genuinely worth doing
- pair with `memory-promotion`
  when the result of the E.L.O.N. pass is "this should become durable" and you need to choose the right artifact

The contract is:

- `elon-doctrine` decides whether the thing deserves to exist
- companion skills decide how it should be shaped, stored, or executed

## Evaluation Lens

### Evidence over aspiration

- Is this grounded in repo evidence, commands, or observed pain?
- Does it reduce mismatch between claimed state and actual state?

### Legibility over lore

- Will the next agent or maintainer understand the system faster because of this?
- Does it reduce dependence on private oral context?

### Optimize for utility x impact

- Does this help a high-value workflow?
- How often will it matter?
- Who benefits: one maintainer, many repos, or every restart?

### No blind inference

- Does this reduce guessing?
- Does it point the next agent toward authoritative files or verified commands?
- Does it surface uncertainty honestly instead of hiding it?

## Output Expectations

Return:

- the thing being judged
- the E.L.O.N. assessment by letter
- the strongest evidence for and against it
- your final recommendation

## Boundaries

- Do not praise complexity for its own sake.
- Do not keep a feature because it is clever.
- Do not score something as valuable unless it improves actual restart, handoff, or truth-maintenance behavior.

## References

- `../../../../docs/runbooks/elon-doctrine.md`
- `../../../../meta/context-spine/spine-notes-context-spine.md`
- `../../../../README.md`
- `../../principal-engineer-review/SKILL.md`
