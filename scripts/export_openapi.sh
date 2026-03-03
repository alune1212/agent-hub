#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}" \
  uv run --project apps/api python -m app.tools.export_openapi --output apps/api/openapi.json
