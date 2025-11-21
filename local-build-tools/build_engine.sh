#!/bin/bash

# Local Flutter Engine Builder - Bash Wrapper
# Provides convenient command-line interface for building Flutter engines locally on macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/build_engine_local.py"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print usage information
usage() {
    cat << EOF
${BLUE}Local Flutter Engine Builder${NC}

USAGE:
    $(basename "$0") [COMMAND] [OPTIONS]

COMMANDS:
    list                List all available build configurations
    build               Build engine(s)
    framework           Build all framework(s) without building engine configurations
    check               Check Xcode and dependencies
    setup               Setup required tools
    help                Show this help message

OPTIONS for 'build' command:
    --platform PLATFORM     Target platform: mac, ios, android, androidlinux, linux, web
    --config CONFIG         Specific configuration to build
    --all                   Build all configurations for the platform
    --framework             Build frameworks after building configurations
    --verbose, -v           Enable verbose output

OPTIONS for 'check' command:
    --xcode                 Check Xcode version and setup
    
OPTIONS for 'setup' command:
    --depot-tools           Setup depot_tools

EXAMPLES:
    # List available configurations
    $(basename "$0") list
    
    # Build specific macOS configuration
    $(basename "$0") build --platform mac --config ci/mac_debug_arm64
    
    # Build all macOS configurations
    $(basename "$0") build --platform mac --all
    
    # Build iOS debug
    $(basename "$0") build --platform ios --config ci/ios_debug

    # Build specific iOS framework
    $(basename "$0") framework --platform ios

    # Build frameworks for all available platforms
    $(basename "$0") framework
    
    # Check Xcode setup
    $(basename "$0") check --xcode
    
    # Setup depot_tools
    $(basename "$0") setup --depot-tools

EOF
}

# Print info message
info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

# Print success message
success() {
    echo -e "${GREEN}✓${NC} $*"
}

# Print warning message
warn() {
    echo -e "${YELLOW}⚠${NC} $*"
}

# Print error message
error() {
    echo -e "${RED}✗${NC} $*" >&2
}

# Main command routing
COMMAND="${1:-help}"

case "$COMMAND" in
    list)
        info "Listing available build configurations..."
        python3 "$PYTHON_SCRIPT" --list
        ;;
    
    build)
        shift
        info "Starting build process..."
        python3 "$PYTHON_SCRIPT" "$@"
        ;;

    framework)
        info "Starting framework build..."
        python3 "$PYTHON_SCRIPT" --framework
        ;;
    
    check)
        shift
        if [[ "$1" == "--xcode" ]]; then
            info "Checking Xcode setup..."
            python3 "$PYTHON_SCRIPT" --check-xcode
        else
            error "Unknown check option: $1"
            usage
            exit 1
        fi
        ;;
    
    setup)
        shift
        if [[ "$1" == "--depot-tools" ]]; then
            info "Setting up depot_tools..."
            python3 "$PYTHON_SCRIPT" --setup-depot-tools
            success "depot_tools setup complete"
            info "Add this to your shell profile to use gclient and depot_tools:"
            echo "  export PATH=\"\$HOME/depot_tools:\$PATH\""
        else
            error "Unknown setup option: $1"
            usage
            exit 1
        fi
        ;;
    
    help|--help|-h)
        usage
        ;;
    
    *)
        error "Unknown command: $COMMAND"
        usage
        exit 1
        ;;
esac

exit $?
