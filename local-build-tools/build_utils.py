"""
Advanced build utilities for Flutter engine local builds
Provides helpers for framework creation, artifact management, and build operations
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict
import json
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BuildArtifact:
    """Represents a build artifact"""
    config_name: str
    platform: str
    build_type: str  # debug, profile, release
    output_dir: Path
    timestamp: str
    build_duration_seconds: float = 0.0
    size_bytes: int = 0


class FrameworkBuilder:
    """Helper class for creating macOS and iOS frameworks"""
    
    def __init__(self, engine_src_dir: Path, verbose: bool = False):
        """Initialize the framework builder
        
        Args:
            engine_src_dir: Path to Flutter engine source (flock/engine/src)
            verbose: Enable verbose output
        """
        self.engine_src_dir = engine_src_dir
        self.verbose = verbose
    
    def log(self, message: str):
        """Log a message if verbose is enabled"""
        if self.verbose:
            print(f"[Framework] {message}")
    
    def create_macos_debug_framework(self, output_dir: Optional[Path] = None) -> bool:
        """Create macOS debug framework from build artifacts
        
        Args:
            output_dir: Output directory for framework (default: out/debug/framework)
            
        Returns:
            Success status
        """
        if output_dir is None:
            output_dir = self.engine_src_dir / "out" / "debug" / "framework"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                "python3", "flutter/sky/tools/create_macos_framework.py",
                "--dst", str(output_dir),
                "--arm64-out-dir", "out/ci/mac_debug_framework_arm64",
                "--x64-out-dir", "out/ci/host_debug_framework",
                "--zip"
            ]
            
            self.log(f"Creating debug framework: {' '.join(cmd)}")
            subprocess.run(cmd, cwd=self.engine_src_dir, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating macOS debug framework: {e}")
            return False
    
    def create_macos_profile_framework(self, output_dir: Optional[Path] = None) -> bool:
        """Create macOS profile framework"""
        if output_dir is None:
            output_dir = self.engine_src_dir / "out" / "profile" / "framework"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                "python3", "flutter/sky/tools/create_macos_framework.py",
                "--dst", str(output_dir),
                "--arm64-out-dir", "out/ci/mac_profile_framework_arm64",
                "--x64-out-dir", "out/ci/host_profile_framework",
                "--zip"
            ]
            
            self.log(f"Creating profile framework: {' '.join(cmd)}")
            subprocess.run(cmd, cwd=self.engine_src_dir, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating macOS profile framework: {e}")
            return False
    
    def create_macos_release_framework(self, output_dir: Optional[Path] = None) -> bool:
        """Create macOS release framework"""
        if output_dir is None:
            output_dir = self.engine_src_dir / "out" / "release" / "framework"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                "python3", "flutter/sky/tools/create_macos_framework.py",
                "--dst", str(output_dir),
                "--arm64-out-dir", "out/ci/mac_release_framework_arm64",
                "--x64-out-dir", "out/ci/host_release_framework",
                "--dsym",
                "--strip",
                "--zip"
            ]
            
            self.log(f"Creating release framework: {' '.join(cmd)}")
            subprocess.run(cmd, cwd=self.engine_src_dir, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating macOS release framework: {e}")
            return False
    
    def create_ios_framework(self, build_type: str = "debug", 
                           output_dir: Optional[Path] = None) -> bool:
        """Create iOS framework
        
        Args:
            build_type: "debug", "profile", or "release"
            output_dir: Output directory for framework
            
        Returns:
            Success status
        """
        if output_dir is None:
            output_dir = self.engine_src_dir / "out" / build_type / "ios"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                "python3", "flutter/sky/tools/create_ios_framework.py",
                "--dst", str(output_dir),
                "--arm64-out-dir", f"out/ci/ios_{build_type}",
                "--simulator-x64-out-dir", f"out/ci/ios_{build_type}_sim",
                "--simulator-arm64-out-dir", f"out/ci/ios_{build_type}_sim_arm64",
                "--dsym",
                "--strip"
            ]
            
            self.log(f"Creating iOS {build_type} framework: {' '.join(cmd)}")
            subprocess.run(cmd, cwd=self.engine_src_dir, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating iOS {build_type} framework: {e}")
            return False


class ArtifactManager:
    """Manages build artifacts and metadata"""
    
    def __init__(self, artifacts_dir: Optional[Path] = None):
        """Initialize the artifact manager
        
        Args:
            artifacts_dir: Directory to store artifact metadata (default: .build_artifacts)
        """
        self.artifacts_dir = artifacts_dir or Path(".build_artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)
        self.metadata_file = self.artifacts_dir / "metadata.json"
    
    def register_artifact(self, artifact: BuildArtifact) -> None:
        """Register a build artifact
        
        Args:
            artifact: BuildArtifact instance to register
        """
        artifacts = self.load_artifacts()
        artifacts.append(asdict(artifact))
        
        with open(self.metadata_file, 'w') as f:
            json.dump(artifacts, f, indent=2, default=str)
    
    def load_artifacts(self) -> List[Dict]:
        """Load all registered artifacts
        
        Returns:
            List of artifact metadata dictionaries
        """
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)
        return []
    
    def get_artifacts_for_config(self, config_name: str) -> List[Dict]:
        """Get artifacts for a specific configuration
        
        Args:
            config_name: Configuration name
            
        Returns:
            List of matching artifact metadata
        """
        artifacts = self.load_artifacts()
        return [a for a in artifacts if a['config_name'] == config_name]
    
    def get_latest_artifact(self, platform: str, build_type: str) -> Optional[Dict]:
        """Get the latest artifact for a platform and build type
        
        Args:
            platform: Platform name (mac, ios, android)
            build_type: Build type (debug, profile, release)
            
        Returns:
            Latest artifact metadata or None
        """
        artifacts = self.load_artifacts()
        matching = [a for a in artifacts 
                   if a['platform'] == platform and a['build_type'] == build_type]
        
        if matching:
            return max(matching, key=lambda a: a['timestamp'])
        return None
    
    def get_artifact_size(self, artifact_dir: Path) -> int:
        """Calculate total size of artifacts in a directory
        
        Args:
            artifact_dir: Directory containing artifacts
            
        Returns:
            Total size in bytes
        """
        total = 0
        for root, dirs, files in os.walk(artifact_dir):
            for file in files:
                total += os.path.getsize(os.path.join(root, file))
        return total
    
    def cleanup_old_artifacts(self, keep_count: int = 3) -> None:
        """Clean up old artifacts, keeping only the most recent ones
        
        Args:
            keep_count: Number of most recent artifacts to keep per config
        """
        artifacts = self.load_artifacts()
        
        # Group by config_name
        by_config = {}
        for artifact in artifacts:
            config = artifact['config_name']
            if config not in by_config:
                by_config[config] = []
            by_config[config].append(artifact)
        
        # Sort by timestamp and mark old ones for deletion
        to_delete = []
        for config, artifacts in by_config.items():
            sorted_artifacts = sorted(artifacts, 
                                     key=lambda a: a['timestamp'], 
                                     reverse=True)
            
            # Mark all but keep_count most recent for deletion
            for old_artifact in sorted_artifacts[keep_count:]:
                to_delete.append(old_artifact)
                if Path(old_artifact['output_dir']).exists():
                    print(f"Removing: {old_artifact['output_dir']}")
                    shutil.rmtree(old_artifact['output_dir'])
        
        # Update metadata
        remaining = [a for a in artifacts if a not in to_delete]
        with open(self.metadata_file, 'w') as f:
            json.dump(remaining, f, indent=2, default=str)
    
    def print_summary(self) -> None:
        """Print a summary of all artifacts"""
        artifacts = self.load_artifacts()
        
        if not artifacts:
            print("No artifacts registered")
            return
        
        print("\n" + "="*80)
        print("BUILD ARTIFACTS SUMMARY")
        print("="*80 + "\n")
        
        by_platform = {}
        for artifact in artifacts:
            platform = artifact['platform']
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(artifact)
        
        for platform in sorted(by_platform.keys()):
            platform_artifacts = by_platform[platform]
            print(f"\n{platform.upper()} ({len(platform_artifacts)} artifacts):")
            print("-" * 80)
            
            for artifact in sorted(platform_artifacts, key=lambda a: a['timestamp'], reverse=True):
                size_mb = artifact['size_bytes'] / (1024 * 1024)
                print(f"  {artifact['config_name']:40} "
                      f"{size_mb:8.1f} MB  "
                      f"{artifact['timestamp']:20}  "
                      f"{artifact['build_duration_seconds']:7.1f}s")
        
        print("\n" + "="*80 + "\n")


class BuildCache:
    """Manages build cache for faster rebuilds"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the build cache
        
        Args:
            cache_dir: Cache directory (default: .build_cache)
        """
        self.cache_dir = cache_dir or Path(".build_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, config_name: str) -> str:
        """Get cache key for a configuration
        
        Args:
            config_name: Configuration name
            
        Returns:
            Cache key
        """
        return config_name.replace("/", "_").replace("\\", "_")
    
    def get_cached_build(self, config_name: str) -> Optional[Path]:
        """Get cached build for a configuration
        
        Args:
            config_name: Configuration name
            
        Returns:
            Path to cached build or None
        """
        cache_key = self.get_cache_key(config_name)
        cache_path = self.cache_dir / cache_key
        
        if cache_path.exists():
            return cache_path
        return None
    
    def save_build_to_cache(self, config_name: str, build_dir: Path) -> bool:
        """Save build artifacts to cache
        
        Args:
            config_name: Configuration name
            build_dir: Directory containing build artifacts
            
        Returns:
            Success status
        """
        try:
            cache_key = self.get_cache_key(config_name)
            cache_path = self.cache_dir / cache_key
            
            # Remove old cache if it exists
            if cache_path.exists():
                shutil.rmtree(cache_path)
            
            # Copy build to cache
            shutil.copytree(build_dir, cache_path)
            return True
            
        except Exception as e:
            print(f"Error saving build to cache: {e}")
            return False
    
    def restore_build_from_cache(self, config_name: str, output_dir: Path) -> bool:
        """Restore build artifacts from cache
        
        Args:
            config_name: Configuration name
            output_dir: Output directory for restored artifacts
            
        Returns:
            Success status
        """
        try:
            cached_build = self.get_cached_build(config_name)
            if not cached_build:
                return False
            
            # Remove existing output if present
            if output_dir.exists():
                shutil.rmtree(output_dir)
            
            # Copy from cache
            shutil.copytree(cached_build, output_dir)
            return True
            
        except Exception as e:
            print(f"Error restoring build from cache: {e}")
            return False


def print_build_help() -> None:
    """Print detailed help information about builds"""
    help_text = """
