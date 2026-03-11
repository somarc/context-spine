# Prerequisites

## Goal

Make explicit what `Context Spine` builds on so teams understand the shoulders it stands on.

## Recommended Wrapper Path

The README quick start uses `npm run ...` wrappers. For that path, verify these commands first:

```bash
git --version
python3 --version
bash --version
node --version
npm --version
command -v qmd && qmd status
```

## Minimal Direct-Script Path

If you do not want to use `npm`, you can run the shell and Python entrypoints directly. For that path, verify:

```bash
git --version
python3 --version
bash --version
command -v qmd && qmd status
```

## QMD Install Commands

If `qmd` is missing, use the official install commands:

```bash
npm install -g @tobilu/qmd
# or
bun install -g @tobilu/qmd
```

On macOS, QMD's official requirements also call for Homebrew SQLite:

```bash
brew install sqlite
```

## Required

- `git`
  - for repo history, branching, and remote collaboration
- `python3`
  - for the memory helper scripts
- `bash`
  - the bootstrap and helper scripts are written as bash entrypoints
- `node` + `npm`
  - required only if you want the `npm run context:*` wrapper commands from the README quick start

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

## Sources

- wrapper commands come from [package.json](../../package.json)
- bootstrap availability checks come from [scripts/context-spine/bootstrap.sh](../../scripts/context-spine/bootstrap.sh)
- qmd availability checks come from [scripts/context-spine/init-qmd.sh](../../scripts/context-spine/init-qmd.sh) and [scripts/context-spine/qmd-refresh.sh](../../scripts/context-spine/qmd-refresh.sh)
- official QMD install and requirements commands come from the [QMD README Quick Start](https://github.com/tobi/qmd#quick-start), [QMD Installation](https://github.com/tobi/qmd#installation), and [QMD Requirements](https://github.com/tobi/qmd#requirements)
