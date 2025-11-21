# Web Build Quick Reference

## Web Platform Now Available! 🎉

The local Flutter Engine build system now supports native macOS builds for Web/WASM targets.

## Available Web Configurations

```
WEB BUILDS (2):
  1. web wasm debug unopt     (wasm_debug_unopt)
  2. web wasm release         (wasm_release)
```

## Common Commands

### View all available configurations
```bash
./build_engine.sh list
```

### Build a single web configuration
```bash
# Build debug WASM (unoptimized)
./build_engine.sh build --platform web --config wasm_debug_unopt

# Build release WASM
./build_engine.sh build --platform web --config wasm_release
```

### Build all web configurations
```bash
./build_engine.sh build --platform web --all
```

## Build Output

Web builds generate artifacts in:
```
flock/engine/src/out/[config_name]/
  ├── lib/
  ├── gen/
  └── [other build artifacts]
```

## Configuration Details

| Config | Full Name | Type | Purpose |
|--------|-----------|------|---------|
| `wasm_debug_unopt` | web wasm debug unopt | Debug | Development, unoptimized for debugging |
| `wasm_release` | web wasm release | Release | Production, optimized for size/speed |

## Build Platform Support Summary

Your local build system now supports:

| Platform | Configs | Status |
|----------|---------|--------|
| macOS | 21 | ✅ Ready |
| iOS | 11 | ✅ Ready |
| Android | 9 | ✅ Ready |
| Web/WASM | 2 | ✅ **NEW - Ready** |
| Linux | 5 | Future expansion |
| **Total** | **48** | **✅ All local-buildable** |

## Next: Building Your First Web Engine

To build a WASM engine:

```bash
# 1. Check your setup
./build_engine.sh check-setup

# 2. Build debug WASM
./build_engine.sh build --platform web --config wasm_debug_unopt

# 3. Monitor progress (in another terminal)
./build_utilities.sh watch

# 4. Verify output
./build_utilities.sh list-builds
```

## For Full Documentation

See: `BUILD_LOCALLY.md`, `README_LOCAL_BUILDS.md`, and `BUILD_SYSTEM_INDEX.md`

---

**Total Configurations Available Locally: 48 build targets across 4 platforms (macOS, iOS, Android, Web)**
