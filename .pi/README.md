# Local Agent Extensions

`.pi/` is the optional extension layer for project-local agent workflows.

Use it when a workflow should:

- travel with the repo
- remain versioned with project truth
- be inspectable by humans
- be reinstallable on another machine

Do **not** use it as a second memory system. Core project truth still belongs in:

- `meta/context-spine/`
- `docs/adr/`
- `docs/runbooks/`
- normal source code and scripts

Recommended subdirectories:

- `skills/` for named, reusable workflows
- `prompts/` for reusable scaffolds

Keep this layer additive. The core Context Spine loop must still work without it.

Read the full guide in [../docs/runbooks/pi-extension-points.md](../docs/runbooks/pi-extension-points.md).
