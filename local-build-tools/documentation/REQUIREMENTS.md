# Local Build System Requirements

## System Requirements

### macOS
- **Minimum**: macOS 10.15 (Catalina)
- **Recommended**: macOS 12.0+ (Monterey or later)

### Hardware
- **CPU**: 4+ cores (8+ cores highly recommended)
- **RAM**: 8GB minimum, 16GB+ recommended
- **Disk**: 50GB+ free space (SSD highly recommended)
- **Build Time**: 15 minutes to 4 hours depending on configuration

## Software Dependencies

### Required
1. **Python 3.8+**
   - Check: `python3 --version`
   - Install: `brew install python3` or https://www.python.org/downloads/

2. **Xcode 16.4+**
   - Check: `xcodebuild -version`
   - Install: `xcode-select --install` or App Store

3. **Git 2.0+**
   - Check: `git --version`
   - Usually included with Xcode

4. **depot_tools**
   - Automatically installed by: `./build_engine.sh setup --depot-tools`
   - Contains: gclient, gn, ninja

### Optional (for specific features)
- **gcloud CLI** (for uploading to Google Cloud Storage)
- **Docker** (if building in containers)

## Installation Steps

### 1. Verify/Install Python 3

```bash
# Check if Python 3 is installed
python3 --version

# If not found, install via Homebrew
brew install python3

# Or download from https://www.python.org/downloads/
```

### 2. Verify/Install Xcode

```bash
# Check Xcode installation
xcode-select --print-path

# Install Xcode Command Line Tools
xcode-select --install

# Or install full Xcode from App Store/Developer portal
# Download: https://developer.apple.com/download/all/
```

### 3. Verify Git

```bash
# Git should be included with Xcode
git --version

# If not, install via Homebrew
brew install git
```

### 4. Setup depot_tools

```bash
# One-time setup
cd /path/to/nest-graphite
./build_engine.sh setup --depot-tools

# Add to your shell profile (~/.zshrc, ~/.bash_profile, or ~/.bashrc)
export PATH="$HOME/depot_tools:$PATH"

# Reload shell
source ~/.zshrc  # or source ~/.bash_profile
```

## Verification Checklist

```bash
# ✓ Python 3
python3 --version
# Expected: Python 3.8+

# ✓ Xcode
xcodebuild -version
# Expected: Xcode 16.4+

# ✓ Git
git --version
# Expected: git version 2.0+

# ✓ Command Line Tools
xcode-select --print-path
# Expected: /Applications/Xcode.app/Contents/Developer (or similar)

# ✓ Build scripts are executable
ls -l build_engine.sh build_utilities.sh
# Expected: -rwxr-xr-x (executable)

# ✓ depot_tools in PATH (after setup)
which gclient
# Expected: /Users/[username]/depot_tools/gclient
```

## Troubleshooting Installation

### Python 3 Not Found

**Issue**: `command not found: python3`

**Solution 1: Homebrew**
```bash
brew install python3
# Then verify
python3 --version
```

**Solution 2: Direct Download**
```bash
# Download and install from https://www.python.org/downloads/
# Then verify
python3 --version
```

### Xcode Issues

**Issue**: `xcode-select: error: command line tools not found`

**Solution**:
```bash
# Install Command Line Tools
xcode-select --install

# Or set path to existing Xcode
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

**Issue**: Xcode version too old

**Solution**:
```bash
# Check current version
xcodebuild -version

# Update Xcode from App Store or Developer website
# Minimum required: Xcode 16.4
```

### depot_tools Issues

**Issue**: `command not found: gclient`

**Solution**:
```bash
# Re-run setup
./build_engine.sh setup --depot-tools

# Verify PATH includes depot_tools
echo $PATH | grep depot_tools

# Add to ~/.zshrc if not present
echo 'export PATH="$HOME/depot_tools:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Disk Space Requirements

### Per Configuration
- **Debug build**: 1-3 GB
- **Profile build**: 2-5 GB
- **Release build**: 3-8 GB
- **With dsym (symbols)**: +2-3 GB

### Total Recommendations
- **Single build**: 5 GB free
- **Multiple builds**: 20-30 GB free
- **Full macOS suite**: 50 GB+ free

