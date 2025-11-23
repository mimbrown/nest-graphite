Here are old lines of code from build_engine_local.py that could be used if someone wants to struggle more with sky_engine.zip, flutter_gpu.zip, flutter_patched_sdk.zip, and flutter_patched_sdk_product.zip.  It is very possible to build it ourselves, but flutter is very picky on how they are zipped, and for whatever reason the built in tools didn't seem to package it quite right or I was getting confused.  In the end, we are changing graphite, which AI tells me doesn't touch the sky_engine or these other artifacts, so why bother!  I moved these lines of code here as they were causing too much clutter in the real code!


    # This is deficient because it isn't looking to add the same license file that is normally packaged, which
    # probably isn't a big dealy, but it makes me less motivated to use this.
    # def create_artifact_zip(self, source_dir, output_zip, license_file, license_arcname, root_folder_name):
    #     """
    #     Creates a strictly formatted Flutter artifact zip.
# 
    #     Structure:
    #       - [root_folder_name]/ (Contains all files from source_dir)
    #       - [license_arcname]   (The License file, placed at the zip root)
    #     """
    #     if not source_dir.exists():
    #         print(f"  ! Warning: Source directory not found: {source_dir}")
    #         return
# 
    #     print(f"  ~ Zipping {output_zip.name}...")
    #     print(f"    + Wrapping contents in '{root_folder_name}/'")
    #     print(f"    + Adding license as '{license_arcname}'")
# 
    #     with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    #         # 1. Add the License File at the root
    #         if license_file and license_file.exists():
    #             zf.write(license_file, license_arcname)
    #         else:
    #             print(f"    ! Error: License file not found at {license_file}")
# 
    #         # 2. Add the Content Directory wrapped in the root_folder_name
    #         for file in source_dir.rglob('*'):
    #             if file.is_file():
    #                 # relative_path: "lib/ui.dart"
    #                 relative_path = file.relative_to(source_dir)
    #                 # final_path:    "sky_engine/lib/ui.dart"
    #                 final_path = Path(root_folder_name) / relative_path
    #                 zf.write(file, final_path)
# 
    #     print(f"  + Created {output_zip.name}")

    # This is deficient because it doesn't account for licenses
    # def zip_directory(self, source_dir, output_zip, arcname_prefix=""):
    #     """Zips a directory recursively."""
    #     if not source_dir.exists():
    #         print(f"  ! Warning: Source directory not found: {source_dir}")
    #         return
# 
    #     print(f"  ~ Zipping {source_dir.name} -> {output_zip.name}...")
    #     with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    #         for file in source_dir.rglob('*'):
    #             if file.is_file():
    #                 # Make path relative to source
    #                 rel_path = file.relative_to(source_dir)
    #                 # If a prefix is needed (e.g. putting it inside a folder in the zip), add it
    #                 arcname = Path(arcname_prefix) / rel_path if arcname_prefix else rel_path
    #                 zf.write(file, arcname)
    #     print(f"  + Created {output_zip.name}")




# from build_engine:
            # "flutter:dist" is a ninja target that builds flutter_gpu.zip, flutter_patched_sdk.zip,
            # flutter_patched_sdk_product.zip, and sky_engine.zip. The problem is that it doesn't exactly build it 
            # the way that it is uploaded. At leastthat's how it has appeared to me, but it has been tricky to tell 
            # as one bad file can be hard to clearthe cache, and then you can get confused if your new attempt didn't 
            # work because the zip file wasn'ta good match, or did it not work because the old file is still in your 
            # cache! Regardless, these could be modified to match, but it is easier to download from the original Flutter bucket.
            # This command is not supported in WASM. For Android it makes these files in every Android folder, which
            # is not the way it is found in the bucket.
            # if "wasm" not in config.config_name and "android" not in config.config_name:
            #     cmd.append("flutter:dist")

            # This is missing a license file.
            # # Special case for building sky_engine.zip:
            # if config.config_name == "ci/host_debug":
            #     sky_engine_src = cwd/ "out" / config.config_name  / "gen" / "dart-pkg" / "sky_engine"
            #     self.zip_directory(sky_engine_src, zip_dir / "sky_engine.zip")
            #     self.log(f"Successfully built sky_engine")
# 
            # # Special case for building flutter_gpu.zip:
            # if config.config_name == "ci/host_debug":
            #     # 4. flutter_gpu.zip
            #     # The flutter_gpu package source is in src/flutter/lib/gpu
            #     gpu_src = cwd / "flutter" / "lib" / "gpu"
            #     if gpu_src.exists():
            #         self.zip_directory(gpu_src, zip_dir / "flutter_gpu.zip")
            #         self.log(f"Successfully built flutter_gpu")
            #     else:
            #         print(f"  ! Error: Could not find flutter_gpu source at {gpu_src}.")
# 
            # # Special case for building flutter_patched_sdk.zip:
            # if config.config_name == "ci/host_debug":
            #     cmd = [
            #         "ninja",
            #         "-C", f"out/{config.config_name}",
            #         "flutter/build/archives:flutter_patched_sdk"
            #     ]
            #     self.run_command(cmd, cwd=cwd)
            #     self.log(f"Successfully built flutter_patched_sdk")
# 
            # # Special case for building flutter_patched_sdk_product.zip:
            # if config.config_name == "ci/host_release":
            #     release_sdk_src = cwd / "out" / config.config_name / "flutter_patched_sdk"
            #     self.zip_directory(release_sdk_src, zip_dir / "flutter_patched_sdk_product.zip")
            #     self.log(f"Successfully built flutter_patched_sdk_product")