#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rm -rf "${ROOT}/dist" "${ROOT}/dist-artifacts" "${ROOT}/node_modules" "${ROOT}/src-tauri/target"
echo "Lexi build artifacts cleaned."
