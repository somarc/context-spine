# Session Start Runbook

## Goal

Start a working session from retrieval and recent evidence instead of raw recall.

## Steps

1. Run `scripts/context-spine/bootstrap.sh`.
2. If the latest session is stale, create a new one with `python3 scripts/context-spine/mem-session.py`.
3. Run retrieval before broad file searches.
4. Open only high-signal artifacts first.
5. Re-anchor decisions in code, tests, and command output.

## Closeout

Before ending the session:

- update the session note
- log at least one observation if something non-trivial changed
- refresh QMD if durable notes or docs were added
