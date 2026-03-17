# ADR 0005: Context Spine Design Compass

## Status

Accepted

## Context

Context Spine is increasingly useful because it makes project memory explicit, legible, and inspectable.

That same success creates a risk:

- more doctrine
- more generated surfaces
- more agent affordances
- more runtime-like behavior

Without a clear compass, the project could become more impressive while becoming less trustworthy.

The right question is not only "what can Context Spine do next?" but also "what must never be compromised if it evolves toward a more native memory surface for Codex or GPT-class agents?"

## Decision

Use the following compass to judge future changes to Context Spine itself.

### Five Non-Negotiable Invariants

1. **Memory must stay inspectable without a special runtime**
   - A human should be able to open the repo and understand the memory surfaces directly from files, docs, and evidence.

2. **Durable, rolling, and generated memory must remain distinct**
   - Baselines, ADRs, and runbooks are not the same as sessions, observations, hot-memory indexes, or scorecards.

3. **Generated aids must never masquerade as truth**
   - Generated surfaces may guide reading and maintenance, but they do not replace code, docs, tests, or verified evidence.

4. **Skills should interpret and maintain memory, not replace it**
   - Skills are adapters and maintenance tools, not the authoritative store of project understanding.

5. **The default path must get simpler over time, not more ceremonial**
   - If a change improves only the system's shape and not restart quality, handoff quality, or drift resistance, it should be simplified or rejected.

### Five Things Context Spine Must Never Become

1. **A transcript archive**
   - The repo must not preserve every narration thread as if storage volume were the same as understanding.

2. **A control plane**
   - Context Spine is a memory surface, not a policy engine, daemon, orchestrator, or always-on runtime manager.

3. **Prompt soup**
   - Skills, prompts, and adapters must not sprawl into a hidden second system that only works for insiders.

4. **A black-box memory product**
   - The value must not depend on proprietary hidden state that the repo itself cannot explain.

5. **Confidence theater**
   - Context Spine must not produce polished memory surfaces that look authoritative while drifting from code, docs, or evidence.

### Five Ways Native Codex Memory Should Surpass Context Spine

If Codex or GPT-class agents eventually ship a native memory surface, it should be better than Context Spine in at least these ways without violating the invariants above:

1. **Automatic capture with evidence discipline**
   - Native memory should capture relevant git state, commands, tests, diffs, and tool events with much less manual upkeep.

2. **Explicit layered memory**
   - Native memory should separate session memory, project memory, and broader personal or organizational memory with clear boundaries and portability.

3. **First-class APIs, not mainly file conventions**
   - Native memory should expose reliable APIs and runtime hooks instead of depending mainly on shell scripts and repo-local file discipline.

4. **Stronger structured schemas alongside markdown**
   - Native memory should offer stronger structured schemas for retrieval, promotion, and evidence while preserving markdown and file-level inspectability where project truth matters.

5. **Less ceremony around normal use**
   - Native memory should reduce the amount of manual upkeep required for ordinary project use rather than demanding more rituals, reports, or maintenance habits.

## Adoption Test

Any future change that claims to make Context Spine more "native" should pass all three tests:

1. it preserves the five invariants
2. it does not push the repo toward the five anti-goals
3. it materially beats the current system on at least one of the five native-memory surpass criteria

If it fails any of those tests, the change should be simplified, deferred, or removed.

## Consequences

- future evolution has a clearer boundary
- the project has a durable answer to "what must stay true?"
- native-memory ambitions are allowed, but only under explicit discipline
- the repo can evolve without losing the thing that currently makes it trustworthy
