# Quick Start: Local Flutter Engine Builds

## Installation (One-Time)

```bash
cd nest-graphite

# Make build script executable
chmod +x build_engine.sh

# Setup depot_tools
./build_engine.sh setup --depot-tools

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
export PATH="$HOME/depot_tools:$PATH"
```

## Most Common Commands

### See all available builds
```bash
./build_engine.sh list
```

### Build macOS debug (recommended starting point)
```bash
./build_engine.sh build --platform mac --config ci/mac_debug_arm64
```

### Build iOS debug
```bash
./build_engine.sh build --platform ios --config ci/ios_debug
```

### Build all macOS configs (takes 2-4 hours)
```bash
./build_engine.sh build --platform mac --all
```

### Check your setup
```bash
./build_engine.sh check --xcode
```

## Build Locations

After building, find outputs in:
```
flock/engine/src/out/[config_name]/
```

Examples:
- `flock/engine/src/out/ci/mac_debug_arm64/` - macOS ARM64 debug
- `flock/engine/src/out/ci/ios_debug/` - iOS device debug
- `flock/engine/src/out/ci/ios_debug_sim_arm64/` - iOS Simulator (Apple Silicon)

## Advanced Options

### Verbose output (see all build details)
```bash
./build_engine.sh build --platform mac --config ci/mac_debug_arm64 --verbose
```

### Use Python directly
```bash
python3 build_engine_local.py --platform mac --all
```

### Custom workspace path
```bash
./build_engine.sh build --workspace /path/to/workspace --platform ios --config ci/ios_debug
```

## What Gets Built

### macOS Builds (21 configs)
- Device builds (arm64)
- Host builds (native architecture)
- Framework builds (for embedding)
- Release builds (optimized)

### iOS Builds (11 configs)
- Device builds
- Simulator builds (x64, arm64)
- Extension-safe variants
- All optimization levels

### Android (macOS runner) (9 configs)
- Debug, profile, release
- Various architectures (arm64, x64, x86)

## Typical Build Times

| Config | Time | Notes |
|--------|------|-------|
| debug | 15-30 min | Fast, unoptimized |
| profile | 30-45 min | Medium optimization |
| release | 45-60 min | Full optimization |
| All macOS | 2-4 hours | Sequential builds |

Times vary based on:
- System CPU cores and RAM
- First build (no cache)
- Disk speed (SSD recommended)

## Troubleshooting

**"Command not found: depot_tools"**
→ Run `export PATH="$HOME/depot_tools:$PATH"` or add to shell profile

**"Xcode version too old"**
→ Update Xcode: `xcode-select --install`

**"flock directory not found"**
→ Make sure you're in nest-graphite root: `cd nest-graphite && ls flock`

**Build very slow or fails with out-of-memory**
→ Close other apps, try building one config at a time

**"Python 3 not found"**
→ Install from https://www.python.org/downloads/ or `brew install python3`

## Next Steps

1. **Try a debug build** - Fastest way to test:
   ```bash
   ./build_engine.sh build --platform mac --config ci/mac_debug_arm64
   ```

2. **Check build output** - Verify successful build:
   ```bash
   ls -lah flock/engine/src/out/ci/mac_debug_arm64/
   ```

3. **Create frameworks** - If needed, see BUILD_LOCALLY.md

4. **Use your engine** - Point Flutter to custom engine or iterate

For detailed documentation, see **BUILD_LOCALLY.md**
