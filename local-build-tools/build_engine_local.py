#!/usr/bin/env python3
"""
Local Flutter Engine Builder - Converts GitHub Actions workflow to local macOS builds
Supports building macOS, iOS, Android (with Mac), Android (with Linux), Linux, and Web engines locally
"""

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum
import shutil
import xml.etree.ElementTree as ET
from flutter_artifact_packager import FlutterArtifactPackager

class Platform(Enum):
    """Supported build platforms"""
    MAC = "mac"
    IOS = "ios"
    ANDROID = "android"
    ANDROIDLINUX = "androidlinux"
    ANDROIDWINDOWS = "androidwindows"
    WINDOWS = "windows"
    LINUX = "linux"
    WEB = "web"

class BuildConfig:
    """Represents a single build configuration"""
    def __init__(self, name: str, config_name: str, platform: Platform):
        self.name = name
        self.config_name = config_name
        self.platform = platform 

FlutterMacOSFrameworks = {
    "ci/mac_debug_framework_arm64": Path("ci/mac_debug_framework_arm64"),
    "ci/host_debug_framework": Path("ci/host_debug_framework"),
    "ci/mac_profile_framework_arm64": Path("ci/mac_profile_framework_arm64"),
    "ci/host_profile_framework": Path("ci/host_profile_framework"),
    "ci/mac_release_framework_arm64": Path("ci/mac_release_framework_arm64"),
    "ci/host_release_framework": Path("ci/host_release_framework"),
    "ci/mac_debug_gen_snapshot_arm64": Path("ci/mac_debug_gen_snapshot_arm64"),
    "ci/host_debug_gen_snapshot": Path("ci/host_debug_gen_snapshot"),
    "ci/mac_profile_gen_snapshot_arm64": Path("ci/mac_profile_gen_snapshot_arm64"),
    "ci/host_profile_gen_snapshot": Path("ci/host_profile_gen_snapshot"),
    "ci/mac_release_gen_snapshot_arm64": Path("ci/mac_release_gen_snapshot_arm64"),
    "ci/host_release_gen_snapshot": Path("ci/host_release_gen_snapshot"),
}

FlutterIOSFrameworks = {
    "ios": "ci/ios_debug",
    "ios-profile": "ci/ios_profile",
    "ios-release": "ci/ios_release",
}

