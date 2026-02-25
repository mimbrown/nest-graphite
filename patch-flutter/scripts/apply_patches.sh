#!/usr/bin/env bash
set -euo pipefail

# Apply patches from patch-flutter/patches into the cloned flutter repo (./flock)
# Usage: apply_patches.sh [comma-separated-patch-list]

PATCH_LIST=${1:-}
PATCH_DIR="$(pwd)/patch-flutter/patches"

if [ ! -d flock ]; then
  echo "Error: ./flock directory not found. Run download_and_prepare_flutter.sh first."
  exit 2
fi

if [ -z "$PATCH_LIST" ]; then
  echo "No patches specified. Nothing to do."
  exit 0
fi

IFS=',' read -ra PATCHES <<< "$PATCH_LIST"
pushd flock >/dev/null
for p in "${PATCHES[@]}"; do
  p_trim=$(echo "$p" | xargs)
  src="$PATCH_DIR/$p_trim"
  if [ ! -f "$src" ]; then
    echo "Patch file not found: $src"
    exit 3
  fi
  echo "Applying patch $src"
  git apply --index "$src"
done
popd >/dev/null

echo "All patches applied (staged) in ./flock."

exit 0
