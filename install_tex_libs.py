#!/usr/bin/env python3
"""
Download and extract ciadslides.tar.gz, but only the contents of the 'ciadslides/'
subfolder, excluding:
  - any .tex or .md files
  - any files under ciadslides/docfigs/

Additionally, download two extra .sty files from GitHub:
  - autolatex.sty
  - autolatex-beamer.sty

All extracted files (from the archive) and these additional .sty files are placed
directly into the script's folder. After extraction/download, the script adds every
file to .gitignore, and finally deletes any 'ciadslides/' folder that may exist.

A progress bar is displayed during each download.
"""

import os
import sys
import urllib.request
import tempfile
import tarfile
import shutil

# Optional colorama – gracefully fall back if not installed
try:
    from colorama import Fore, Style
except ImportError:
    class Fore:
        RED = BLUE = RESET = ''
    Style = Fore

# The URL of the archive
BEAMER_ARCHIVE_URL = "https://www.arakhne.org/download/latex/slides%20-%20beamer/ciadslides.tar.gz"

# Additional .sty files to download
EXTRA_STY_FILES = [
    {
        "url": "https://raw.githubusercontent.com/gallandarakhneorg/autolatex2/refs/heads/master/src/autolatex2/tex/autolatex.sty",
        "filename": "autolatex.sty"
    },
    {
        "url": "https://raw.githubusercontent.com/gallandarakhneorg/autolatex2/refs/heads/master/src/autolatex2/tex/autolatex-beamer.sty",
        "filename": "autolatex-beamer.sty"
    }
]

# The name of the top-level directory we want to extract (and then strip)
TARGET_TOP_DIR = "ciadslides/"

# Subdirectory to skip entirely (inside TARGET_TOP_DIR)
SKIP_SUBDIR = "docfigs/"

# File extensions to skip (in addition to the subdirectory rule)
SKIP_EXTENSIONS = (".tex", ".md")

def error(*messages: str):
    for message in messages:
        print(Fore.RED + f"ERROR: {message}" + Style.RESET_ALL, file=sys.stderr)
    sys.exit(255)

def info(*messages: str):
    for message in messages:
        print(Fore.BLUE + f"INFO : {message}" + Style.RESET_ALL)

def should_skip(member_name: str) -> bool:
    """
    Return True if the member should be skipped.
    Conditions:
      - ends with .tex or .md (case‑insensitive)
      - is inside ciadslides/docfigs/ (any depth)
    """
    lower_name = member_name.lower()
    for ext in SKIP_EXTENSIONS:
        if lower_name.endswith(ext):
            return True

    if member_name.startswith(TARGET_TOP_DIR + SKIP_SUBDIR):
        return True
    if member_name == TARGET_TOP_DIR + SKIP_SUBDIR.rstrip('/'):
        return True

    return False

