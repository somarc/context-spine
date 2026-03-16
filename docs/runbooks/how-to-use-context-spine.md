# How To Use Context Spine

## Goal

Use Context Spine to make a project easier to understand, easier to resume, and less dependent on one person remembering everything.

You do not need Codex to benefit from it. You do not need a fully automated setup. The value comes from keeping a small set of memory surfaces current and trustworthy.

## Who It Is For

Context Spine is useful for:

- developers joining or resuming a project
- tech leads trying to keep decisions and evidence connected
- teams handing work across people or across weeks
- agent users who want better retrieval and less re-explaining
- solo builders who want their own project memory to stay durable

## What People Actually Do With It

In practice, people use Context Spine for five common jobs:

1. start work faster by reading the current baseline note and latest session summary
2. capture what changed in a form that survives context resets and teammate handoffs
3. link decisions back to code, tests, logs, or commands instead of vague memory
4. refresh retrieval so future searches find the right notes quickly
5. keep long-horizon knowledge outside the repo while keeping short-horizon working memory close to the code

For agents, the key surface is not just the baseline note. It is the combination of:

- the baseline note
- the latest session
- the hot-memory working set
- the current source-of-truth files named in the baseline

## Core Surfaces

These are the surfaces a person actually interacts with:

- `meta/context-spine/spine-notes-*.md`
  The baseline understanding of the project or subsystem.
- `meta/context-spine/sessions/`
  Session summaries for current work.
- `meta/context-spine/hot-memory-index.md`
  A working set that points at what should be opened first right now.
- `meta/context-spine/observations/`
  Small dated observations, decisions, and open questions.
- `docs/adr/`
  Architecture decisions that should last.
- `docs/runbooks/`
  Repeatable operating knowledge.
- `.agent/diagrams/`
  Visual explainers for systems, plans, audits, or investigations.

## A Normal Session

Use this when starting meaningful work:

1. if this is your first visit to the repo, run `npm run context:setup`; otherwise run `npm run context:bootstrap`
2. read the baseline `spine-notes-*.md`
3. read `hot-memory-index.md` to see the current working set
4. read the latest session summary if one exists
4. create a fresh session note if the last one is stale or the task is substantial
5. do the work in code, tests, docs, or commands
6. update the session note with what changed, what was verified, and what remains open
7. add an observation if something non-trivial was learned
8. run `npm run context:refresh` if notes or docs changed
9. run `npm run context:doctor` when the repo's trusted reading path changed

## A Good Session Note

A useful session note is short and concrete. It should answer:

- what problem was being worked on
- what branch / commit / worktree state framed the session
- what is true now
- what evidence was used
- what command last proved something important
- what decisions were made
- what is still open
- what someone else should do next

If another person can open the session note tomorrow and continue without asking for a recap, the note is doing its job.

## A Good Baseline Note

The baseline `spine-notes-*.md` should tell a new reader:

- what this repo is for
- where the important code and docs live
- what commands matter
- what the current working model is
- what the architecture, boundaries, and invariants are
- what is unresolved

It should be updated when the project shape changes, not on every small edit.

## Team Workflows

### Onboarding

Give a new teammate three things:

1. the baseline note
2. the latest session note
3. one visual explainer if the system is complex

That is usually enough to replace a long verbal dump.

### Handoffs

Before handing work to another person:

- update the current session note
- add direct evidence paths or `qmd://` links
- list the next action explicitly

### Investigations

For debugging or audits:

- collect command output, logs, and tests first
- synthesize them into a durable note or evidence pack
- link the result back into the project graph

### Weekly Maintenance

Once a week is usually enough:

- review whether the baseline note is still accurate
- check whether session notes are being created for real work
- roll stable architecture or boundary knowledge out of sessions and into durable notes
- refresh retrieval if docs or notes changed
- run the memory score if you want a lightweight health check
- run the doctor if the repo now feels harder to trust than it should

## Retention

Do not let the repository turn into a transcript archive.

- keep architecture, shape, boundaries, and current operating assumptions durable
- keep sessions and observations only as rolling working memory
- periodically condense the important parts into baseline notes, runbooks, ADRs, or curated evidence packs
- treat hot-memory indexes and scorecards as local generated aids

## With Or Without Codex

Context Spine works in both modes.

### Without Codex

Use the repo as a disciplined project memory system:

- write baseline notes
- keep session notes current
- store visual explainers and ADRs
- use QMD or another retrieval layer to search notes and docs

### With Codex

Codex gets better results because the repo already has structure:

- bootstrap points at the right files
- retrieval has a smaller, higher-signal search space
- session notes reduce repetitive restatement
- decisions and evidence are easier to trust

Codex is an accelerator here, not the main character.

## Minimal Adoption Path

If you want the smallest useful version:

1. add `meta/context-spine/`
2. create one baseline `spine-notes-*.md`
3. create `sessions/` and start writing one note per meaningful session
4. add one bootstrap command or runbook that tells people where to start
5. refresh retrieval when notes are added

That is enough to get value.

## Signs It Is Working

You know Context Spine is helping when:

- people ask for fewer verbal recaps
- project restarts are faster
- decisions are easier to trace
- searches return the notes you actually need
- work can be handed off with less friction
