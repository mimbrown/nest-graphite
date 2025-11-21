# Build System Index & File Guide

Complete guide to the local Flutter Engine build system for macOS.

## 📂 Files Created

### Core Build Scripts

| File | Purpose | Type | Executable |
|------|---------|------|-----------|
| `build_engine.sh` | Main command-line interface | Bash | ✓ |
| `build_engine_local.py` | Core build engine | Python | ✗ |
| `build_utilities.sh` | Build management utilities | Bash | ✓ |
| `build_utils.py` | Advanced build helpers | Python | ✗ |

### Documentation

| File | Purpose | Audience | Length |
|------|---------|----------|--------|
| `QUICK_START.md` | Fast reference & setup | Everyone | Short (5 min) |
| `BUILD_LOCALLY.md` | Complete guide & reference | Developers | Long (30 min) |
| `REQUIREMENTS.md` | System requirements & setup | Installers | Medium (15 min) |
| `README_LOCAL_BUILDS.md` | System overview | Developers | Long (20 min) |
| `BUILD_SYSTEM_INDEX.md` | This file | Everyone | Short (5 min) |

---

## 🚀 Quick Navigation

### Just Want to Build?
→ Start with **QUICK_START.md**

### Need Complete Documentation?
→ Read **BUILD_LOCALLY.md**

### Have System Issues?
→ Check **REQUIREMENTS.md**

### Want Deep Understanding?
→ Study **README_LOCAL_BUILDS.md**

### Need Help with Commands?
→ Run `./build_engine.sh help`

---

## 📋 Common Tasks

### Setup (One-Time)
```bash
# 1. Make scripts executable
chmod +x build_engine.sh build_utilities.sh

# 2. Setup depot_tools
./build_engine.sh setup --depot-tools

# 3. Add to shell profile (~/.zshrc or ~/.bash_profile)
export PATH="$HOME/depot_tools:$PATH"
```

### Build Engine
```bash
# List available builds
./build_engine.sh list

# Build macOS debug (fastest, good for testing)
./build_engine.sh build --platform mac --config ci/mac_debug_arm64

# Build iOS debug
./build_engine.sh build --platform ios --config ci/ios_debug

# Build all macOS configs (takes 2-4 hours)
./build_engine.sh build --platform mac --all
```

### Monitor & Manage Builds
```bash
# Show build status
./build_utilities.sh status

# List completed builds
./build_utilities.sh list-builds

# Monitor build in real-time
./build_utilities.sh watch ci/mac_debug_arm64

# Compare builds
./build_utilities.sh compare

# Clean old builds
./build_utilities.sh clean
```

---

## 🔧 Scripts Overview

### build_engine.sh
**Purpose**: Main command-line interface  
**Type**: Bash wrapper  
**Usage**: `./build_engine.sh [COMMAND] [OPTIONS]`

**Commands**:
- `list` - Show all available configurations
- `build` - Build engines (requires --platform and --config or --all)
- `check` - Check system setup (--xcode)
- `setup` - Setup required tools (--depot-tools)
- `help` - Show help message

**Examples**:
```bash
./build_engine.sh list
./build_engine.sh build --platform mac --config ci/mac_debug_arm64
./build_engine.sh build --platform ios --all --verbose
./build_engine.sh check --xcode
```

---

### build_engine_local.py
**Purpose**: Core build orchestration engine  
**Type**: Python 3 application  
**Usage**: `python3 build_engine_local.py [OPTIONS]`

**Classes**:
- `FlutterEngineBuilder` - Main builder class
- `BuildConfig` - Configuration representation
- `Platform` - Platform enumeration

**Features**:
- 50+ pre-configured build targets
- Multi-platform support (macOS, iOS, Android, Linux, Web)
- Detailed logging and error handling
- Framework creation helpers
- JSON export of results

**Examples**:
```python
from build_engine_local import FlutterEngineBuilder

builder = FlutterEngineBuilder(verbose=True)
builder.build_mac_engine("ci/mac_debug_arm64")
builder.list_available_configs()
```

