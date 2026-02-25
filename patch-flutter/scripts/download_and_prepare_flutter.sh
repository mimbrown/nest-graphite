#!/usr/bin/env bash
set -euo pipefail

# Downloads latest Flutter release (or a specific tag) and clones it into ./flock
# Usage: download_and_prepare_flutter.sh [<tag>]

TAG=${1:-}
OUT_DIR="flock"

# Default to the `stable` branch unless a specific tag/branch is provided.
if [ -z "$TAG" ]; then
  TAG="stable"
  echo "No tag supplied; defaulting to Flutter branch: $TAG"
else
  echo "Using requested Flutter tag/branch: $TAG"
fi

if [ -d "$OUT_DIR" ]; then
  echo "Removing existing $OUT_DIR"
  rm -rf "$OUT_DIR"
fi

echo "Cloning flutter@$TAG into $OUT_DIR..."
git clone --depth=1 --branch "$TAG" https://github.com/flutter/flutter.git "$OUT_DIR"

echo "Done."

exit 0
