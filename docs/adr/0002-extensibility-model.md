# ADR 0002: Extensibility Model

## Status

Accepted

## Context

The memory layer must grow with the project without becoming tightly coupled to one agent runtime or one knowledge backend.

## Decision

Context Spine extends through adapters and conventions:

- `scripts/context-spine/` for core bootstrap and memory tools
- `scripts/delegation/` for evidence packaging and delegate adapters
- `.pi/skills/` and `.pi/prompts/` for project-local agent extensions
- durable note conventions that can be mapped onto existing vault practices

The core loop remains stable even when specific tools change.

## Consequences

- new capabilities can be added locally without redesigning the whole system
- different projects can keep different durable note prefixes and external vault layouts
- the repository remains useful even if a specific delegate runtime is not installed
