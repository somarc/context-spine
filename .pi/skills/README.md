# Skills

Place project-local skills here.

Each skill should be:

- tied to a real repeated workflow
- small enough to maintain
- explicit about what it does
- grounded in code, docs, or scripts instead of vague prose
- aware of adjacent skills when the real job spans multiple lenses

Prefer skill composition over skill sprawl:

- one skill can judge value
- another can judge architecture
- another can decide promotion target or maintenance action

Skills should call out their natural companions instead of pretending they are sufficient for every case.

Use a skill when the repo needs a named workflow such as:

- memory bootstrap
- architectural review
- bounded investigation
- domain-specific implementation guidance

Do not turn this directory into a generic prompt dump or a second copy of the project docs.

Current bundled skills:

- `context-spine`
- `principal-engineer-review`
- `context-spine-maintenance`
- `elon-doctrine`
- `memory-promotion`
- `multi-repo-rollout`
- `visual-corpus-curator`

`context-spine/` remains the bundled source-of-truth skill for promoting this workflow into Codex.

Read the fuller guidance in [../../docs/runbooks/pi-extension-points.md](../../docs/runbooks/pi-extension-points.md).