---

### build_utilities.sh
**Purpose**: Build artifact management and monitoring  
**Type**: Bash utility script  
**Usage**: `./build_utilities.sh [COMMAND]`

**Commands**:
- `status` - Show current build status
- `list-builds` - List all completed builds
- `list-outputs` - Show output directory for config
- `watch` - Monitor a build in real-time
- `compare` - Compare builds by size/date
- `clean` - Remove build artifacts
- `clean-all` - Remove all builds + cache

**Features**:
- Real-time build monitoring
- File counting and size analysis
- Build comparison tools
- Artifact cleanup and management

---

### build_utils.py
**Purpose**: Advanced build utilities and helpers  
**Type**: Python library  
**Import**: `from build_utils import ...`

**Classes**:
- `FrameworkBuilder` - Create macOS/iOS frameworks
- `ArtifactManager` - Track build metadata
- `BuildCache` - Cache builds for fast access
- `BuildArtifact` - Artifact data structure

**Usage Examples**:
```python
from build_utils import FrameworkBuilder, ArtifactManager
from pathlib import Path

# Create frameworks
builder = FrameworkBuilder(Path("flock/engine/src"))
builder.create_macos_debug_framework()

# Manage artifacts
manager = ArtifactManager()
manager.print_summary()
manager.cleanup_old_artifacts(keep_count=3)
```

---

## 📚 Documentation Guide

### QUICK_START.md ⚡
- **Read time**: 5 minutes
- **Audience**: Everyone
- **Contains**:
  - One-time setup steps
  - Most common commands
  - Build time estimates
  - Quick troubleshooting

### BUILD_LOCALLY.md 📖
- **Read time**: 30 minutes
- **Audience**: Developers building locally
- **Contains**:
  - Complete setup guide
  - All available configurations
  - Platform-specific details
  - Build output locations
  - Troubleshooting section
  - Performance tips

### REQUIREMENTS.md 🔧
- **Read time**: 15 minutes
- **Audience**: System administrators
- **Contains**:
  - System requirements
  - Installation steps
  - Verification checklist
  - Troubleshooting
  - Hardware recommendations
  - Version compatibility

### README_LOCAL_BUILDS.md 📄
- **Read time**: 20 minutes
- **Audience**: Developers (overview)
- **Contains**:
  - System overview
  - File structure
  - Platform support
  - Build configurations
  - Python usage examples
  - Advanced features

---

## 🎯 Supported Platforms & Configurations

### macOS (21 configs)
- Device builds (arm64)
- Host builds (native arch)
- Framework builds
- Debug, profile, release variants

### iOS (11 configs)
- Device and simulator builds
- arm64, x64 variants
- Debug, profile, release
- Extension-safe variants

### Android (9 configs on macOS)
- arm64, x64, x86 architectures
- Debug, profile, release modes

### Linux & Web
- Configurations defined but not fully implemented for local builds
- Would require Linux-specific toolchain

---

## 📊 Build Configuration Examples

```
macOS:
  ci/mac_debug_arm64
  ci/mac_profile_arm64
  ci/mac_release_arm64
  ci/host_debug
  ci/host_debug_framework
  ci/host_profile
  ci/host_release
  ...

iOS:
  ci/ios_debug
  ci/ios_debug_sim
  ci/ios_debug_sim_arm64
  ci/ios_profile
  ci/ios_release
  ...

Android (macOS):
  android_debug_arm64
  android_debug_unopt
  ci/android_profile
  ci/android_release
  ...
```

See `./build_engine.sh list` for complete list.

---

## 🏗️ Build Output Structure

```
flock/engine/src/out/
├── ci/
│   ├── mac_debug_arm64/
│   │   ├── obj/
│   │   ├── exe/
│   │   └── gen/
│   ├── ios_debug/
│   ├── android_release/
│   └── ...
└── [other configs]/
```

---

