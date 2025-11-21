# Local Flutter Engine Build System

## Overview

This directory now contains a complete local build system that converts the GitHub Actions workflow (`build-and-upload-engine-variants.yaml`) into bash and Python scripts you can run directly on your macOS machine.

## What's Included

### 📜 Scripts

1. **`build_engine.sh`** (Main entry point)
   - Bash wrapper for easy command-line access
   - Colored output and user-friendly interface
   - Commands: `list`, `build`, `check`, `setup`, `help`

2. **`build_engine_local.py`** (Core build engine)
   - Python 3 application that orchestrates builds
   - Supports all platforms: macOS, iOS, Android, Linux, Web
   - Manages 50+ build configurations
   - Command-line interface with detailed help

3. **`build_utilities.sh`** (Helper utilities)
   - Manage build artifacts and artifacts
   - Monitor builds in real-time
   - Clean up old builds
   - Compare build sizes and timestamps
   - Commands: `status`, `clean`, `list-builds`, `watch`, `compare`

4. **`build_utils.py`** (Advanced utilities library)
   - Framework creation helpers (macOS, iOS)
   - Artifact management and metadata tracking
   - Build cache system for faster access
   - JSON-based build history

### 📚 Documentation

1. **`BUILD_LOCALLY.md`** (Comprehensive guide)
   - Complete setup instructions
   - Detailed configuration reference
   - Troubleshooting guide
   - Performance tips

2. **`QUICK_START.md`** (Fast reference)
   - One-time installation steps
   - Most common commands
   - Build time estimates
   - Quick troubleshooting

3. **`README_LOCAL_BUILDS.md`** (This file)
   - Overview of the build system
   - File structure and purpose
   - Quick commands reference

## Quick Start

### First Time Setup (5 minutes)

```bash
# Make scripts executable
chmod +x build_engine.sh build_utilities.sh

# Setup depot_tools (one-time)
./build_engine.sh setup --depot-tools

# Add to shell profile (~/.zshrc)
export PATH="$HOME/depot_tools:$PATH"
```

### Run Your First Build

```bash
# List available builds
./build_engine.sh list

# Build macOS debug (fastest option to test)
./build_engine.sh build --platform mac --config ci/mac_debug_arm64

# Check build progress
./build_utilities.sh status
```

## File Structure

```
nest-graphite/
├── build_engine.sh              # Main command-line interface
├── build_engine_local.py        # Core build engine (Python)
├── build_utilities.sh           # Helper utilities script
├── build_utils.py               # Advanced utilities library
├── BUILD_LOCALLY.md             # Comprehensive documentation
├── QUICK_START.md               # Quick reference guide
└── flock/
    └── engine/
        └── src/
            └── out/
                ├── ci/mac_debug_arm64/
                ├── ci/ios_debug/
                └── ... (build outputs)
```

## Common Commands

### Build Commands

```bash
# List all available configurations
./build_engine.sh list

# Build a single configuration
./build_engine.sh build --platform mac --config ci/mac_debug_arm64

# Build all configs for a platform
./build_engine.sh build --platform mac --all

# Build with verbose output
./build_engine.sh build --platform ios --config ci/ios_debug --verbose
```

### Utility Commands

```bash
# Show build status
./build_utilities.sh status

# List completed builds
./build_utilities.sh list-builds

# See output directory for a config
./build_utilities.sh list-outputs ci/mac_debug_arm64

# Monitor a build in real-time
./build_utilities.sh watch ci/mac_debug_arm64

# Compare builds by size and date
./build_utilities.sh compare

# Clean build artifacts
./build_utilities.sh clean

# Remove everything (builds + cache + metadata)
./build_utilities.sh clean-all
```

### Setup Commands

```bash
# Check Xcode installation
./build_engine.sh check --xcode

# Setup depot_tools (one-time)
./build_engine.sh setup --depot-tools
```

## Platform Support

### macOS (21 configurations)
- ✅ Fully supported
- arm64, x64 variants
- Debug, profile, release modes
- Framework creation support

### iOS (11 configurations)
- ✅ Fully supported
- Device and simulator builds
- arm64, x64 variants
- Extension-safe variants

### Android (9 configurations)
- ✅ Supported on macOS runners
- arm64, x64, x86 architectures
- Debug, profile, release modes

### Linux & Web
- 📋 Not yet fully implemented for local builds
- Would require Linux-specific tools

## Build Configurations

### macOS Examples
- `ci/mac_debug_arm64` - Debug for Apple Silicon
- `ci/mac_profile_arm64` - Profiling build
- `ci/mac_release_arm64` - Optimized release
- `ci/host_debug` - Native architecture debug
- `ci/host_debug_framework` - Framework debug build

### iOS Examples
- `ci/ios_debug` - Device debug
- `ci/ios_debug_sim` - Simulator debug (x64)
- `ci/ios_debug_sim_arm64` - Simulator debug (Apple Silicon)
- `ci/ios_profile` - Profiling build
- `ci/ios_release` - Release build

### Android Examples (macOS)
- `android_debug_arm64` - Debug arm64
- `ci/android_profile` - Profile build
- `ci/android_release` - Release build

## Output Locations

Builds are placed in:

```
flock/engine/src/out/[config_name]/
```

