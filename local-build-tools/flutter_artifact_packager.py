import os
import zipfile
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

class FlutterArtifactPackager:
    def __init__(self, verbose=True):
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def process(self, build_dir, engine_hash, output_dir):
        """
        Main entry point to process a single build directory.
        
        :param build_dir: Path to the build output (e.g. 'out/android_debug_arm64')
        :param engine_hash: The Git hash of the engine
        :param output_dir: Path where final AARs/POMs should be saved
        """
        build_path = Path(build_dir)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        target_version = f"1.0.0-{engine_hash}"

        try:
            self.log(f"--- Processing {build_path.name} ---")
            
            # 1. Auto-detect artifact names from the build folder
            artifact_name, embedding_name = self._detect_artifacts(build_path)
            abi = self._get_abi_from_artifact(artifact_name)
            
            self.log(f"  Detected Artifact:  {artifact_name}")
            self.log(f"  Detected Embedding: {embedding_name}")
            self.log(f"  Target ABI:         {abi}")
            self.log(f"  Target Version:     {target_version}")

            # 2. Process Architecture Artifact (libflutter.so)
            self._create_arch_aar(build_path, out_path, artifact_name, abi, target_version)
            
            # 3. Process Embedding Artifact (flutter.jar / classes.jar)
            self._create_embedding_aar(build_path, out_path, embedding_name, target_version)

            self.log("  Done.\n")

        except Exception as e:
            print(f"Error processing {build_path}: {e}")

    # =========================================================================
    # Internal Logic Methods
    # =========================================================================

    def _create_arch_aar(self, build_dir, out_dir, artifact_name, abi, version):
        aar_name = f"{artifact_name}-{version}.aar"
        pom_name = f"{artifact_name}-{version}.pom"
        out_dir_full = out_dir / artifact_name / version
        os.makedirs(out_dir_full, exist_ok=True)
        
        # NOTE: Using 'libflutter.so' as the source for the native library.
        native_lib_source = build_dir / "libflutter.so"

        # If libflutter.so is missing, try common alternative locations
        if not native_lib_source.exists():
            # For unoptimized builds, it might be in lib.stripped/ or similar
            # However, for the standard Maven artifacts, 'libflutter.so' should be present.
            # We raise an error if the primary artifact is missing.
            raise FileNotFoundError(f"Required native library 'libflutter.so' not found in {build_dir}")

        # Create AAR
        self._zip_aar(
            output_path=out_dir_full / aar_name,
            manifest_package=f"io.flutter.{artifact_name}",
            files_to_add=[
                (native_lib_source, f"jni/{abi}/libflutter.so")
            ]
        )

        # Rewrite POM
        self._update_pom(
            source_pom=build_dir / f"{artifact_name}.pom",
            dest_pom=out_dir_full / pom_name,
            new_version=version,
            packaging="aar"
        )

    def _create_embedding_aar(self, build_dir, out_dir, embedding_name, version):
        aar_name = f"{embedding_name}-{version}.aar"
        pom_name = f"{embedding_name}-{version}.pom"
        out_dir_full = out_dir / embedding_name / version
        os.makedirs(out_dir_full, exist_ok=True)

        # Find source JAR (prefer specific name, fallback to flutter.jar)
        jar_source = build_dir / f"{embedding_name}.jar"
        if not jar_source.exists():
            jar_source = build_dir / "flutter.jar"

        # Create AAR
        self._zip_aar(
            output_path=out_dir_full / aar_name,
            manifest_package="io.flutter.embedding.android",
            files_to_add=[
                (jar_source, "classes.jar")
            ]
        )

        # Rewrite POM
        self._update_pom(
            source_pom=build_dir / f"{embedding_name}.pom",
            dest_pom=out_dir_full / pom_name,
            new_version=version,
            packaging="aar"
        )

    # =========================================================================
    # Helper Static Methods
    # =========================================================================

    @staticmethod
    def _detect_artifacts(build_dir):
        """Scans for POM files to determine the correct artifact names."""
        poms = list(build_dir.glob("*.pom"))
        embedding_pom = None
        arch_pom = None

        for pom in poms:
            if "flutter_embedding" in pom.name:
                embedding_pom = pom
            elif "x86" in pom.name or "arm" in pom.name:
                arch_pom = pom

        if not arch_pom:
            raise FileNotFoundError(f"Could not auto-detect Architecture POM in {build_dir}")
        
        embed_name = embedding_pom.stem if embedding_pom else f"flutter_embedding_{arch_pom.stem.split('_')[-1]}"
        return arch_pom.stem, embed_name

    @staticmethod
    def _get_abi_from_artifact(artifact_name):
        """Converts Flutter internal names to Android ABI names."""
        base = artifact_name.replace("_debug", "").replace("_release", "").replace("_profile", "")
        mapping = {
            "arm64_v8a": "arm64-v8a",
            "armeabi_v7a": "armeabi-v7a",
            "x86_64": "x86_64",
            "x86": "x86"
        }
        return mapping.get(base, base)

    @staticmethod
    def _zip_aar(output_path, manifest_package, files_to_add):
        """Creates the AAR zip file with a generated AndroidManifest and required res/ dir."""
        manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{manifest_package}">
    <uses-sdk android:minSdkVersion="16" />
</manifest>"""
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as aar:
            # 1. Write Manifest
            aar.writestr('AndroidManifest.xml', manifest)
            
            # 2. Write Empty res/ directory (Mandatory for valid AARs)
            # zipfile requires explicit ZipInfo for directories or a trailing slash
            res_info = zipfile.ZipInfo('res/')
            aar.writestr(res_info, '')

            # 3. Write R.txt if it exists (Optional but good practice if you find it)
            # We check the source of the first file to guess the build dir
            if files_to_add:
                first_src = files_to_add[0][0]
                r_txt = first_src.parent / "R.txt"
                if r_txt.exists():
                    aar.write(r_txt, "R.txt")

            # 4. Write valid files (classes.jar, libflutter.so, etc.)
            for src, dest in files_to_add:
                if src.exists():
                    aar.write(src, dest)
                else:
                    print(f"  ! WARNING: File missing: {src}")

    @staticmethod
    def _update_pom(source_pom, dest_pom, new_version, packaging="aar"):
        """
        Updates the version tag AND injects the packaging tag to ensure
        Gradle knows this is an AAR, not a JAR.
        """
        if not source_pom.exists():
            print(f"  ! Error: Source POM not found: {source_pom}")
            return

        ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}

        try:
            tree = ET.parse(source_pom)
            root = tree.getroot()
            
            # 1. Update Version
            version_tag = root.find('mvn:version', ns)
            if version_tag is None:
                version_tag = root.find('version') # fallback
            
            if version_tag is not None:
                version_tag.text = new_version
            else:
                print(f"  ! Warning: No <version> tag found in {source_pom.name}")

            # 2. Update/Add Packaging Tag
            packaging_tag = root.find('mvn:packaging', ns)
            if packaging_tag is None:
                packaging_tag = root.find('packaging') # fallback
            
            if packaging_tag is not None:
                packaging_tag.text = packaging
            else:
                # If missing, insert it after artifactId or version
                new_packaging = ET.Element('packaging')
                new_packaging.text = packaging
                # Inserting at index 3 is usually safe (after group, artifact, version)
                root.insert(3, new_packaging)

            tree.write(dest_pom, encoding='UTF-8', xml_declaration=True)
            
        except Exception as e:
            print(f"  ! Failed to rewrite POM {source_pom.name}: {e}")