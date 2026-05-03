#!/usr/bin/env bash
# Gatekeep installer
# Usage: curl -fsSL https://raw.githubusercontent.com/Mongolianbrain/gatekeep/main/install.sh | bash

set -euo pipefail

GATEKEEP_HOME="${GATEKEEP_HOME:-$HOME/.local/share/gatekeep}"
BIN_DIR="${HOME}/.local/bin"
REPO="https://github.com/Mongolianbrain/gatekeep.git"
BRANCH="main"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚧 Installing Gatekeep...${NC}"

# Check for Python
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Python 3 is required but not found.${NC}"
    exit 1
fi

# Create directories
mkdir -p "$GATEKEEP_HOME" "$BIN_DIR"

# Clone or update
if [ -d "$GATEKEEP_HOME/.git" ]; then
    echo "   Updating existing installation..."
    git -C "$GATEKEEP_HOME" pull --ff-only origin "$BRANCH" 2>/dev/null || true
else
    echo "   Cloning repository..."
    git clone --depth 1 --branch "$BRANCH" "$REPO" "$GATEKEEP_HOME" 2>/dev/null || {
        # Fallback: download archive
        echo "   Git not available, downloading archive..."
        TMPDIR=$(mktemp -d)
        curl -fsSL "https://github.com/Mongolianbrain/gatekeep/archive/refs/heads/${BRANCH}.tar.gz" | tar -xz -C "$TMPDIR"
        cp -r "$TMPDIR/gatekeep-$BRANCH"/* "$GATEKEEP_HOME/"
        rm -rf "$TMPDIR"
    }
fi

# Create wrapper scripts in PATH
cat > "$BIN_DIR/ask-worker" << 'WRAPPER'
#!/usr/bin/env bash
exec python3 "${GATEKEEP_HOME}/src/gatekeep/ask_worker.py" "${@}"
WRAPPER
chmod +x "$BIN_DIR/ask-worker"

cat > "$BIN_DIR/gatekeep-init" << 'WRAPPER'
#!/usr/bin/env bash
# gatekeep-init: Install pre-commit hook in current project
GATEKEEP_HOME="${GATEKEEP_HOME:-$HOME/.local/share/gatekeep}"

if [ ! -d ".git" ]; then
    echo "❌ Not a git repository. Run from project root."
    exit 1
fi

# Copy pre-commit hook
cp "$GATEKEEP_HOME/src/gatekeep/pre_commit.py" ".git/hooks/pre-commit"
chmod +x ".git/hooks/pre-commit"
echo "✅ Gatekeep pre-commit hook installed."

# Copy default rules if not exists
if [ ! -f ".gatekeep.yaml" ]; then
    cp "$GATEKEEP_HOME/rules/default.yaml" ".gatekeep.yaml"
    echo "✅ .gatekeep.yaml created."
fi

echo ""
echo "🔍 Next steps:"
echo "   1. Set your worker API key:"
echo "      echo 'GATEKEEP_WORKER_KEY=sk-your-key' >> .env"
echo "   2. Add to CLAUDE.md:"
echo "      'Use ask-worker to read files >300 lines or 3+ files at once.'"
WRAPPER
chmod +x "$BIN_DIR/gatekeep-init"

echo ""
echo -e "${GREEN}✅ Gatekeep installed!${NC}"
echo ""
echo "   Commands added:"
echo "     ask-worker    — Read files through a cheap worker model"
echo "     gatekeep-init — Initialize Gatekeep in a project"
echo ""
echo "   📁 Installed at: $GATEKEEP_HOME"
echo ""
echo "   🔑 Set your API key:"
echo "      export GATEKEEP_WORKER_KEY='sk-your-deepseek-api-key'"
echo ""
echo "   Add to ~/.bashrc or ~/.zshrc to persist:"
echo "      export PATH=\"\$HOME/.local/bin:\$PATH\""
echo "      export GATEKEEP_WORKER_KEY='sk-your-key'"
