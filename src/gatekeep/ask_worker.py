"""ask-worker: Read files through a cheap worker model instead of Claude.

Usage:
  ask-worker <file> [<file>...] <question>
  ask-worker <file> [<file>...] -q <question>

Reads specified files, sends them to the worker model (DeepSeek by default),
and returns a concise summary answering your question. Saves 10-100x tokens
compared to having Claude read the files directly.
"""

import argparse
import os
import sys
import json
import pathlib
import urllib.request


WORKER_MODEL = os.environ.get("GATEKEEP_WORKER_MODEL", "deepseek-chat")
WORKER_API_URL = os.environ.get("GATEKEEP_WORKER_URL", "https://api.deepseek.com/v1/chat/completions")
WORKER_API_KEY = os.environ.get("GATEKEEP_WORKER_KEY", "")


def read_files(paths: list[str]) -> list[dict]:
    """Read files and return list of {path, content} dicts."""
    docs = []
    for p in paths:
        path = pathlib.Path(p)
        if not path.exists():
            print(f"⚠ File not found: {p}", file=sys.stderr)
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        # Truncate huge files to prevent blowing context
        lines = content.splitlines()
        if len(lines) > 3000:
            lines = lines[:3000]
            content = "\n".join(lines) + "\n... [truncated at 3000 lines]"
        docs.append({"path": str(path), "content": content})
    return docs


def build_corpus(docs: list[dict]) -> str:
    """Pack docs into an XML-like corpus."""
    parts = []
    for d in docs:
        parts.append(f'<file path="{d["path"]}">\n{d["content"]}\n</file>')
    return "\n\n".join(parts)


def ask_worker(corpus: str, question: str) -> str:
    """Send corpus + question to the worker model."""
    if not WORKER_API_KEY:
        return "❌ GATEKEEP_WORKER_KEY not set. Set it in your environment or add to .env."

    system_prompt = (
        "You are a precise code analyst. "
        "Read the provided files and answer the user's question concisely. "
        "Be accurate and direct. Include file paths and line numbers when relevant. "
        "Keep responses under 500 words unless more detail is requested."
    )

    payload = json.dumps({
        "model": WORKER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"<corpus>\n{corpus}\n</corpus>"},
            {"role": "user", "content": question},
        ],
        "max_tokens": 4096,
        "temperature": 0.1,
    }).encode()

    req = urllib.request.Request(
        WORKER_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {WORKER_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return f"❌ API error ({e.code}): {body}"
    except Exception as e:
        return f"❌ Error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Gatekeep ask-worker — read files through a cheap model",
        usage="ask-worker <file> [<file>...] -q <question>",
    )
    parser.add_argument("files", nargs="*", help="Files to read")
    parser.add_argument("-q", "--question", required=True, help="Your question about the files")
    args = parser.parse_args()

    if not args.files:
        # Read from stdin — useful for piping file lists
        files = [line.strip() for line in sys.stdin if line.strip()]
    else:
        files = args.files

    if not files:
        parser.print_help()
        sys.exit(1)

    docs = read_files(files)
    if not docs:
        print("❌ No files could be read.", file=sys.stderr)
        sys.exit(1)

    corpus = build_corpus(docs)
    response = ask_worker(corpus, args.question)
    print(response)


if __name__ == "__main__":
    main()
