# nest-graphite

Automated builds of the Flutter engine with [SIL Graphite](https://graphite.sil.org/)
support, published in the official artifact layout so the stock `flutter` tool can
consume them via `FLUTTER_STORAGE_BASE_URL`.

**Why:** rendering Graphite fonts (e.g. Awami Nastaliq) requires HarfBuzz to be
compiled with `graphite2`, which the stock Flutter engine does not include. This
repo rebuilds the engine for each Flutter stable release with Graphite enabled —
no framework fork, no tool fork, just replacement engine artifacts.

## How it works

Everything runs on free GitHub Actions runners in this public repo:

1. **`check-flutter-release.yml`** (daily, 05:00 UTC) — resolves the current
   Flutter stable version and its engine hash. If
   `gs://flutter-graphite-builds` doesn't have an `engine_stamp.json` for that
   hash, it dispatches a full build.
2. **`build-engines-v2.yml`** — the whole pipeline:
   - **build-linux / build-mac** — matrix over all engine configs (Android on
     ubuntu, macOS/iOS on macos runners, including the iOS `extension_safe`
     variants required by framework assembly). Each job checks out Flutter at
     the release tag, does a slim `gclient sync`, injects Graphite (see
     [`patch-flutter/`](patch-flutter/README.md)), builds, and verifies
     graphite symbols are present.
   - **frameworks** — restores the mac out-dirs and assembles
     `Flutter.xcframework`, `FlutterMacOS.framework`, gen_snapshots, etc.
     A hard assert checks every expected artifact exists before anything is
     published (the upstream framework scripts swallow errors).
   - **backfill** — copies the artifacts we don't rebuild (dart-sdk,
     sky_engine, patched SDKs, web SDK, windows/linux host artifacts, fonts,
     gradle wrapper…) from the official `flutter_infra_release` bucket at the
     same engine hash. Building at the release tag keeps hashes aligned, which
     is what makes this backfill valid.
   - **release** — uploads everything to the bucket and publishes
     `engine_stamp.json` **last**. The flutter tool treats the stamp as "this
     release exists", so a partial upload is never consumable.

Engine builds are pinned to
[silnrsi/graphite](https://github.com/silnrsi/graphite) and optionally carry a
Skia fix for U+0600–U+0603 rendering (`APPLY_SKIA_PATCH` repo variable,
currently `true`).

## Consuming the builds

One-time (any machine, using [fvm](https://fvm.app) fork support to keep a
separate engine cache):

```sh
fvm fork add graphite https://github.com/flutter/flutter.git
fvm install graphite/<version>          # e.g. graphite/3.44.4
```

Per project:

```sh
fvm use graphite/<version>
export FLUTTER_STORAGE_BASE_URL=https://storage.googleapis.com/flutter-graphite-builds
fvm flutter precache --android --ios
```

`FLUTTER_STORAGE_BASE_URL` must be set whenever building the project — Android
resolves engine AARs from `<base-url>/download.flutter.io` at Gradle build
time. Keep it per-project (e.g. direnv `.envrc`); **never export it globally**
or it will poison stock SDK caches. Stock Flutter keeps working side by side
via plain `fvm use <version>`.

Verify an installed engine has Graphite:

```sh
strings ~/fvm/versions/graphite/<version>/bin/cache/artifacts/engine/ios/Flutter.xcframework/ios-arm64/Flutter.framework/Flutter | grep -c graphite
```

## Runbook

- **Manual full release:** dispatch `build-engines-v2.yml` with
  `flutter_tag=<tag>`, `scope=full`, `upload_gcs=true`.
- **Smoke test:** `scope=smoke`, `upload_gcs=false` — builds one config per
  platform, publishes nothing.
- **Recovery** (some jobs failed but most artifacts exist): first try
  `gh run rerun <id> --failed`. If frameworks need re-assembly from a previous
  run's artifacts, dispatch with `frameworks_from_run=<run-id>`; add
  `recovery_build_configs=["ci/…"]` to rebuild specific missing configs.
- **Failure visibility:** production runs (`upload_gcs=true`) open a GitHub
  issue in this repo on failure, since cron-dispatched runs don't email anyone.

Configuration: `GCP_SA_KEY` secret (service account with `objectAdmin` on the
bucket only), `APPLY_SKIA_PATCH` variable. Bucket has a 240-day lifecycle
(~3 releases/month × ~4 GB ≈ a few dollars/month).

## Repo layout

- `.github/workflows/` — the two workflows above
- `.github/actions/` — `prepare-flock` (checkout + sync + graphite injection),
  `publish-outputs` (artifact/GCS upload)
- `patch-flutter/` — Graphite injection script and Skia patch
  ([details](patch-flutter/README.md))
- `local-build-tools/` — `build_engine.sh` → `build_engine_local.py`, the
  build/framework driver invoked by CI (also runnable locally against a
  prepared `./flock` checkout)

## History

Originally forked from [join-the-flock/nest](https://github.com/join-the-flock/nest);
the fork-maintenance tooling and the manual local build process were removed in
July 2026 once the CI pipeline shipped its first release (Flutter 3.44.4).
They're in git history if ever needed.