class FlutterEngineBuilder:
    """Main builder class for local Flutter engine builds"""
    
    # macOS build configurations
    MAC_CONFIGS = [
        BuildConfig("mac debug arm64", "ci/mac_debug_arm64", Platform.MAC),
        BuildConfig("mac debug framework arm64", "ci/mac_debug_framework_arm64", Platform.MAC),
        BuildConfig("mac debug gen snapshot arm64", "ci/mac_debug_gen_snapshot_arm64", Platform.MAC),
        BuildConfig("mac profile arm64", "ci/mac_profile_arm64", Platform.MAC),
        BuildConfig("mac profile framework arm64", "ci/mac_profile_framework_arm64", Platform.MAC),
        BuildConfig("mac profile gen snapshot arm64", "ci/mac_profile_gen_snapshot_arm64", Platform.MAC),
        BuildConfig("mac release arm64", "ci/mac_release_arm64", Platform.MAC),
        BuildConfig("mac release framework arm64", "ci/mac_release_framework_arm64", Platform.MAC),
        BuildConfig("mac release gen snapshot arm64", "ci/mac_release_gen_snapshot_arm64", Platform.MAC),
        BuildConfig("mac host debug", "ci/host_debug", Platform.MAC),
        BuildConfig("mac host debug clang tidy", "ci/host_debug_clang_tidy", Platform.MAC),
        BuildConfig("mac host debug framework", "ci/host_debug_framework", Platform.MAC),
        BuildConfig("mac host debug gen snapshot", "ci/host_debug_gen_snapshot", Platform.MAC),
        BuildConfig("mac host debug unopt arm64", "ci/host_debug_unopt_arm64", Platform.MAC),
        BuildConfig("mac host profile", "ci/host_profile", Platform.MAC),
        BuildConfig("mac host profile framework", "ci/host_profile_framework", Platform.MAC),
        BuildConfig("mac host profile gen snapshot", "ci/host_profile_gen_snapshot", Platform.MAC),
        BuildConfig("mac host release", "ci/host_release", Platform.MAC),
        BuildConfig("mac host release arm64 licenses", "ci/host_release_arm64_licenses", Platform.MAC),
        BuildConfig("mac host release framework", "ci/host_release_framework", Platform.MAC),
        BuildConfig("mac host release gen snapshot", "ci/host_release_gen_snapshot", Platform.MAC),
    ]
    
    # iOS build configurations
    IOS_CONFIGS = [
        BuildConfig("ios debug", "ci/ios_debug", Platform.IOS),
        BuildConfig("ios debug sim", "ci/ios_debug_sim", Platform.IOS),
        BuildConfig("ios debug sim arm64", "ci/ios_debug_sim_arm64", Platform.IOS),
        BuildConfig("ios profile", "ci/ios_profile", Platform.IOS),
        BuildConfig("ios release", "ci/ios_release", Platform.IOS),
        BuildConfig("ios debug extension safe", "ci/ios_debug_extension_safe", Platform.IOS),
        BuildConfig("ios debug sim arm64 extension safe", "ci/ios_debug_sim_arm64_extension_safe", Platform.IOS),
        BuildConfig("ios debug sim extension safe", "ci/ios_debug_sim_extension_safe", Platform.IOS),
        BuildConfig("ios debug unopt sim arm64 extension safe", "ci/ios_debug_unopt_sim_arm64_extension_safe", Platform.IOS),
        BuildConfig("ios profile extension safe", "ci/ios_profile_extension_safe", Platform.IOS),
        BuildConfig("ios release extension safe", "ci/ios_release_extension_safe", Platform.IOS),
    ]
    
    # Android build configurations (macOS runners)
    ANDROID_MAC_CONFIGS = [
        BuildConfig("android debug arm64", "android_debug_arm64", Platform.ANDROID),
        BuildConfig("android debug unopt", "android_debug_unopt", Platform.ANDROID),
        BuildConfig("android debug unopt arm64", "android_debug_unopt_arm64", Platform.ANDROID),
        BuildConfig("android profile", "ci/android_profile", Platform.ANDROID),
        BuildConfig("android profile arm64", "ci/android_profile_arm64", Platform.ANDROID),
        BuildConfig("android profile x64", "ci/android_profile_x64", Platform.ANDROID),
        BuildConfig("android release", "ci/android_release", Platform.ANDROID),
        BuildConfig("android release arm64", "ci/android_release_arm64", Platform.ANDROID),
        BuildConfig("android release x64", "ci/android_release_x64", Platform.ANDROID),
    ]

    # Android build configurations (ubuntu runners)
    # Prefer CI to non-CI build configurations
    # If this is planned to be run on both Linux and macOS, then duplicates can probably be removed
    ANDROID_LINUX_CONFIGS = [
        BuildConfig("android debug unopt arm64", "android_debug_unopt_arm64", Platform.ANDROID),
        BuildConfig("android debug unopt x64", "android_debug_unopt_x64", Platform.ANDROID),
        BuildConfig("android debug", "ci/android_debug", Platform.ANDROID),
        BuildConfig("android debug unopt", "ci/android_debug_unopt", Platform.ANDROID),
        BuildConfig("android debug arm64", "ci/android_debug_arm64", Platform.ANDROID),
        BuildConfig("android debug x64", "ci/android_debug_x64", Platform.ANDROID),
        BuildConfig("android debug x86", "ci/android_debug_x86", Platform.ANDROID),
        BuildConfig("android embedder debug unopt", "ci/android_embedder_debug_unopt", Platform.ANDROID),
        BuildConfig("android emulator debug x64", "ci/android_emulator_debug_x64", Platform.ANDROID),
        BuildConfig("android profile", "ci/android_profile", Platform.ANDROID),
        BuildConfig("android profile arm64", "ci/android_profile_arm64", Platform.ANDROID),
        BuildConfig("android profile x64", "ci/android_profile_x64", Platform.ANDROID),
        BuildConfig("android release", "ci/android_release", Platform.ANDROID),
        BuildConfig("android release arm64", "ci/android_release_arm64", Platform.ANDROID),
        BuildConfig("android release x64", "ci/android_release_x64", Platform.ANDROID),
    ]

    # Linux build configurations
    LINUX_CONFIGS = [
        BuildConfig("linux debug arm64", "ci/linux_debug_arm64", Platform.LINUX),
        BuildConfig("linux profile arm64", "ci/linux_profile_arm64", Platform.LINUX),
        BuildConfig("linux release arm64", "ci/linux_release_arm64", Platform.LINUX),
        BuildConfig("linux host debug", "ci/host_debug", Platform.LINUX),
        BuildConfig("linux host debug clang tidy", "ci/host_debug_clang_tidy", Platform.LINUX),
        BuildConfig("linux host debug desktop", "ci/host_debug_desktop", Platform.LINUX),
        BuildConfig("linux host debug unopt", "ci/host_debug_unopt", Platform.LINUX),
        BuildConfig("linux host release", "ci/host_release", Platform.LINUX),
        BuildConfig("linux host release desktop", "ci/host_release_desktop", Platform.LINUX),
        BuildConfig("linux host release licenses", "ci/host_release_licenses", Platform.LINUX),
    ]
    
    #Windows build configurations
    WINDOWS_CONFIGS = [
        BuildConfig("windows host debug", "ci/host_debug", Platform.WINDOWS),
        BuildConfig("windows host profile", "ci/host_profile", Platform.WINDOWS),
        BuildConfig("windows host release", "ci/host_release", Platform.WINDOWS),
        BuildConfig("windows host debug arm64", "ci/host_debug_arm64", Platform.WINDOWS),
        BuildConfig("windows host profile arm64", "ci/host_profile_arm64", Platform.WINDOWS),
        BuildConfig("windows host release arm64", "ci/host_release_arm64", Platform.WINDOWS),
    ]
    
    #Android build configurations (Windows runners)
    ANDROID_WINDOWS_CONFIGS = [
        BuildConfig("windows android profile", "ci/android_profile", Platform.ANDROID),
        BuildConfig("windows android profile arm64", "ci/android_profile_arm64", Platform.ANDROID),
        BuildConfig("windows android profile x64", "ci/android_profile_x64", Platform.ANDROID),
        BuildConfig("windows android release", "ci/android_release", Platform.ANDROID),
        BuildConfig("windows android release arm64", "ci/android_release_arm64", Platform.ANDROID),
        BuildConfig("windows android release x64", "ci/android_release_x64", Platform.ANDROID),
    ]
    
    # Web/WASM build configurations (can be built on macOS and Linux)
    WEB_CONFIGS = [
        BuildConfig("web wasm debug unopt", "wasm_debug_unopt", Platform.WEB),
        BuildConfig("web wasm release", "wasm_release", Platform.WEB),
    ]
    
    def __init__(self, workspace_root: Optional[str] = None, verbose: bool = False):
        """Initialize the builder
        
        Args:
            workspace_root: Root directory of the workspace (default: current directory)
            verbose: Enable verbose output
        """
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.verbose = verbose
        self.flock_dir = self.workspace_root / "flock"
        self.engine_src_dir = self.flock_dir / "engine" / "src"

        # Find Engine Version Hash
        with open(f"{self.flock_dir}/bin/internal/engine.version",'r',encoding='utf-8-sig') as engineVersion:
            self.hash = engineVersion.read().strip()
        
        # Environment variables
        self.env = os.environ.copy()
        self.env["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
        self.env["FLUTTER_BRANCH"] = "stable"
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        print(f"[{level}] {message}")
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command
        
        Args:
            cmd: Command to run as list
            cwd: Working directory
            check: Raise exception on non-zero exit
            capture_output: Capture stdout/stderr
            
        Returns:
            CompletedProcess object
        """
        if self.verbose:
            self.log(f"Running: {' '.join(cmd)}")
        
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=self.env,
            check=check,
            capture_output=capture_output,
            text=True
        )
    
    def check_xcode_version(self, required_version: str = "16.4"):
        """Check and set Xcode version
        
        Args:
            required_version: Required Xcode version
        """
        self.log(f"Checking Xcode version (required: {required_version})")
        
        try:
            result = self.run_command(
                ["xcode-select", "--print-path"],
                capture_output=True
            )
            xcode_path = result.stdout.strip()
            self.log(f"Current Xcode path: {xcode_path}")
            
            # Try to extract version
            version_result = self.run_command(
                ["xcodebuild", "-version"],
                capture_output=True
            )
            self.log(f"Xcode version info:\n{version_result.stdout}")
            
        except Exception as e:
            self.log(f"Warning: Could not check Xcode version: {e}", "WARN")
    
    def setup_depot_tools(self):
        """Setup depot_tools if not already present"""
        depot_tools_home = Path.home() / "depot_tools"
        
        if depot_tools_home.exists():
            self.log(f"depot_tools already exists at {depot_tools_home}")
            return str(depot_tools_home)
        
        self.log("Setting up depot_tools...")
        self.run_command([
            "git", "clone",
            "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
            str(depot_tools_home)
        ])
        
        # Add to PATH for this process
        self.env["PATH"] = f"{depot_tools_home}:{self.env.get('PATH', '')}"
        self.log(f"depot_tools installed at {depot_tools_home}")
        
        return str(depot_tools_home)
    
    def assemble_flock(self, flutter_ref: str = "stable", token: Optional[str] = None):
        """Assemble the flock repository
        
        Args:
            flutter_ref: Flutter branch/ref to use
            token: GitHub token for authentication
        """
        self.log(f"Assembling flock with Flutter ref: {flutter_ref}")
        
        if not self.flock_dir.exists():
            self.log("Flock directory not found, this should be checked out already", "WARN")
            return False
        
        # Note: In real usage, you'd need to implement the actual flock assembly
        # This is typically handled by the assemble-flock GitHub action
        self.log("Flock directory exists, ready for build")
        return True

    def build_engine(self, config: BuildConfig, output_dir: Optional[Path] = None):
        """Build engine
        
        Args:
            config_name: Configuration name (e.g., "ci/mac_debug_arm64", "ci/android_release", "wasm_debug_unopt", "ci/ios_debug")
            output_dir: Output directory for build artifacts
        """
        self.log(f"Building {config.platform.value} engine: {config.config_name}")
        
        if not self.engine_src_dir.exists():
            self.log(f"Engine source directory not found: {self.engine_src_dir}", "ERROR")
            return False
        
        try:
            # Change to engine source directory
            cwd = self.engine_src_dir
            
            # Run the build command
            cmd = [
                "./flutter/bin/et","build",
                "--config", config.config_name
            ]
            
            self.run_command(cmd, cwd=cwd)
            
            # Build with ninja
            cmd = [
                "ninja",
                "-C", f"out/{config.config_name}"
            ]
            
            self.run_command(cmd, cwd=cwd)
            self.log(f"Successfully built {config.config_name}")
            
            # Move zip files to flutter_infra_release folder
            zip_dir = cwd / "out" / config.config_name / "zip_archives"
            dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}"
            if os.path.isdir(zip_dir) and os.listdir(zip_dir) and config.config_name.find("test") == -1:
                shutil.copytree(zip_dir,dest_dir, dirs_exist_ok=True)
                self.log(f"Successfully copied {config.config_name} zip files")

            if "android" in config.config_name:
                # Package AAR files from .so and .jar files and rename POM files
                io_dir = f"{self.engine_src_dir}/out/download.flutter.io/io/flutter/"
                packager = FlutterArtifactPackager(verbose=True)
                packager.process(
                    build_dir=f"{self.engine_src_dir}/out/{config.config_name}",
                    engine_hash=self.hash,
                    output_dir=io_dir)
                self.log(f"Successfully built {config.config_name} AAR files")

            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Build failed: {e}", "ERROR")
            return False
    
    def build_multiple(self, configs: List[BuildConfig], parallel: bool = False):
        """Build multiple configurations
        
        Args:
            configs: List of build configurations
            parallel: Build in parallel (limited by max_parallel)
        """
        results = {}
        
        for config in configs:
            self.log(f"\n{'='*60}")
            self.log(f"Building: {config.name}\n{'='*60}\n")

            success = self.build_engine(config)
            #self.log(f"Platform {config.platform.value} not yet implemented for local builds", "WARN")
            #success = False
            
            results[config.name] = success
        
        return results
    
    def create_macos_frameworks(self, build_outputs: Dict[str, Path]):
        """Create macOS frameworks from build outputs
        
        Args:
            build_outputs: Dictionary mapping config names to output paths
        """
        self.log("Creating macOS frameworks...")
        
        cwd = self.engine_src_dir
        
        # mac_debug_framework_arm64 framework creation
        if "ci/mac_debug_framework_arm64" in build_outputs and "ci/host_debug_framework" in build_outputs:
            try:
                out_dir = "out/debug/framework"
                cmd = [
                    "python3", "flutter/sky/tools/create_embedder_framework.py",
                    "--dst", out_dir,
                    "--arm64-out-dir", "out/ci/mac_debug_framework_arm64",
                    "--x64-out-dir", "out/ci/host_debug_framework",
                    "--zip"
                ]
                
                self.run_command(cmd, cwd=cwd)
                self.log("Successfully created debug embedder framework")

                zip_dir = f"{self.engine_src_dir}/{out_dir}"
                dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/darwin-x64/"
                os.makedirs(dest_dir, exist_ok=True)
                if os.path.isdir(zip_dir) and os.listdir(zip_dir):
                    shutil.copyfile(f"{zip_dir}/FlutterEmbedder.framework.zip",f"{dest_dir}/FlutterEmbedder.framework.zip")
                    self.log(f"Successfully copied embedder framework files to darwin-x64")

                cmd = [
                    "python3", "flutter/sky/tools/create_macos_framework.py",
                    "--dst", out_dir,
                    "--arm64-out-dir", "out/ci/mac_debug_framework_arm64",
                    "--x64-out-dir", "out/ci/host_debug_framework",
                    "--zip"
                ]
                
                self.run_command(cmd, cwd=cwd)
                self.log("Successfully created debug macos framework")

                zip_dir = f"{self.engine_src_dir}/{out_dir}"
                dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/darwin-x64/"
                if os.path.isdir(zip_dir) and os.listdir(zip_dir):
                    shutil.copyfile(f"{zip_dir}/FlutterMacOS.framework.zip",f"{dest_dir}/FlutterMacOS.framework.zip")
                    shutil.copyfile(f"{zip_dir}/framework.zip",f"{dest_dir}/framework.zip")
                    self.log(f"Successfully copied framework files to darwin-x64")
                
            except subprocess.CalledProcessError as e:
                self.log(f"Framework creation failed: {e}", "ERROR")

        # mac_profile_framework_arm64 framework creation
        if "ci/mac_profile_framework_arm64" in build_outputs and "ci/host_profile_framework" in build_outputs:
            try:
                out_dir = "out/profile/framework"
                cmd = [
                    "python3", "flutter/sky/tools/create_macos_framework.py",
                    "--dst", out_dir,
                    "--arm64-out-dir", "out/ci/mac_profile_framework_arm64",
                    "--x64-out-dir", "out/ci/host_profile_framework",
                    "--zip"
                ]
                
                self.run_command(cmd, cwd=cwd)
                self.log("Successfully created profile macos framework")

                zip_dir = f"{self.engine_src_dir}/{out_dir}"
                dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/darwin-x64-profile/"
                os.makedirs(dest_dir, exist_ok=True)
                if os.path.isdir(zip_dir) and os.listdir(zip_dir):
                    shutil.copyfile(f"{zip_dir}/FlutterMacOS.framework.zip",f"{dest_dir}/FlutterMacOS.framework.zip")
                    shutil.copyfile(f"{zip_dir}/framework.zip",f"{dest_dir}/framework.zip")
                    self.log(f"Successfully copied framework files to darwin-x64-profile")
                
            except subprocess.CalledProcessError as e:
                self.log(f"Framework creation failed: {e}", "ERROR")

        # mac_release_framework_arm64 framework creation
        if "ci/mac_release_framework_arm64" in build_outputs and "ci/host_release_framework" in build_outputs:
            try:
                out_dir = "out/release/framework"
                cmd = [
                    "python3", "flutter/sky/tools/create_macos_framework.py",
                    "--dst", out_dir,
                    "--arm64-out-dir", "out/ci/mac_release_framework_arm64",
                    "--x64-out-dir", "out/ci/host_release_framework",
                    "--zip"
                ]
                
                self.run_command(cmd, cwd=cwd)
                self.log("Successfully created release macos framework")

                zip_dir = f"{self.engine_src_dir}/{out_dir}"
                dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/darwin-x64-release/"
                os.makedirs(dest_dir, exist_ok=True)
                if os.path.isdir(zip_dir) and os.listdir(zip_dir):
                    shutil.copyfile(f"{zip_dir}/FlutterMacOS.framework.zip",f"{dest_dir}/FlutterMacOS.framework.zip")
                    shutil.copyfile(f"{zip_dir}/framework.zip",f"{dest_dir}/framework.zip")
                    self.log(f"Successfully copied framework files to darwin-x64-release")
                
            except subprocess.CalledProcessError as e:
                self.log(f"Framework creation failed: {e}", "ERROR")

        # mac_debug_gen_snapshot_arm64 framework creation
        if "ci/mac_debug_gen_snapshot_arm64" in build_outputs and "ci/host_debug_gen_snapshot" in build_outputs:
            try:
                out_dir = "out/debug/snapshot"
                cmd = [
                    "python3", "flutter/sky/tools/create_macos_gen_snapshots.py",
                    "--dst", out_dir,
                    "--arm64-path", "out/ci/mac_debug_gen_snapshot_arm64/universal/gen_snapshot_arm64",
                    "--x64-path", "out/ci/host_debug_gen_snapshot/universal/gen_snapshot_x64",
                    "--zip"
                ]
                
                self.run_command(cmd, cwd=cwd)
                self.log("Successfully created debug macos gen snapshot")

                zip_dir = f"{self.engine_src_dir}/{out_dir}"
                dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/darwin-x64/"
                os.makedirs(dest_dir, exist_ok=True)
                if os.path.isdir(zip_dir) and os.listdir(zip_dir):
                    shutil.copyfile(f"{zip_dir}/gen_snapshot.zip",f"{dest_dir}/gen_snapshot.zip")
                    self.log(f"Successfully copied snapshot files to darwin-x64")
                
            except subprocess.CalledProcessError as e:
                self.log(f"Framework creation failed: {e}", "ERROR")

        # mac_profile_gen_snapshot_arm64 framework creation
        if "ci/mac_profile_gen_snapshot_arm64" in build_outputs and "ci/host_profile_gen_snapshot" in build_outputs:
            try:
                out_dir = "out/profile/snapshot"
                cmd = [
                    "python3", "flutter/sky/tools/create_macos_gen_snapshots.py",
                    "--dst", out_dir,
                    "--arm64-path", "out/ci/mac_profile_gen_snapshot_arm64/universal/gen_snapshot_arm64",
                    "--x64-path", "out/ci/host_profile_gen_snapshot/universal/gen_snapshot_x64",
                    "--zip"
                ]
                
                self.run_command(cmd, cwd=cwd)
                self.log("Successfully created profile macos gen snapshot")

                zip_dir = f"{self.engine_src_dir}/{out_dir}"
                dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/darwin-x64-profile/"
                os.makedirs(dest_dir, exist_ok=True)
                if os.path.isdir(zip_dir) and os.listdir(zip_dir):
                    shutil.copyfile(f"{zip_dir}/gen_snapshot.zip",f"{dest_dir}/gen_snapshot.zip")
                    self.log(f"Successfully copied snapshot files to darwin-x64-profile")
                
            except subprocess.CalledProcessError as e:
                self.log(f"Framework creation failed: {e}", "ERROR")

        # mac_release_gen_snapshot_arm64 framework creation
        if "ci/mac_release_gen_snapshot_arm64" in build_outputs and "ci/host_release_gen_snapshot" in build_outputs:
            try:
                out_dir = "out/release/snapshot"
                cmd = [
                    "python3", "flutter/sky/tools/create_macos_gen_snapshots.py",
                    "--dst", out_dir,
                    "--arm64-path", "out/ci/mac_release_gen_snapshot_arm64/universal/gen_snapshot_arm64",
                    "--x64-path", "out/ci/host_release_gen_snapshot/universal/gen_snapshot_x64",
                    "--zip"
                ]
                
                self.run_command(cmd, cwd=cwd)
                self.log("Successfully created release macos gen snapshot")

                zip_dir = f"{self.engine_src_dir}/{out_dir}"
                dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/darwin-x64-release/"
                os.makedirs(dest_dir, exist_ok=True)
                if os.path.isdir(zip_dir) and os.listdir(zip_dir):
                    shutil.copyfile(f"{zip_dir}/gen_snapshot.zip",f"{dest_dir}/gen_snapshot.zip")
                    self.log(f"Successfully copied snapshot files to darwin-x64-release")
                
            except subprocess.CalledProcessError as e:
                self.log(f"Framework creation failed: {e}", "ERROR")
    
    def create_ios_frameworks(self, build_outputs: Dict[str, str]):
        """Create iOS frameworks from build outputs
        
        Args:
            build_outputs: Dictionary mapping config names to output paths
        """
        self.log("Creating iOS frameworks...")
        
        cwd = self.engine_src_dir

        for name, path in build_outputs.items():
            if name in ["ios", "ios-profile", "ios-release"]:
                try:
                    out_dir = f"out/{name}"
                    cmd = [
                        "python3", "flutter/sky/tools/create_ios_framework.py",
                        "--dst", out_dir,
                        "--arm64-out-dir", f"out/{path}",
                        "--simulator-x64-out-dir", f"out/ci/ios_debug_sim",
                        "--simulator-arm64-out-dir", f"out/ci/ios_debug_sim_arm64",
                        "--dsym",
                        "--strip"
                    ]

                    self.run_command(cmd, cwd=cwd)
                    self.log(f"Successfully created {name} framework")

                    # Copy this to the flutter_infra_release folder
                    zip_dir = f"{self.engine_src_dir}/{out_dir}"
                    dest_dir = f"{self.engine_src_dir}/out/flutter_infra_release/flutter/{self.hash}/{name}/"
                    os.makedirs(dest_dir, exist_ok=True)
                    if os.path.isdir(f"{self.engine_src_dir}/{out_dir}") and os.listdir(f"{self.engine_src_dir}/{out_dir}"):
                        zip_files = list(Path(zip_dir).glob("*.zip")) 
                        for zip_file in zip_files:
                            shutil.copyfile(zip_file,f"{dest_dir}/{os.path.basename(zip_file)}")
                            self.log(f"Successfully copied os.path.basename(zip_file)")

                except subprocess.CalledProcessError as e:
                    self.log(f"iOS framework creation failed: {e}", "ERROR")
    
    def list_available_configs(self):
        """List all available build configurations"""
        print("\n" + "="*60)
        print("AVAILABLE BUILD CONFIGURATIONS")
        print("="*60 + "\n")
        
        configs_by_platform = {
            Platform.MAC: self.MAC_CONFIGS,
            Platform.IOS: self.IOS_CONFIGS,
            Platform.ANDROID: self.ANDROID_MAC_CONFIGS,
            Platform.ANDROIDLINUX: self.ANDROID_LINUX_CONFIGS,
            Platform.ANDROIDWINDOWS: self.ANDROID_WINDOWS_CONFIGS,
            Platform.LINUX: self.LINUX_CONFIGS,
            Platform.WINDOWS: self.WINDOWS_CONFIGS,
            Platform.WEB: self.WEB_CONFIGS,
        }
        
        for platform, configs in configs_by_platform.items():
            print(f"\n{platform.value.upper()} BUILDS ({len(configs)}):")
            print("-" * 60)
            for i, config in enumerate(configs, 1):
                print(f"  {i:2}. {config.name:45} ({config.config_name})")
        
        print("\n" + "="*60 + "\n")

    def list_available_frameworks(self):
        """List all available framewok build"""
        print("\n" + "="*60)
        print("AVAILABLE FRAMEWORK BUILD")
        print("="*60 + "\n")




def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Local Flutter Engine Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available configurations
  %(prog)s --list
  
  # Build a specific macOS configuration
  %(prog)s --platform mac --config "ci/mac_debug_arm64"
  
  # Build all macOS configurations
  %(prog)s --platform mac --all
  
  # Build specific iOS configuration
  %(prog)s --platform ios --config "ci/ios_debug"

  # Build frameworks for all available platforms
  %(prog)s --framework
  
  # Check Xcode setup
  %(prog)s --check-xcode
        """
    )
    
    parser.add_argument(
        "--workspace",
        default=None,
        help="Workspace root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available build configurations"
    )
    
    parser.add_argument(
        "--platform",
        choices=["mac", "ios", "android", "androidlinux", "linux", "androidwindows", "windows", "web"],
        help="Target platform to build"
    )
    
    parser.add_argument(
        "--framework",
        action="store_true",
        help="Build all available frameworks"
    )
    
    parser.add_argument(
        "--config",
        help="Specific configuration to build (e.g., ci/mac_debug_arm64)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build all configurations for the specified platform"
    )
    
    parser.add_argument(
        "--check-xcode",
        action="store_true",
        help="Check Xcode version and setup"
    )
    
    parser.add_argument(
        "--setup-depot-tools",
        action="store_true",
        help="Setup depot_tools if not present"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Create builder instance
    builder = FlutterEngineBuilder(
        workspace_root=args.workspace,
        verbose=args.verbose
    )

    # Handle framework command
    if (args.framework and not args.platform):
        builder.create_ios_frameworks(FlutterIOSFrameworks)
        builder.create_macos_frameworks(FlutterMacOSFrameworks)
        return 0
    
    # Handle list command
    if args.list:
        builder.list_available_configs()
        return 0
    
    # Handle check-xcode command
    if args.check_xcode:
        builder.check_xcode_version()
        return 0
    
    # Handle setup-depot-tools command
    if args.setup_depot_tools:
        builder.setup_depot_tools()
        return 0
    
    # Handle build commands
    if args.platform:
        platform = Platform(args.platform)
        
        # Get configurations to build
        if args.platform == "mac":
            configs = builder.MAC_CONFIGS
        elif args.platform == "ios":
            configs = builder.IOS_CONFIGS
        elif args.platform == "android":
            configs = builder.ANDROID_MAC_CONFIGS
        elif args.platform == "androidlinux":
            configs = builder.ANDROID_LINUX_CONFIGS
        elif args.platform == "androidwinodws":
            configs = builder.ANDROID_WINDOWS_CONFIGS
        elif args.platform == "linux":
            configs = builder.LINUX_CONFIGS
        elif args.platform == "winodws":
            configs = builder.WINDOWS_CONFIGS
        elif args.platform == "web":
            configs = builder.WEB_CONFIGS
        else:
            print(f"Platform {args.platform} not yet fully implemented", file=sys.stderr)
            return 1
        
        # Filter by specific config if provided
        if args.config:
            configs = [c for c in configs if c.config_name == args.config]
            if not configs:
                print(f"Configuration not found: {args.config}", file=sys.stderr)
                return 1
        elif not args.all:
            print("Please specify --config or --all", file=sys.stderr)
            parser.print_help()
            return 1
        
        # Run builds
        results = builder.build_multiple(configs)

        # Handle framework command
        if (args.framework):
            if (args.platform == "ios"):
                builder.create_ios_frameworks(FlutterIOSFrameworks)
            elif (args.platform == "mac"):
                builder.create_macos_frameworks(FlutterMacOSFrameworks)
        
        # Print summary
        print("\n" + "="*60)
        print("BUILD SUMMARY")
        print("="*60)
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"\nCompleted: {successful}/{total}")
        for name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"  {status}: {name}")
        
        return 0 if successful == total else 1
    
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
