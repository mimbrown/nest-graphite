# Flutter Graphite Patching

Everything needed to turn a stock Flutter checkout into a Graphite-enabled one.
Used by the workflows in `.github/workflows/` (see `build-engines-v2.yml` and
the `prepare-flock` composite action).

## How an engine gets Graphite

1. Clone Flutter at a release tag into `./flock`, write a slim `.gclient`,
   and `gclient sync` (all handled by `.github/actions/prepare-flock`).
2. Clone [silnrsi/graphite](https://github.com/silnrsi/graphite) into
   `flock/engine/src/flutter/third_party/graphite` (pinned ref).
3. Run `scripts/graphite_harfbuzz_buildgn.py flock` — reads the **stock**
   harfbuzz BUILD.gn from the checkout's GN secondary source root
   (`engine/src/flutter/build/secondary/flutter/third_party/harfbuzz/`) and
   writes a Graphite-enabled version into the primary source root
   (`engine/src/flutter/third_party/harfbuzz/BUILD.gn`), which GN prefers.
   Because it transforms whatever the current Flutter version ships, it
   survives upstream harfbuzz source-list churn; it fails loudly if the stock
   file's structure changes beyond recognition.
4. Optionally apply `patches/unicode-0600-0603-fix.patch` **inside the Skia
   checkout** (`flock/engine/src/flutter/third_party/skia`) — it patches
   `modules/skparagraph` and `modules/skunicode`.

## Scripts

- `scripts/graphite_harfbuzz_buildgn.py` — generates the Graphite harfbuzz
  BUILD.gn (step 3 above)
- `scripts/download_and_prepare_flutter.sh` — clones a Flutter tag into `./flock`
- `scripts/apply_patches.sh` — applies patch files from `patches/` into `./flock`
  (only valid for patches that target the flutter repo itself, e.g. gclient files)

## Patches

- `patches/unicode-0600-0603-fix.patch` — Skia fix for Arabic-script
  (U+0600–U+0603) rendering: defensive cluster-table gap filling in
  skparagraph plus a bidi-region rewrite in skunicode. (A dropped line in
  the second hunk was repaired on 2026-07-04; verified to apply against
  the Skia revision pinned by Flutter 3.44.4.)
- `patches/add_slim_gclients.patch` — legacy; the slim `.gclient` files are
  now generated inline by the `prepare-flock` action.
