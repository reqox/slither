#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/dist/Lexi.AppImage"

if [[ ! -f "${APP}" ]]; then
  echo "Lexi.AppImage not found. Build it first with ./apps/lexi/scripts/build.sh" >&2
  exit 1
fi

chmod +x "${APP}"
exec "${APP}" --appimage-extract-and-run "$@"
