#!/usr/bin/env python3
"""Gatekeep ask-worker: read files through a cheap worker model.

Installed to PATH by install.sh. Delegates to src/gatekeep/ask_worker.py.
"""
import sys
import os

# Find the real script relative to this symlink/script
script_dir = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(script_dir, "..", "src", "gatekeep", "ask_worker.py")

if os.path.exists(src):
    # Add src parent to path and run
    sys.path.insert(0, os.path.join(script_dir, "..", "src"))
    from gatekeep.ask_worker import main
    main()
else:
    # Fallback: try installed location
    sys.path.insert(0, os.path.expanduser("~/.local/share/gatekeep/src"))
    try:
        from gatekeep.ask_worker import main
        main()
    except ImportError as e:
        print(f"❌ Gatekeep not found. Run 'gatekeep install' or check installation.", file=sys.stderr)
        print(f"   Error: {e}", file=sys.stderr)
        sys.exit(1)
