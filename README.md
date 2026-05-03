<div align="center">
  <h1>🚧 Gatekeep</h1>
  <p><strong>Worker proxy for AI coding agents.</strong><br/>
  Save tokens. Enforce rules. Stop bad commits.</p>
  <p>
    <a href="#quick-start">Quick Start</a> •
    <a href="#how-it-works">How It Works</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#why-gatekeep">Why Gatekeep</a>
  </p>
</div>

---

**Gatekeep** sits between your AI coding agent (Claude Code, Codex, OpenCode) and your system. It delegates expensive I/O to a cheap worker model and blocks unauthorized changes — so your agent stops burning tokens and doing things you didn't ask for.

## Quick Start

```bash
# 1. Install
curl -fsSL https://raw.githubusercontent.com/Mongolianbrain/gatekeep/main/install.sh | bash

# 2. Set your API key (DeepSeek recommended — $0.27/million tokens)
export GATEKEEP_WORKER_KEY='sk-your-deepseek-api-key'

# 3. Initialize in your project
cd your-project
gatekeep-init
```

That's it. `ask-worker` is now in your PATH and Claude can use it.

## How It Works

### Without Gatekeep

```
You → Claude → reads files directly (8000 tokens) → writes code → commits
```

Claude has full access: reads huge files, generates boilerplate with its expensive model, and can modify anything including its own configuration.

### With Gatekeep

```
You → Claude → ask-worker (400 tokens) → Claude writes code → pre-commit validates
                     ↓
              DeepSeek / Gemini / cheap model
```

Gatekeep adds two guardrails:

1. **`ask-worker`** — Claude tells Gatekeep to read files. Gatekeep delegates to a cheap model that returns a summary. Claude never sees the raw file.
2. **`pre-commit`** — Before each commit, Gatekeep validates against rules (max file size, blocked config changes, etc.). If a rule is violated, the commit is blocked.

### Cost Comparison

| Task | Claude Direct | Via Gatekeep | Savings |
|---|---|---|---|
| Read 3 files (500 lines each) | ~12,000 tokens | ~600 tokens (summary) | **20x** |
| Generate test boilerplate | ~4,000 tokens | ~400 tokens (worker) | **10x** |
| Update documentation | ~5,000 tokens | ~200 tokens (worker) | **25x** |

Worker model cost: ~$0.38 per 3 weeks of daily engineering work.

## Components

### `ask-worker`

Reads files through a cheap worker model and returns concise answers.

```bash
# Read and summarize
ask-worker src/app.ts -q "What exports does this file have?"

# Multiple files with context
ask-worker src/*.ts -q "How does authentication work?"

# Large codebase exploration
ask-worker src/models/*.ts src/routes/*.ts -q "Find all database queries"
```

### `gatekeep-init`

One-command setup for any project:

```bash
cd your-project
gatekeep-init
# ✅ Pre-commit hook installed
# ✅ .gatekeep.yaml created
```

### Pre-commit Hook

Validates staged changes before they reach your repo:

- Blocks commits that modify gatekeep config
- Warns on commits touching `.hermes` or `CLAUDE.md`
- Flags oversized commits (20+ files or 500+ changes per file)

### CLAUDE.md Template

Add this to your project's `CLAUDE.md`:

```markdown
# Gatekeep Rules

## File Reading
- Files >300 lines → use `ask-worker` to read them
- 3+ files at once → use `ask-worker` before processing
- Use `ask-worker -q "summarize"` to get file overviews

## Code Generation
- Boilerplate, tests, configs → generate with `ask-worker`
- Architecture, debugging, safety-critical → do NOT delegate
```

## Configuration

All rules live in `.gatekeep.yaml` at your project root:

```yaml
worker:
  model: deepseek-chat  # or gemini-2.0-flash, gpt-4o-mini
  api_url: https://api.deepseek.com/v1/chat/completions

delegate:
  read_large_files: true
  generate_boilerplate: true
  never_delegate:
    - debugging
    - architecture_decisions

rules:
  max_files_per_commit: 20
  max_changes_per_file: 500

block:
  commands:
    - pattern: "rm.*\\.hermes"
      reason: "Never modify Hermes configuration"
  config_changes:
    - .gatekeep.yaml
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GATEKEEP_WORKER_KEY` | — | Your worker model API key **(required)** |
| `GATEKEEP_WORKER_MODEL` | `deepseek-chat` | Worker model name |
| `GATEKEEP_WORKER_URL` | `https://api.deepseek.com/v1/chat/completions` | API endpoint |

## Why Gatekeep?

**The problem:** AI coding agents are incredibly useful but they:
- **Burn through tokens** — Claude reads 8000 tokens for a file you need summarized
- **Ignore instructions** — they modify configs, delete models, repeat prompts
- **Have no boundaries** — they access everything, change anything

Gatekeep solves this not by *asking* the agent to behave, but by **restricting what it can do**. The agent's instructions are suggestions. Gatekeep's rules are enforced in code.

## Supported Agents

- **Claude Code** — via Bash tool calling `ask-worker`
- **Codex** — via shell commands
- **OpenCode** — via terminal integration
- **Any CLI agent** — Gatekeep is agent-agnostic

## License

MIT
