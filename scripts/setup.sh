#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "── Topiome setup ─────────────────────────────────────────────"
echo "root: $ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv bulunamadı. Kurulum: https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ .env oluşturuldu"
fi

echo "→ Python bağımlılıkları (uv sync)"
npm --prefix apps/web install
(cd apps/api && uv sync --python 3.12 --extra dev)

echo "→ Veritabanı (Alembic migration) ve demo verisi"
(cd apps/api && uv run python -m app.seed)

echo ""
echo "✓ Hazır."
echo "  Web:  npm run dev:web   → http://localhost:3000"
echo "  API:  npm run dev:api   → http://localhost:8000/docs"
echo "  Demo: demo@topiome.com / demo1234"
