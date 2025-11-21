# Fetch engine dependencies
./flock/engine/src/flutter/bin/et fetch
# Build All Android Engines
./build_engine.sh build --platform android --all
# Build All Mac Engines
./build_engine.sh build --framework --platform mac --all
# Build All Web Engines
./build_engine.sh build --platform web --all
# Build All iOS Engines
./build_engine.sh build --framework --platform ios --all
echo Successfully built all engines for mac!
echo Upload Artifacts to //flutter-graphite-builds/flutter_infra_release/flutter/
# Download Dependencies and store in proper folder hierarchy
./download_deps.sh
# Download missing Flutter Engine Artifacts. Comment out if you plan to build with Linux as well.
./download_missing.sh
echo Upload flutter_infra_release folder to the GCP Bucket