def safe_extract_member(tar: tarfile.TarFile, member: tarfile.TarInfo, target_dir: str, target_path: str):
    """
    Extract a single member to target_path, creating parent directories as needed.
    Returns True if a regular file was extracted (for .gitignore tracking).
    """
    parent_dir = os.path.dirname(target_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    if member.isreg():
        with tar.extractfile(member) as src, open(target_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
        # Preserve permission bits (optional)
        os.chmod(target_path, member.mode)
        return True  # Regular file extracted
    elif member.isdir():
        os.makedirs(target_path, exist_ok=True)
        return False
    else:
        # Symlinks, devices, etc. – skip silently
        return False

def update_gitignore(script_dir: str, extracted_files: list):
    """
    Append each extracted file (relative path from script_dir) to .gitignore
    if not already listed.
    """
    gitignore_path = os.path.join(script_dir, ".gitignore")
    existing_entries = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    existing_entries.add(stripped)

    new_entries = [f for f in extracted_files if f not in existing_entries]
    if not new_entries:
        info("All extracted/downloaded files are already listed in .gitignore.")
        return

    with open(gitignore_path, "a", encoding="utf-8") as f:
        if os.path.getsize(gitignore_path) == 0:
            f.write("# Downloaded ciadslides files and extra sty files (auto-generated)\n")
        else:
            f.write("\n# Downloaded ciadslides files and extra sty files (auto-generated)\n")
        for path in sorted(new_entries):
            git_entry = path.replace(os.sep, '/')
            f.write(f"{git_entry}\n")
        f.write("# End of auto-generated section\n")

    info(f"Added {len(new_entries)} file(s) to .gitignore")

def download_with_progress(url: str, dest_path: str):
    """
    Download a file from url to dest_path, showing a progress bar.
    """
    class ProgressHook:
        def __init__(self):
            self.total_size = 0
            self.downloaded = 0

        def __call__(self, count, block_size, total_size):
            if total_size == -1:
                return  # No total size given
            if self.total_size == 0:
                self.total_size = total_size
                sys.stdout.write(f"Downloading {os.path.basename(dest_path)}: 0% [{self.downloaded}/{self.total_size} bytes]\r")
                sys.stdout.flush()
            self.downloaded += block_size
            percent = int(100 * self.downloaded / self.total_size)
            sys.stdout.write(f"Downloading {os.path.basename(dest_path)}: {percent}% [{self.downloaded}/{self.total_size} bytes]\r")
            sys.stdout.flush()
            if self.downloaded >= self.total_size:
                sys.stdout.write("\n")

    hook = ProgressHook()
    urllib.request.urlretrieve(url, dest_path, reporthook=hook)

def remove_ciadslides_folder(script_dir: str):
    """
    Remove the 'ciadslides' subfolder (if it exists) and all its contents.
    """
    target_folder = os.path.join(script_dir, "ciadslides")
    if os.path.exists(target_folder):
        try:
            shutil.rmtree(target_folder)
            info(f"Removed existing folder: {target_folder}")
        except Exception as e:
            info(f"Warning: could not remove {target_folder}: {e}")

def download_extra_sty_files(script_dir: str) -> list:
    """
    Download each extra .sty file into script_dir. Returns list of relative paths
    (just filenames) of successfully downloaded files.
    """
    downloaded = []
    for sty in EXTRA_STY_FILES:
        dest = os.path.join(script_dir, sty["filename"])
        info(f"Downloading {sty['url']} ...")
        try:
            download_with_progress(sty["url"], dest)
            downloaded.append(sty["filename"])
            info(f"  Saved to {dest}")
        except Exception as e:
            info(f"  Warning: could not download {sty['filename']}: {e}")
    return downloaded

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    info(f"Target directory: {script_dir}")

    temp_file = None
    extracted_rel_paths = []

    try:
        # 1. Download the main archive
        info(f"Downloading main archive from {BEAMER_ARCHIVE_URL} ...")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz")
        temp_file.close()
        download_with_progress(BEAMER_ARCHIVE_URL, temp_file.name)

        # 2. Extract only the desired content from the archive
        info(f"Extracting contents of '{TARGET_TOP_DIR}' (excluding .tex/.md files and '{SKIP_SUBDIR}') into {script_dir} ...")
        with tarfile.open(temp_file.name, "r:gz") as tar:
            extracted_count = 0
            for member in tar.getmembers():
                if not member.name.startswith(TARGET_TOP_DIR):
                    continue
                if member.name == TARGET_TOP_DIR.rstrip('/'):
                    continue
                if should_skip(member.name):
                    info(f"  Skipped: {member.name}")
                    continue

                rel_path = member.name[len(TARGET_TOP_DIR):]
                if not rel_path:
                    continue

                target_path = os.path.join(script_dir, rel_path)
                if not os.path.realpath(target_path).startswith(os.path.realpath(script_dir)):
                    info(f"  Skipping unsafe path: {rel_path}")
                    continue

                was_file = safe_extract_member(tar, member, script_dir, target_path)
                if was_file:
                    extracted_rel_paths.append(rel_path)
                extracted_count += 1
                info(f"  Extracted: {rel_path}")

            if extracted_count == 0:
                info("Warning: No files were extracted from the archive (all were skipped or not found).")
            else:
                info(f"Extracted {extracted_count} items ({len(extracted_rel_paths)} regular files).")

        # 3. Download the extra .sty files
        extra_files = download_extra_sty_files(script_dir)
        extracted_rel_paths.extend(extra_files)

        # 4. Update .gitignore
        if extracted_rel_paths:
            update_gitignore(script_dir, extracted_rel_paths)
        else:
            info("No files were downloaded/extracted – nothing to add to .gitignore.")

        info("All operations completed successfully.")

    except urllib.error.URLError as e:
        error(f"Network error: {e}")
    except tarfile.TarError as e:
        error(f"Archive error: {e}")
    except Exception as e:
        error(f"Unexpected error: {e}")
    finally:
        # Clean up temporary archive file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
            info("Temporary archive file removed.")
        # Remove any leftover ciadslides/ folder
        remove_ciadslides_folder(script_dir)

if __name__ == "__main__":
    main()