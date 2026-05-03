# Gatekeep 🚧

Keep your AI coding agents in check. Stop burning tokens. Stop them doing what they want.

Gatekeep is a lightweight worker proxy for Claude Code, Codex, OpenCode, and any CLI agent. It sits between your agent and your system — reading files through a cheap worker model, validating shell commands against rules, and blocking bad commits before they happen.

- **Save tokens** — use DeepSeek, Gemini, or any cheap model for reading files and generating boilerplate
- **Enforce rules** — agents can't modify config, delete models, or run dangerous commands
- **No setup hassle** — `curl | bash` install, one YAML config, works with any agent

Built for developers who love AI but hate watching their agent ignore instructions and burn through their weekly limit in 3 days.