Examples:
```
flock/engine/src/out/ci/mac_debug_arm64/
flock/engine/src/out/ci/ios_debug/
flock/engine/src/out/ci/android_release/
```

## Python Usage

You can also use the build system directly from Python:

```python
from build_engine_local import FlutterEngineBuilder, Platform

builder = FlutterEngineBuilder(verbose=True)

# Build single config
builder.build_mac_engine("ci/mac_debug_arm64")

# Build multiple configs
configs = builder.MAC_CONFIGS
results = builder.build_multiple(configs)
```

For advanced operations:

```python
from build_utils import FrameworkBuilder, ArtifactManager, BuildCache

# Create frameworks
fw_builder = FrameworkBuilder(Path("flock/engine/src"), verbose=True)
fw_builder.create_macos_debug_framework()

# Manage artifacts
manager = ArtifactManager()
manager.print_summary()

# Use cache
cache = BuildCache()
cached = cache.get_cached_build("ci/mac_debug_arm64")
```

## Typical Build Times

| Build Type | Duration | Notes |
|------------|----------|-------|
| Debug | 15-30 min | Unoptimized, fastest |
| Profile | 30-45 min | Medium optimization |
| Release | 45-60 min | Full optimization |
| All macOS | 2-4 hours | Sequential builds |

⏱️ Times vary based on CPU, RAM, disk speed, and cache state

## Requirements

### Hardware Recommended
- **CPU**: 4+ cores (8+ cores recommended)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Disk**: 50GB+ free space (SSD highly recommended)

### Software Required
- **macOS**: 10.15 (Catalina) or later
- **Xcode**: 16.4 or later
- **Python**: 3.8 or later
- **Git**: 2.0 or later

## Troubleshooting

### Quick Fixes

**Command not found errors:**
```bash
# Ensure PATH is set correctly
export PATH="$HOME/depot_tools:$PATH"

# For permanent fix, add to ~/.zshrc or ~/.bash_profile
```

**Xcode issues:**
```bash
# Check version
xcodebuild -version

# Install or update
xcode-select --install
```

**Build failures:**
```bash
# Try with verbose output
./build_engine.sh build --platform mac --config ci/mac_debug_arm64 --verbose

# Check logs
tail -100 build.log
```

See **BUILD_LOCALLY.md** for detailed troubleshooting.

## Advanced Features

### Framework Creation

After building framework engine variants:

```python
from build_utils import FrameworkBuilder
from pathlib import Path

builder = FrameworkBuilder(Path("flock/engine/src"))
builder.create_macos_debug_framework()
builder.create_ios_framework("debug")
```

### Artifact Tracking

Automatically track all builds:

```python
from build_utils import ArtifactManager

manager = ArtifactManager()
manager.print_summary()  # Show all builds
manager.cleanup_old_artifacts(keep_count=3)  # Keep only 3 newest
```

### Build Caching

Cache builds for faster access:

```python
from build_utils import BuildCache
from pathlib import Path

cache = BuildCache()
if cache.get_cached_build("ci/mac_debug_arm64"):
    cache.restore_build_from_cache("ci/mac_debug_arm64", Path("output"))
```

## Workflow Equivalence

### GitHub Actions → Local Build Equivalence

| GitHub Action | Local Command |
|---------------|---------------|
| `assemble-flock` | Already present in workspace |
| `build-and-upload-engine` | `./build_engine.sh build --platform [os] --config [name]` |
| `create_macos_framework.py` | `build_utils.py` framework functions |
| `create_ios_framework.py` | `build_utils.py` framework functions |
| Matrix builds | `./build_engine.sh build --platform [os] --all` |

## Key Differences from GitHub Actions

1. **No automatic uploads** - Artifacts stay on your machine
2. **No matrix parallelization** - Builds run sequentially by default
3. **Manual platform selection** - Choose target platform explicitly
4. **Direct Xcode integration** - Uses your locally installed Xcode
5. **Full build history** - Local caching and metadata tracking
6. **Real-time monitoring** - Watch builds progress with `build_utilities.sh watch`

## Development & Contributing

The build system is modular and extensible:

- **`build_engine_local.py`** - Add new platforms or configurations
- **`build_utils.py`** - Extend with new build utilities
- **Shell scripts** - Modify shell interface as needed

## Getting Help

### Documentation
- Quick answers: **QUICK_START.md**
- Detailed info: **BUILD_LOCALLY.md**
- Code help: `./build_engine.sh help`

### Commands
```bash
./build_engine.sh help        # Main help
./build_engine.sh list        # See all builds
./build_engine.sh --verbose   # Debug output
```

### Common Issues
- See **BUILD_LOCALLY.md** Troubleshooting section
- Run `./build_utilities.sh status` to diagnose issues
- Use `--verbose` flag for detailed output

## Next Steps

1. ✅ **Setup** - Run `./build_engine.sh setup --depot-tools`
2. ✅ **Verify** - Run `./build_engine.sh check --xcode`
3. ✅ **Build** - Try `./build_engine.sh build --platform mac --config ci/mac_debug_arm64`
4. ✅ **Monitor** - Use `./build_utilities.sh status`
5. ✅ **Iterate** - Build different configurations as needed

---

**Created**: November 17, 2025  
**System**: macOS with zsh shell  
**Python Version**: 3.8+  
**License**: Same as nest-graphite project

For more information, visit: https://github.com/mimbrown/nest-graphite
