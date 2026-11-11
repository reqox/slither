#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/dist-artifacts"
rm -rf "${OUT}"
mkdir -p "${OUT}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. No host-side Node.js/Rust installation is needed." >&2
  exit 1
fi

docker buildx build \
  --file "${ROOT}/Dockerfile" \
  --tag lexi-builder:local \
  --output "type=local,dest=${OUT}" \
  "${ROOT}"

APPIMAGE="$(find "${OUT}" -maxdepth 1 -type f -name '*.AppImage' -print -quit)"
if [[ -z "${APPIMAGE}" ]]; then
  echo "Build completed but no AppImage artifact was exported." >&2
  exit 1
fi

mkdir -p "${ROOT}/dist"
cp "${APPIMAGE}" "${ROOT}/dist/Lexi.AppImage"
chmod +x "${ROOT}/dist/Lexi.AppImage"
echo "Built: ${ROOT}/dist/Lexi.AppImage"
