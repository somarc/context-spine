# PI Extension Points

## Goal

Explain how `.pi/` works as an optional extension layer for project-local agent workflows without turning Context Spine into an agent-only system.

The short rule is:

- `meta/context-spine/`, `docs/`, and `scripts/context-spine/` are the core memory system
- `.pi/` is the optional extension plane that lets a specific project carry local agent workflows with it

Context Spine should still make sense without `.pi/`.

## What `.pi/` Is For

Use `.pi/` when you want agent behavior to be:

- project-owned
- versioned with the repo
- explicit instead of hidden in chat habits
- installable or reusable on another machine

Good `.pi/` content makes a repo easier to operate across machines, sessions, and people. It should not become a second undocumented product inside the project.

## What Belongs In `.pi/`

### `.pi/skills/`

Use this for small, named workflows that an agent can invoke repeatedly.

Good fit:

- memory bootstrap helpers
- review lenses
- bounded investigation workflows
- domain-specific research or implementation procedures
- repo-specific safety or release checks

A skill should be:

- procedural
- scoped to a real workflow
- small enough to maintain
- explicit about inputs, outputs, and verification

Bad fit:

- giant philosophy essays
- generic coding advice
- one-off project notes that belong in docs or memory
- business logic that should live in scripts or code

### `.pi/prompts/`

Use this for reusable prompt scaffolds, not for core project truth.

Good fit:

- recurring briefing formats
- handoff templates
- investigation prompts
- audit prompt skeletons
- structured output contracts for delegated work

Bad fit:

- durable architecture decisions
- operational runbooks
- current status or roadmap truth
- information that will rot if copied out of the repo docs

Prompt scaffolds should point back into the real source-of-truth surfaces instead of replacing them.

## What Does Not Belong In `.pi/`

Do not put these in `.pi/` just because an agent may read them:

- core architecture decisions
  - use `docs/adr/`
- operating procedures
  - use `docs/runbooks/`
- current project status, phase state, or session continuity
  - use `meta/context-spine/`
- delegated evidence or investigation outputs
  - use evidence packs or durable notes
- implementation logic that the product runtime depends on
  - use real code under normal source directories

`.pi/` is an adapter layer, not the project memory layer itself.

## Design Principles

### 1. Additive, not mandatory

If `.pi/` disappears, the repo should still be understandable and operable through the normal Context Spine loop.

### 2. Procedural, not archival

Skills and prompt scaffolds should tell an agent how to do something. They should not become a dumping ground for project history or unresolved notes.

### 3. Repo-owned, not machine-owned

If a workflow matters repeatedly, keep the source in `.pi/` and sync/install it outward. Do not rely on a personal global setup as the only copy.

### 4. Scripts before giant prompts

If a workflow needs stable behavior, prefer a small script plus a slim skill wrapper over a huge natural-language prompt.

### 5. Truth stays elsewhere

`.pi/` should point into real docs, code, and memory. It should not silently become the place where the actual project model lives.

## Recommended Shape

```text
.pi/
  README.md
  skills/
    README.md
    <skill-name>/
      SKILL.md
      scripts/
      references/
  prompts/
    README.md
    <prompt-name>.md
```

This is intentionally small. Add more only when there is a repeated need.

## Typical Patterns

### Pattern A: Repo-local skill source

Use when a workflow is worth invoking by name.

Example:

- `context-spine`
- `principal-engineer-review`

Flow:

1. define the skill in `.pi/skills/<name>/SKILL.md`
2. validate it
3. sync or install it into the runtime
4. keep the repo copy as source of truth

### Pattern B: Prompt scaffold

Use when a workflow needs a consistent framing but does not deserve a full skill.

Example:

- handoff prompt
- evidence-pack audit prompt
- domain-specific analysis starter

Flow:

1. keep the scaffold in `.pi/prompts/`
2. reference canonical docs and code paths from it
3. revise it when the workflow changes materially

### Pattern C: Script-backed extension

Use when natural language alone is too brittle.

Example:

- install/sync helpers
- validation scripts
- bounded delegation packagers

The script should live under normal repo script paths. The `.pi` layer should describe how and when to use it, not hide the executable behavior.

## How `.pi/` Relates To Context Spine

The clean split is:

- `meta/context-spine/`
  - current continuity and rolling memory
- `docs/`
  - durable explanations and operating truth
- `scripts/context-spine/`
  - core bootstrap, retrieval, doctor, upgrade
- `.pi/`
  - optional project-local agent operating extensions

That keeps the system understandable for both humans and agents.

## Maintenance Loop

When `.pi/` changes:

1. update the source under `.pi/`
2. validate or sync the skill if relevant
3. record any meaningful workflow shift in a session note or runbook
4. run the doctor if the reading path changed materially

For bundled Codex skills, see [codex-skill.md](./codex-skill.md).

## When To Add A New `.pi` Surface

Add a new skill or prompt only if all of these are true:

- the workflow recurs
- the workflow benefits from being named and shared
- the workflow is awkward to rediscover from scratch
- the workflow is not better represented as a runbook or script alone

If those are not true, keep it out of `.pi/`.

## Anti-Patterns

- storing project status in prompts
- copying architecture truth into skill text instead of linking it
- adding dozens of tiny prompts with no ownership
- creating agent-only workflows that humans cannot inspect or reason about
- making the repo depend on a global runtime state that is not represented in the repo

## Current Use In This Repo

Today, `.pi/` is primarily used for:

- bundled Codex skill sources under `.pi/skills/`
- optional prompt scaffolding space under `.pi/prompts/`

That is intentionally conservative. The extension point is real, but it is not meant to absorb the rest of the system.
