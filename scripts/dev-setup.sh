#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# One-shot local dev setup for LicitScope.
# -----------------------------------------------------------------------------
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/.." && pwd)"

echo "→ Setting up API (Python venv)..."
cd "$root/apps/api"
python -m venv .venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash / MSYS)
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
pip install --upgrade pip
pip install -e ".[dev]"

echo "→ Seeding demo database..."
DATABASE_URL="sqlite:///./licitscope.db" python -m app.scripts.seed --if-empty

echo "→ Installing web dependencies..."
cd "$root/apps/web"
npm install --no-audit --no-fund

echo "✓ Done. Start the stack with:"
echo "    make api    # backend on :8000"
echo "    make web    # frontend on :3000"
