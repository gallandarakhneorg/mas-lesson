#!/usr/bin/env python3
"""
Talk installer for LaTeX/Beamer presentations.

This script lists available talks or installs a specific talk's content into
the root TALK.tex file.

Usage:
    python3 talk_manager.py                 # list all talks
    python3 talk_manager.py --install <id> # install the talk with given id
    python3 talk_manager.py --help         # show this help
"""

import argparse
import os
import sys
import re
from pathlib import Path

# --- Configuration ---
TALKS_DIR = Path("talks")
TALK_TEX_FILE = Path("TALK.tex")

# --- Helper functions ---

def list_talks():
    """Print all available talk IDs (subdirectories of TALKS_DIR)."""
    if not TALKS_DIR.exists():
        print(f"Error: '{TALKS_DIR}' not found. Are you running from the project root?")
        return

    talk_dirs = [d.name for d in TALKS_DIR.iterdir() if d.is_dir()]
    if not talk_dirs:
        print("No talks found.")
    else:
        print("Available talks:")
        for tid in sorted(talk_dirs):
            print(f"  - {tid}")

def extract_latex_content(md_path):
    """
    Read the Markdown file and extract the content between triple backticks.
    If a fence is present, it may be ```latex or just ```.
    Returns the extracted content as a string, or None if no fences are found.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code = False
    content_lines = []
    fence_found = False

    for line in lines:
        # Detect start of fenced block: ``` or ```latex
        if re.match(r'^```(latex)?\s*$', line.strip()):
            in_code = True
            fence_found = True
            continue
        # Detect end of fenced block: ```
        if in_code and re.match(r'^```\s*$', line.strip()):
            in_code = False
            continue
        if in_code:
            content_lines.append(line)

    if not fence_found:
        return None

    # Join lines and strip trailing whitespace, but keep internal structure
    return ''.join(content_lines).rstrip('\n')

def install_talk(talk_id):
    """Install the talk with the given ID into TALK.tex."""
    talk_dir = TALKS_DIR / talk_id
    if not talk_dir.exists():
        print(f"Error: Talk directory '{talk_dir}' does not exist.")
        return False

    md_file = talk_dir / "TALK.md"
    if not md_file.exists():
        print(f"Error: '{md_file}' not found.")
        return False

    content = extract_latex_content(md_file)
    if content is None:
        print(f"Warning: No Markdown code fences found in {md_file}. Copying entire file as-is.")
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read().rstrip('\n')
    else:
        print(f"Extracted LaTeX content from {md_file}.")

    # Write to root TALK.tex
    try:
        with open(TALK_TEX_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully installed talk '{talk_id}' into {TALK_TEX_FILE}.")
        return True
    except Exception as e:
        print(f"Error writing to {TALK_TEX_FILE}: {e}")
        return False

# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Manage LaTeX/Beamer talks. Lists available talks by default."
    )
    parser.add_argument(
        "--install",
        metavar="TALK_ID",
        help="Install the talk with the given ID into TALK.tex"
    )
    args = parser.parse_args()

    if args.install:
        success = install_talk(args.install)
        sys.exit(0 if success else 1)
    else:
        list_talks()
        sys.exit(0)

if __name__ == "__main__":
    main()
