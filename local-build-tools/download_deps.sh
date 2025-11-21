#!/bin/bash

flutterRepo=flock
flutterInternalFolder=$flutterRepo/bin/internal
outDir=$flutterRepo/engine/src/out
targets=(
    $(<./$flutterInternalFolder/gradle_wrapper.version) \
    flutter_infra_release/ios-usb-dependencies/ios-deploy/$(<./$flutterInternalFolder/ios-deploy.version)/ios-deploy.zip \
    flutter_infra_release/ios-usb-dependencies/libimobiledevice/$(<./$flutterInternalFolder/libimobiledevice.version)/libimobiledevice.zip \
    flutter_infra_release/ios-usb-dependencies/libimobiledeviceglue/$(<./$flutterInternalFolder/libimobiledeviceglue.version)/libimobiledeviceglue.zip \
    flutter_infra_release/ios-usb-dependencies/libplist/$(<./$flutterInternalFolder/libplist.version)/libplist.zip \
    flutter_infra_release/ios-usb-dependencies/libusbmuxd/$(<./$flutterInternalFolder/libusbmuxd.version)/libusbmuxd.zip \
    $(<./$flutterInternalFolder/material_fonts.version) \
    flutter_infra_release/ios-usb-dependencies/openssl/$(<./$flutterInternalFolder/openssl.version)/openssl.zip
)
for target in "${targets[@]}"; do
    mkdir -p "$outDir/${target%/*}"
    echo Downloading https://storage.googleapis.com/$target
    curl -0 --output $outDir/$target \
        https://storage.googleapis.com/$target
done
echo Dependencies are downloaded and stored in proper folder hierarchy!