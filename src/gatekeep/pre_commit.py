#!/usr/bin/env python3
"""Gatekeep pre-commit hook: validate staged changes before commit.

Installed by 'gatekeep init' into .git/hooks/pre-commit.
Checks staged diffs against rules in gatekeep.yaml.
"""
import os
import sys
import subprocess
import pathlib


def find_rules() -> str | None:
    """Find gatekeep rules file in project or user home."""
    # Project-level
    local = pathlib.Path(".gatekeep.yaml")
    if local.exists():
        return str(local)
    # Fallback: user-level
    user = pathlib.Path.home() / ".config" / "gatekeep" / "rules.yaml"
    if user.exists():
        return str(user)
    return None


def get_staged_diff() -> str:
    """Get staged diff (what would be committed)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat", "--diff-filter=ACMR"],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout


def get_staged_files() -> list[str]:
    """Get list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, timeout=10
    )
    return [f for f in result.stdout.splitlines() if f]


def check_max_size(diff_stat: str) -> list[str]:
    """Check if commit is too large."""
    issues = []
    lines = diff_stat.splitlines()
    total_changes = len(lines)

    if total_changes > 20:
        issues.append(f"⚠ Commit touches {total_changes} files (max 20 recommended). Consider splitting.")

    for line in lines:
        parts = line.split()
        if len(parts) >= 4 and "+++" not in line and "---" not in line:
            try:
                changes = int(parts[-1].replace("+", "").replace("-", "")) if parts[-1].isdigit() else 0
                if changes > 500:
                    issues.append(f"⚠ {parts[0]}: {changes} changes (max 500 recommended).")
            except (ValueError, IndexError):
                pass

    return issues


def check_config_changes(files: list[str]) -> list[str]:
    """Check if commit modifies gatekeep or agent configs."""
    issues = []
    blocked_paths = [".gatekeep.yaml", "gatekeep.yaml"]
    for f in files:
        if f in blocked_paths:
            issues.append(f"❌ Blocked: commit modifies {f} which should be in .gitignore.")
        if ".hermes" in f or f.endswith("CLAUDE.md"):
            issues.append(f"⚠ Warning: commit modifies {f}.")
    return issues


def main():
    print("🔍 Gatekeep pre-commit check...")

    files = get_staged_files()
    if not files:
        print("   No staged files. Skipping.")
        sys.exit(0)

    diff_stat = get_staged_diff()

    issues = []
    issues.extend(check_max_size(diff_stat))
    issues.extend(check_config_changes(files))

    if issues:
        print()
        for issue in issues:
            print(f"   {issue}")
        print()
        print("   Commit blocked. Fix issues above or run: git commit --no-verify")
        sys.exit(1)

    print("   ✅ All checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