### Check Available Space

```bash
# Show disk usage
df -h

# Show directory sizes
du -sh flock/engine/src/out/
```

## Memory Requirements

### During Builds
- **Minimum**: 4 GB available RAM
- **Recommended**: 8-16 GB available RAM
- **For parallel builds**: 16 GB+ RAM

### Monitor During Build

```bash
# Watch memory usage in real-time
while true; do
  clear
  date
  ps aux | head -n 1
  ps aux | grep -E "ninja|clang|ld|et" | head -10
  sleep 5
done
```

## Network Requirements

### For Initial Setup
- depot_tools download: ~500 MB
- Engine source code: ~3-5 GB (first sync)

### For Development
- Generally none required after initial setup
- Optional: gcloud for artifact uploads

### Bandwidth Considerations

Initial setup requires:
- **depot_tools**: 500 MB (~5 min on typical connection)
- **Engine source**: 3-5 GB (~30-60 min on typical connection)

## Environment Setup

### Shell Configuration

Add to `~/.zshrc` or `~/.bash_profile`:

```bash
# Flutter Engine Build Environment
export DEPOT_TOOLS_WIN_TOOLCHAIN=0
export PATH="$HOME/depot_tools:$PATH"
export FLUTTER_BRANCH=stable
```

### Optional Variables

```bash
# Set custom build directory
export BUILD_DIR="/path/to/build"

# Enable verbose output
export VERBOSE=1

# Set parallel jobs (default: auto-detected)
export NINJA_PARALLEL_JOBS=4
```

## IDE/Editor Support

### VS Code
- Recommended extensions:
  - Python (by Microsoft)
  - Bash IDE (mads-hartmann.bash-ide-vscode)
  - Shell Format (foxundermoon.shell-format)

### Python IDE
- PyCharm Community Edition
- Recommended for `build_engine_local.py` development

### Text Editors
- Any text editor with bash/python syntax highlighting
- Vim, Emacs, Sublime Text all supported

## CI/CD Considerations

If running builds in CI/CD:

### GitHub Actions
- Use pre-installed tools
- Larger hardware available (ubuntu-latest has ~8 cores)

### Local CI/CD (Jenkins, GitLab)
- Ensure hardware meets requirements above
- Set appropriate environment variables
- Increase disk space allocation

### Docker

```dockerfile
FROM python:3.10-bullseye

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl

# Setup build environment
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git /opt/depot_tools
ENV PATH="/opt/depot_tools:$PATH"

# Copy build scripts
COPY build_engine_local.py /app/
COPY build_utils.py /app/

WORKDIR /app
```

## Version Compatibility

### Python
- **3.8**: Supported
- **3.9**: Supported
- **3.10**: Supported  ✓ (Recommended)
- **3.11+**: Supported

### Xcode
- **16.4**: Minimum (Required)
- **16.5+**: Fully supported

### macOS
- **10.15**: Minimum (Catalina)
- **11.0+**: Fully supported
- **14.0+**: Recommended (Sonoma)

## Performance Tuning

### Faster Builds

1. **Use SSD**: Builds are I/O intensive
2. **Close other apps**: Free up RAM
3. **Use ccache**: C++ compiler cache
4. **Enable parallel builds**: Set `NINJA_PARALLEL_JOBS`

### Install ccache (Optional)

```bash
brew install ccache

# Enable in build
export CC="ccache clang"
export CXX="ccache clang++"
```

## Support & Issues

For setup issues:

1. Check this document first
2. Review **BUILD_LOCALLY.md** troubleshooting
3. Run verification checklist above
4. Check with `./build_engine.sh --verbose`

## Next Steps

After verifying all requirements:

1. ✓ Run `./build_engine.sh setup --depot-tools`
2. ✓ Add `export PATH="$HOME/depot_tools:$PATH"` to shell profile
3. ✓ Reload shell: `source ~/.zshrc`
4. ✓ Run `./build_engine.sh check --xcode`
5. ✓ Start with `./build_engine.sh list`

---

**Last Updated**: November 17, 2025  
**For**: nest-graphite local builds  
**Platform**: macOS  
**Shell**: zsh/bash
