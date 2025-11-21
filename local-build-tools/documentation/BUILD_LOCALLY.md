# Local Flutter Engine Build Guide

This guide explains how to use the local build scripts to compile Flutter engines on your macOS machine, converting the GitHub Actions workflow to bash and Python scripts.

## Prerequisites

Before you start, ensure you have:

1. **macOS 10.15+** (Catalina or later)
2. **Xcode 16.4+** (Required for building Flutter engines)
3. **Python 3.8+**
4. **Git** (already installed with Xcode)
5. **Command Line Tools for Xcode**

### Initial Setup

#### 1. Install Command Line Tools

```bash
xcode-select --install
```

#### 2. Install Xcode (if not already installed)

Download from [App Store](https://apps.apple.com/us/app/xcode/id497799835) or [Apple Developer](https://developer.apple.com/download/all/)

Verify Xcode version:
```bash
xcodebuild -version
```

Should show version 16.4 or higher.

#### 3. Clone the Repository

```bash
git clone https://github.com/mimbrown/nest-graphite.git
cd nest-graphite
```

#### 4. Setup depot_tools (one-time)

```bash
./build_engine.sh setup --depot-tools
```

Then add to your `~/.zshrc` or `~/.bash_profile`:

```bash
export PATH="$HOME/depot_tools:$PATH"
```

Reload your shell:
```bash
source ~/.zshrc
```

## Quick Start

### List Available Configurations

See all available build targets:

```bash
./build_engine.sh list
```

This shows:
- **macOS builds** (21 configurations)
- **iOS builds** (11 configurations)
- **Android builds** (9 configurations for macOS runners)

### Build a Single Configuration

#### Build macOS Debug (arm64)

```bash
./build_engine.sh build --platform mac --config ci/mac_debug_arm64
```

#### Build iOS Debug

```bash
./build_engine.sh build --platform ios --config ci/ios_debug
```

#### Build Android Debug (arm64)

```bash
./build_engine.sh build --platform android --config android_debug_arm64
```

### Build All Configurations for a Platform

#### Build All macOS Engines

```bash
./build_engine.sh build --platform mac --all
```

#### Build All iOS Engines

```bash
./build_engine.sh build --platform ios --all
```

#### Build All Android Engines (macOS runner)

```bash
./build_engine.sh build --platform android --all
```

### Enable Verbose Output

For detailed build information:

```bash
./build_engine.sh build --platform mac --config ci/mac_debug_arm64 --verbose
```

Or use the Python script directly:

```bash
python3 build_engine_local.py --verbose --platform mac --config ci/mac_debug_arm64
```

## Understanding Build Configurations

### macOS Configurations

| Name | Config | Purpose |
|------|--------|---------|
| mac debug arm64 | `ci/mac_debug_arm64` | Debug build for Apple Silicon |
| mac debug framework arm64 | `ci/mac_debug_framework_arm64` | Debug framework for Apple Silicon |
| mac profile arm64 | `ci/mac_profile_arm64` | Profiling build for Apple Silicon |
| mac release arm64 | `ci/mac_release_arm64` | Release build for Apple Silicon |
| mac host debug | `ci/host_debug` | Debug build for current architecture |
| mac host debug framework | `ci/host_debug_framework` | Debug framework build |
| mac host release | `ci/host_release` | Release build for current architecture |

### iOS Configurations

| Name | Config | Purpose |
|------|--------|---------|
| ios debug | `ci/ios_debug` | Debug build for physical device |
| ios debug sim | `ci/ios_debug_sim` | Debug build for iOS Simulator (x64) |
| ios debug sim arm64 | `ci/ios_debug_sim_arm64` | Debug build for iOS Simulator (arm64) |
| ios profile | `ci/ios_profile` | Profiling build |
| ios release | `ci/ios_release` | Release build |

### Android Configurations (macOS)

| Name | Config | Purpose |
|------|--------|---------|
| android debug arm64 | `android_debug_arm64` | Debug build for arm64 |
| android debug unopt | `android_debug_unopt` | Unoptimized debug build |
| android profile | `ci/android_profile` | Profiling build |
| android release | `ci/android_release` | Release build |

## Build Output Locations

After a successful build, find artifacts in:

```
flock/engine/src/out/[config_name]/
```

Example paths:
- macOS debug: `flock/engine/src/out/ci/mac_debug_arm64/`
- iOS debug: `flock/engine/src/out/ci/ios_debug/`
- Android debug: `flock/engine/src/out/android_debug_arm64/`

## Pre-Build Checks

### Check Xcode Installation

```bash
./build_engine.sh check --xcode
```

This will display:
- Current Xcode path
- Xcode version information
- CLT status

### Verify Python Installation

```bash
python3 --version
```

Should show Python 3.8 or higher.

### Verify Git

```bash
git --version
```

## Using the Python Script Directly

If you prefer to use the Python script directly without the bash wrapper:

```bash
python3 build_engine_local.py --list
```

```bash
python3 build_engine_local.py --platform mac --config ci/mac_debug_arm64 --verbose
```

```bash
python3 build_engine_local.py --platform ios --all
```

## Advanced Usage

### Custom Workspace Path

```bash
./build_engine.sh build --workspace /custom/path --platform mac --config ci/mac_debug_arm64
```

Or with Python:

```bash
python3 build_engine_local.py --workspace /custom/path --platform mac --config ci/mac_debug_arm64
```

### Building Frameworks

After building individual engines, create frameworks:

```bash
# After building framework engine configs
python3 -c "
import sys
sys.path.insert(0, '.')
from build_engine_local import FlutterEngineBuilder

builder = FlutterEngineBuilder()
builder.create_macos_frameworks({
    'ci/mac_debug_framework_arm64': 'out/ci/mac_debug_framework_arm64',
    'ci/host_debug_framework': 'out/ci/host_debug_framework'
})
"
```

## Troubleshooting

### "Command not found: python3"

Install Python 3 from:
- [python.org](https://www.python.org/downloads/)
- Homebrew: `brew install python3`

### "Xcode version check failed"

Ensure Xcode 16.4+ is installed:

```bash
xcode-select --install
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
```

### Build fails with "depot_tools: command not found"

Make sure depot_tools is set up:

```bash
./build_engine.sh setup --depot-tools
export PATH="$HOME/depot_tools:$PATH"
```

### "flock directory not found"

Ensure you're in the workspace root and the flock directory is checked out:

```bash
git status
ls -la flock/
```

If flock is missing, you may need to check it out or initialize it.

### Memory or Build Issues

For faster builds or on systems with limited resources, try building one configuration at a time instead of using `--all`.

Large builds can take 30+ minutes depending on:
- Configuration complexity
- System specs (CPU cores, RAM, disk speed)
- Whether it's the first build (caches empty)

## Key Differences from GitHub Actions

The local build scripts differ from the GitHub Actions workflow in:

1. **No automatic uploads** - Built artifacts stay on your machine
2. **No cross-platform matrix** - Run builds that match your current platform (macOS)
3. **Manual framework creation** - Framework creation scripts need to be run separately if needed
4. **No GCP integration** - Can't upload to Google Cloud Storage
5. **Direct Xcode control** - Uses your locally installed Xcode (vs. setup in Actions)

## Environment Variables

You can configure builds with environment variables:

```bash
# Set Flutter branch (default: stable)
export FLUTTER_BRANCH=stable
./build_engine.sh build --platform mac --config ci/mac_debug_arm64

# Disable Xcode toolchain (already set by default)
export DEPOT_TOOLS_WIN_TOOLCHAIN=0
```

## Performance Tips

1. **Use an SSD** - Engine builds are I/O intensive
2. **Build on main partition** - Avoid network storage
3. **Close other applications** - Free up RAM (engine builds need 8GB+)
4. **Use debug configs first** - Faster than release builds
5. **Reuse caches** - Don't delete `flock/engine/src/out/` between builds

## Getting Help

For issues specific to:

- **Flutter engine**: https://github.com/flutter/flutter
- **Graphite/Flock**: https://github.com/mimbrown/nest-graphite
- **Build scripts**: Check the `build_engine_local.py` source code or run with `--verbose`

## Next Steps

After successful builds:

1. **Use the engine** - Point Flutter to your custom engine build
2. **Run tests** - Verify your build with Flutter tests
3. **Iterate** - Make changes and rebuild quickly
4. **Optimize** - Adjust configurations based on your needs

Good luck with your Flutter engine builds! 🚀
