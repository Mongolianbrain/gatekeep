# Gatekeep Rules

Gatekeep is installed. Follow these rules to save tokens and stay within limits.

## File Reading
- Files >300 lines → use `ask-worker <file>` to read them
- 3+ files at once → use `ask-worker <file1> <file2> -q "explain"` first
- Use `ask-worker -q "summarize"` to get file overviews before deep work

## Code Generation
- Boilerplate, tests, configs → generate with `ask-worker`
- Architecture decisions, debugging, safety-critical → do NOT delegate

## Commands
- One bash command per message
- Describe your environment before writing a response
- Do NOT modify `.gatekeep.yaml` or `GATEKEEP_*` env vars
- Do NOT delete or modify Gatekeep installation files
