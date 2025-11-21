#!/bin/bash

# Flutter Engine Build Utilities
# Helper commands for common build tasks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_SRC="${SCRIPT_DIR}/flock/engine/src"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ${NC} $*"; }
success() { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
error() { echo -e "${RED}✗${NC} $*" >&2; }

usage() {
    cat << EOF
${BLUE}Flutter Engine Build Utilities${NC}

USAGE:
    $(basename "$0") [COMMAND] [OPTIONS]

COMMANDS:
    status              Show build status and available artifacts
    clean               Remove build artifacts
    clean-all           Remove all builds and cache
    list-builds         List all completed builds with timestamps
    list-outputs        Show output directory for a config
    watch               Monitor a build in progress
    watch-all           Monitor all builds (continuous list-builds)
    compare             Compare build timestamps/sizes
    help                Show this help message

EXAMPLES:
    # Check what builds are available
    $(basename "$0") status
    
    # List all completed builds
    $(basename "$0") list-builds
    
    # See output location for specific build
    $(basename "$0") list-outputs ci/mac_debug_arm64
    
    # Remove all build artifacts
    $(basename "$0") clean-all

EOF
}

# Show build status
status() {
    if [ ! -d "$ENGINE_SRC" ]; then
        error "Engine source not found at $ENGINE_SRC"
        exit 1
    fi
    
    info "Build Status Report"
    info "Engine source: $ENGINE_SRC"
    
    if [ ! -d "$ENGINE_SRC/out" ] && [ ! -d "$ENGINE_SRC/out/ci" ]; then
        warn "No builds found yet"
        return
    fi
    
    echo ""
    info "Available builds:"
    echo ""
    
    local total=0
    local size_total=0
    
    for build_dir in "$ENGINE_SRC"/out/*/; do
        if [ -d "$build_dir" ]  && [ "$build_dir" != "$ENGINE_SRC/out/ci/" ]; then
            local config_name=$(basename "$build_dir")
            local size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
            local timestamp=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$build_dir" 2>/dev/null || echo "unknown")
            
            printf "  %-40s %8s  %s\n" "$config_name" "$size" "$timestamp"
            
            ((total++))
        fi
    done
    
    for build_dir in "$ENGINE_SRC"/out/ci/*/; do
        if [ -d "$build_dir" ]; then
            local config_name=$(basename "$build_dir")
            local size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
            local timestamp=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$build_dir" 2>/dev/null || echo "unknown")
            
            printf "  %-40s %8s  %s\n" "ci/$config_name" "$size" "$timestamp"
            
            ((total++))
        fi
    done
    
    echo ""
    if [ $total -eq 0 ]; then
        warn "No builds found"
    else
        success "Found $total build(s)"
    fi
    echo ""
}

# Clean build artifacts
clean() {
    if [ ! -d "$ENGINE_SRC/out" ]; then
        warn "No builds to clean"
        return
    fi
    
    read -p "Remove all build artifacts? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Cleaning build artifacts..."
        rm -rf "$ENGINE_SRC/out"
        success "Cleaned successfully"
    else
        warn "Cleanup cancelled"
    fi
}

# Clean everything including cache
clean_all() {
    read -p "Remove ALL builds, cache, and metadata? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Cleaning all artifacts..."
        
        [ -d "$ENGINE_SRC/out" ] && rm -rf "$ENGINE_SRC/out"
        [ -d "$SCRIPT_DIR/.build_artifacts" ] && rm -rf "$SCRIPT_DIR/.build_artifacts"
        [ -d "$SCRIPT_DIR/.build_cache" ] && rm -rf "$SCRIPT_DIR/.build_cache"
        
        success "Cleaned all artifacts"
    else
        warn "Cleanup cancelled"
    fi
}

# List builds with details
list_builds() {
    if [ ! -d "$ENGINE_SRC/out" ] && [ ! -d "$ENGINE_SRC/out/ci" ]; then
        warn "No builds found"
        return
    fi
    
    echo ""
    info "Completed builds:"
    echo ""
    printf "%-44s | %-8s | %-19s | Files | Key Files\n" "Configuration" "Size" "Modified"
    echo "$(printf '%0.s-' {1..97})"
    
    for build_dir in "$ENGINE_SRC"/out/*/; do
        if [ -d "$build_dir" ]  && [ "$build_dir" != "$ENGINE_SRC/out/ci/" ]; then
            local config=$(basename "$build_dir")
            local size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
            local timestamp=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$build_dir" 2>/dev/null || echo "unknown")
            local file_count=$(find "$build_dir" -type f 2>/dev/null | wc -l)
            local key_files=$([[ $(find "$build_dir" -maxdepth 2 \( -name "*.framework" -o -name "*.zip" -o -name "gen_snapshot*" \) 2>/dev/null | wc -l) -eq 0 ]] && echo "false" || echo "true")
            
            printf "%-44s | %8s | %19s | %5d | %9s\n" "$config" "$size" "$timestamp" "$file_count" "$key_files"
        fi
    done
    
    for build_dir in "$ENGINE_SRC"/out/ci/*/; do
        if [ -d "$build_dir" ]; then
            local config=$(basename "$build_dir")
            local size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
            local timestamp=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$build_dir" 2>/dev/null || echo "unknown")
            local file_count=$(find "$build_dir" -type f 2>/dev/null | wc -l)
            local key_files=$([[ $(find "$build_dir" -maxdepth 2 \( -name "*.framework" -o -name "*.zip" -o -name "gen_snapshot*" \) 2>/dev/null | wc -l) -eq 0 ]] && echo "false" || echo "true")
            
            printf "%-44s | %8s | %19s | %5d | %9s\n" "ci/$config" "$size" "$timestamp" "$file_count" "$key_files"
            
            ((total++))
        fi
    done
    echo ""
    
    #info "Pending builds:"
    #echo ""
    #source ./build_engine_local.sh
}

# Show output directory for config
list_outputs() {
    if [ -z "$1" ]; then
        error "Please specify a config name"
        echo "Example: $(basename "$0") list-outputs ci/mac_debug_arm64"
        exit 1
    fi
    
    local config="$1"
    local output_dir="$ENGINE_SRC/out/$config"
    
    if [ ! -d "$output_dir" ]; then
        error "Build not found: $output_dir"
        exit 1
    fi
    
    info "Output directory: $output_dir"
    echo ""
    
    du -sh "$output_dir"/* 2>/dev/null | sort -rh | head -20
    
    echo ""
    info "Key files:"
    find "$output_dir" -maxdepth 2 \( -name "*.framework" -o -name "*.zip" -o -name "gen_snapshot*" \) 2>/dev/null | sed 's|^|  |'
    echo ""
}

# Watch a build directory
watch() {
    if [ -z "$1" ]; then
        error "Please specify a config name to watch"
        exit 1
    fi
    
    local config="$1"
    local output_dir="$ENGINE_SRC/out/$config"
    
    if [ ! -d "$output_dir" ]; then
        info "Waiting for build: $config"
        info "Checking every 5 seconds..."
        
        while [ ! -d "$output_dir" ]; do
            sleep 5
        done
        
        success "Build started!"
    fi
    
    info "Monitoring build: $config"
    info "Press Ctrl+C to stop"
    echo ""
    
    while true; do
        clear
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Monitoring: $config"
        echo "---"
        
        # Show size growth
        local size=$(du -sh "$output_dir" 2>/dev/null | cut -f1)
        local file_count=$(find "$output_dir" -type f 2>/dev/null | wc -l)
        
        echo "Current size: $size"
        echo "File count: $file_count"
        echo ""
        
        # Show recent files
        echo "Recently modified files:"
        find "$output_dir" -type f -mmin -5 2>/dev/null | head -5 | sed 's|^|  |'
        
        echo ""
        echo "(updating every 5 seconds...)"
        sleep 5
    done
}

# Watch all builds (continuous list-builds)
watch-all() {

    local output_dir="$ENGINE_SRC/out/"
    
    if [ ! -d "$output_dir" ]; then
        info "Waiting for build: $config"
        info "Checking every 5 seconds..."
        
        while [ ! -d "$output_dir" ]; do
            sleep 5
        done
        
        success "Build started!"
    fi
    
    info "Monitoring build: $config"
    info "Press Ctrl+C to stop"
    echo ""
    
    while true; do
        clear
        list_builds
        
        echo ""
        echo "(updating every 10 seconds...)"
        sleep 10
    done
}

# Compare builds
compare() {
    if [ ! -d "$ENGINE_SRC/out" ]; then
        error "No builds found"
        exit 1
    fi
    
    echo ""
    info "Build Comparison"
    echo ""
    printf "%-40s | %-10s | %-19s\n" "Configuration" "Size" "Modified"
    echo "$(printf '%0.s-' {1..75})"
    
    local configs=($(ls -1d "$ENGINE_SRC"/out/*/ 2>/dev/null | xargs -I {} basename {}))
    
    for config in "${configs[@]}"; do
        local build_dir="$ENGINE_SRC/out/$config"
        local size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
        local timestamp=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$build_dir" 2>/dev/null || echo "unknown")
        
        printf "%-40s | %10s | %19s\n" "$config" "$size" "$timestamp"
    done
    
    echo ""
}

# Main
case "${1:-help}" in
    status)
        status
        ;;
    clean)
        clean
        ;;
    clean-all)
        clean_all
        ;;
    list-builds)
        list_builds
        ;;
    list-outputs)
        list_outputs "$2"
        ;;
    watch)
        watch "$2"
        ;;
    watch-all)
        watch-all
        ;;
    compare)
        compare
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: $1"
        usage
        exit 1
        ;;
esac

exit $?
