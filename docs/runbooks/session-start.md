# Session Start Runbook

## Goal

Start a working session from retrieval and recent evidence instead of raw recall.

## Steps

1. Run `npm run context:bootstrap`.
2. Open the repo baseline `meta/context-spine/spine-notes-*.md`.
3. Use `meta/context-spine/hot-memory-index.md` as a working set, not just a recent-files list.
4. If the latest session is stale, create a new one with `npm run context:session`.
5. Run retrieval before broad file searches.
6. Open only high-signal artifacts first.
7. Re-anchor decisions in code, tests, and command output.
8. Run `npm run context:doctor` if the work changed canonical docs, the repo reading path, or the project's trusted source map.

## Closeout

Before ending the session:

- update the session note
- capture branch / HEAD / worktree state if it changed materially
- record the last command that verified something important
- log at least one observation if something non-trivial changed
- run `npm run context:refresh` if durable notes or docs were added
- run `npm run context:embed` only when vector hydration is worth the extra runtime and the host supports it
- run `npm run context:doctor` when the repo now feels harder to trust than it should
