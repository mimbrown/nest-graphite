# GitHub Actions for Flutter Engine Builds

This folder contains scripts and patches used by the GitHub Actions workflows in `.github/workflows/`.

## Scripts

- `scripts/download_and_prepare_flutter.sh` — clones the requested (or latest) Flutter release into `./flock`
- `scripts/apply_patches.sh` — applies patch files from `patch-flutter/patches/` into the cloned `flock` repo

## Patches

Located in `patch-flutter/patches/`:
- `add_slim_gclients.patch` — custom gclient files for slim builds (applied by default)
- `unicode-0600-0603-fix.patch` — Unicode handling fix for Skia

## Workflows

### `build-engines.yml` (Main Workflow)

Unified parallel workflow that builds all engine configurations across macOS, iOS, Android, Linux, and Web platforms.

**Features:**
- Automatic matrix strategy: each build configuration runs in a separate parallel job
- Supports up to ~60 concurrent engine builds
- Framework creation jobs depend on individual builds completing first
- Optional GCP artifact upload
- Scheduled daily runs + manual dispatch

**Dispatch Inputs:**
- `flutter_tag` — Optional Flutter release tag (defaults to latest)
- `apply_patches` — Enable patch application (default: true)
- `patches` — Comma-separated patch names (default: `add_slim_gclients.patch`)
- `gcp_bucket` — Optional GCP bucket for artifact storage
- `gcp_credentials_base64` — Optional base64-encoded GCP service account key

**Job Structure:**
```
├── build-mac (21 configs parallel)
├── build-ios (11 configs parallel)
├── build-android-mac (9 configs parallel)
├── build-android-linux (15 configs parallel)
├── build-linux (10 configs parallel)
├── build-web (2 configs parallel)
├── create-mac-frameworks (depends on build-mac, build-ios, build-android-mac)
└── create-ios-frameworks (depends on build-ios)
```

## Usage

### Trigger manually from GitHub Actions tab

1. Go to **Actions** → **Build Flutter Engines (Parallel Matrix)**
2. Click **Run workflow**
3. Configure inputs:
   - Set `apply_patches: true` to apply patches
   - Provide `gcp_bucket` and `gcp_credentials_base64` if uploading artifacts
   - Optionally specify a `flutter_tag`

### Automatic scheduled runs

- Runs daily at UTC 4:00 (configurable in workflow)
- Uses default inputs (patches applied, no GCP upload)

## Integration with build_engine.sh

The workflow invokes `./build_engine.sh build --config <config_name>` for each matrix entry, which in turn calls `build_engine_local.py`. The Python script knows all available configurations and handles the full build pipeline.

## GCP Uploads

If `gcp_bucket` and `gcp_credentials_base64` are provided:
- Individual build outputs are tarred and uploaded to `gs://bucket/flutter_infra_release/flutter/<engine-hash>/`
- Framework archives are uploaded separately after creation