FLUTTER ENGINE LOCAL BUILD - DETAILED HELP

The build system provides several utilities for managing Flutter engine builds:

1. FRAMEWORK BUILDER
   - Creates macOS and iOS frameworks from individual engine builds
   - Supports debug, profile, and release variants
   - Automatically handles dsym and strip operations

2. ARTIFACT MANAGER
   - Tracks all builds and their metadata
   - Maintains build timestamps, duration, and size
   - Supports cleanup of old builds
   - Generates summary reports

3. BUILD CACHE
   - Caches built artifacts for faster access
   - Useful for switching between different build types
   - Reduces rebuild time for similar configurations

USAGE EXAMPLES:

# Create frameworks after builds
python3 << 'EOF'
from build_utils import FrameworkBuilder
from pathlib import Path

builder = FrameworkBuilder(Path("flock/engine/src"), verbose=True)
builder.create_macos_debug_framework()
builder.create_ios_framework("debug")
EOF

# Manage artifacts
python3 << 'EOF'
from build_utils import ArtifactManager

manager = ArtifactManager()
manager.print_summary()
manager.cleanup_old_artifacts(keep_count=2)
EOF

# Use build cache
python3 << 'EOF'
from build_utils import BuildCache
from pathlib import Path

cache = BuildCache()
cached = cache.get_cached_build("ci/mac_debug_arm64")
if cached:
    print(f"Found cached build: {cached}")
EOF

For more information, see BUILD_LOCALLY.md
    """
    print(help_text)


if __name__ == "__main__":
    print_build_help()
