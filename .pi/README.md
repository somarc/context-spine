# Local Agent Extensions

This directory is the extension point for project-local agent tooling.

Recommended subdirectories:

- `skills/` for local skills
- `prompts/` for reusable prompt scaffolds

Keep this layer additive. Do not make the core memory loop depend on it.