## ⏱️ Typical Build Times

| Configuration | Time | Notes |
|---------------|------|-------|
| macOS debug | 15-30 min | Fast, minimal optimization |
| iOS debug | 20-40 min | Device build |
| Android debug | 25-45 min | Multiple architectures |
| macOS release | 45-60 min | Full optimization |
| All macOS | 2-4 hours | Sequential |

Varies by: CPU cores, RAM, disk speed, cache state

---

## �� Workflow

```
1. Setup (one-time)
   └─ ./build_engine.sh setup --depot-tools
   └─ Add PATH to shell profile

2. Choose Platform
   └─ mac, ios, android, linux, web

3. Choose Configuration
   └─ ./build_engine.sh list
   └─ Pick config or use --all

4. Build
   └─ ./build_engine.sh build --platform [X] --config [Y]

5. Monitor (optional)
   └─ ./build_utilities.sh watch [config]

6. Verify
   └─ ./build_utilities.sh status

7. Use Output
   └─ flock/engine/src/out/[config]/
```

---

## 🆘 Troubleshooting Quick Links

| Issue | File | Section |
|-------|------|---------|
| Setup errors | REQUIREMENTS.md | Installation Steps |
| Build failures | BUILD_LOCALLY.md | Troubleshooting |
| Command not working | build_engine.sh | help |
| Missing depot_tools | QUICK_START.md | Installation |
| Xcode issues | REQUIREMENTS.md | Xcode Issues |
| Slow builds | BUILD_LOCALLY.md | Performance Tips |

---

## 🚦 Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Xcode 16.4+ installed
- [ ] Git installed
- [ ] Workspace checked out
- [ ] Scripts are executable
- [ ] depot_tools setup complete
- [ ] PATH environment variable updated
- [ ] Shell profile reloaded

---

## 📞 Getting Help

### For Immediate Answers
```bash
./build_engine.sh help
./build_utilities.sh help
python3 build_engine_local.py --help
```

### For Common Issues
See **REQUIREMENTS.md** troubleshooting section

### For Detailed Guidance
Read **BUILD_LOCALLY.md**

### For Quick Reference
See **QUICK_START.md**

---

## 🎓 Learning Path

1. **Start**: Read **QUICK_START.md** (5 min)
2. **Setup**: Follow installation steps (5 min)
3. **Try**: Build first config with `./build_engine.sh build --platform mac --config ci/mac_debug_arm64` (30+ min)
4. **Explore**: List all builds with `./build_engine.sh list` (1 min)
5. **Learn**: Read **BUILD_LOCALLY.md** for details (30 min)
6. **Master**: Explore Python files and advanced utilities (varies)

---

## 📝 File Summary

| File | Lines | Purpose | Edit Frequently? |
|------|-------|---------|-----------------|
| `build_engine.sh` | 130 | Command wrapper | Never |
| `build_engine_local.py` | 550 | Main builder | For new platforms |
| `build_utilities.sh` | 210 | Management | Never |
| `build_utils.py` | 400 | Utilities | For new features |
| `QUICK_START.md` | 100 | Reference | When adding commands |
| `BUILD_LOCALLY.md` | 300 | Full guide | When changing system |
| `REQUIREMENTS.md` | 250 | Setup help | When deps change |
| `README_LOCAL_BUILDS.md` | 400 | Overview | For updates |

---

## 🔐 Security Notes

- Scripts do NOT upload to cloud (local only)
- NO credentials stored in scripts
- Builds are isolated to workspace
- Safe to share scripts publicly

---

## 🎯 Next Steps

1. **New users**: Start with **QUICK_START.md**
2. **Have issues**: Check **REQUIREMENTS.md**
3. **Want details**: Read **BUILD_LOCALLY.md**
4. **Understanding system**: Review **README_LOCAL_BUILDS.md**

---

**Created**: November 17, 2025  
**System**: macOS with zsh shell  
**Status**: Ready to use ✓

Get started: `./build_engine.sh help`
