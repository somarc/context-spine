# Session Start Runbook

## Goal

Start a working session from retrieval and recent evidence instead of raw recall.

## Steps

1. Run `npm run context:bootstrap`.
2. Open `meta/context-spine/spine-notes-context-spine.md`.
3. If the latest session is stale, create a new one with `npm run context:session`.
4. Run retrieval before broad file searches.
5. Open only high-signal artifacts first.
6. Re-anchor decisions in code, tests, and command output.
7. Run `npm run context:doctor` if the work changed canonical docs, the repo reading path, or the project's trusted source map.

## Closeout

Before ending the session:

- update the session note
- log at least one observation if something non-trivial changed
- refresh QMD if durable notes or docs were added
- run `npm run context:doctor` when the repo now feels harder to trust than it should
