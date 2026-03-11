# Prerequisites

## Goal

Make explicit what `Context Spine` builds on so teams understand the shoulders it stands on.

## Required

- `git`
  - for repo history, branching, and remote collaboration
- `python3`
  - for the memory helper scripts
- a POSIX shell
  - the bootstrap and helper scripts are written for `bash`/`zsh` style environments

## Strongly Recommended

- `qmd`
  - this is the retrieval layer that turns repo memory, docs, and vault notes into one query plane
- an external durable note system
  - Obsidian is a strong fit, but the key requirement is linked, durable, searchable notes outside the repo

## Optional but High-Value

- local agent runtime extensions under `.pi/`
- `ollama` or another local model backend
- `tmux` for bounded parallel work
- GitHub Actions or another CI runner
- a visual explainer workflow for complex retrieved context

## Prior Art / Dependencies

Context Spine deliberately builds on existing tools instead of reinventing them:

- Git for source-of-truth history
- QMD for retrieval
- Markdown and linked notes for durable knowledge
- existing agent runtimes for execution and delegation
- self-contained HTML for visual explainers

## Principle

Context Spine is an intelligence layer, not a replacement stack. Its value comes from connecting these surfaces into one operating loop.
