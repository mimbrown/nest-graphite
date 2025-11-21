# Fetch engine dependencies
./flock/engine/src/flutter/bin/et fetch
# Build All Android Engines
./build_engine.sh build --platform androidlinux --all
# Build All Linux Engines
./build_engine.sh build --framework --platform linux --all
# Build All Web Engines
./build_engine.sh build --platform web --all
echo Successfully built all engines for mac!
echo Upload Artifacts to //flutter-graphite-builds/flutter_infra_release/flutter/
# Download Dependencies and store in proper folder hierarchy
./download_deps.sh
echo Upload flutter_infra_release folder to the GCP Bucket