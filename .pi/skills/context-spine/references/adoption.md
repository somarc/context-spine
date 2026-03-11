# Context Spine Adoption

## Required repo surfaces

- `meta/context-spine/`
- `scripts/context-spine/`
- `docs/adr/`
- `docs/runbooks/`
- `.agent/diagrams/`

## Minimum memory artifacts

- one baseline durable note: `meta/context-spine/spine-notes-<topic>.md`
- one session directory: `meta/context-spine/sessions/`
- one observation directory: `meta/context-spine/observations/`
- one hot-memory index: `meta/context-spine/hot-memory-index.md`

## Wrapper guidance

Prefer repo-local wrappers that remove ambiguity:

- `context:init`
- `context:update`
- `context:embed`
- `context:bootstrap`
- `context:session`
- `context:score`

If the repo already uses `npm`, expose them via `package.json`. Otherwise direct shell scripts are acceptable.

## Codex skill distribution

If the repo wants to ship the skill with the project:

1. keep the source at `.pi/skills/context-spine/`
2. add a repo install script that syncs to `${CODEX_HOME:-$HOME/.codex}/skills/context-spine`
3. validate with the `skill-creator` quick validator before installation

## First verification pass

After installation or repair:

1. run init/update/embed
2. run bootstrap
3. confirm the baseline note appears in bootstrap output
4. confirm a session note can be created
5. confirm retrieval points at the repo-local index and memory root
