#!/bin/bash

# These files are missing after building on the Mac. I believe Linux builds them,
# but this is a workaround for Mac users.

flutterRepo=flock
flutterInternalFolder=$flutterRepo/bin/internal
# Get Engine Hash
engineVersion=$(<./$flutterInternalFolder/engine.version)
while [[ ${#engineVersion} -ne 40 ]]; do
    sleep 1
done
outDir=$flutterRepo/engine/src/out
infraDir=flutter_infra_release/flutter/$engineVersion
targets=(
    $infraDir/android-arm/linux-x64.zip \
    $infraDir/android-arm-profile/linux-x64.zip \
    $infraDir/android-arm-release/linux-x64.zip \
    $infraDir/windows-x64/artifacts.zip \
    $infraDir/windows-x64/font-subset.zip \
    $infraDir/linux-x64/artifacts.zip \
    $infraDir/linux-x64/font-subset.zip \
    $infraDir/dart-sdk-linux-x64.zip \
    $infraDir/dart-sdk-windows-x64.zip \
    $infraDir/android-x64/artifacts.zip \
    $infraDir/android-x86/artifacts.zip \
    $infraDir/android-x86-profile/artifacts.zip \
    $infraDir/android-x86-release/artifacts.zip \
    $infraDir/engine_stamp.json
    $infraDir/flutter_gpu.zip \
    $infraDir/flutter_patched_sdk.zip \
    $infraDir/flutter_patched_sdk_product.zip
    $infraDir/sky_engine.zip
)
for target in "${targets[@]}"; do
    dest=$outDir/$target
    if [ ! -f $dest ]; then
        mkdir -p "$outDir/${target%/*}"
        echo Downloading https://storage.googleapis.com/$target
        curl -0 --output $dest \
            https://storage.googleapis.com/$target
    else
        echo Skipped. Already exists: $target
    fi
done
echo Dependencies are downloaded and stored in proper folder hierarchy!