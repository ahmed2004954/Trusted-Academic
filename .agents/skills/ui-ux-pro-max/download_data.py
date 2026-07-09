#!/usr/bin/env python3
"""
Download all data files for UI/UX Pro Max skill from GitHub.
Run: python .agents/skills/ui-ux-pro-max/download_data.py
"""

import urllib.request
import os
import sys

BASE_URL = "https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
STACKS_DIR = os.path.join(DATA_DIR, "stacks")
SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "scripts")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STACKS_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Files to download
DATA_FILES = [
    "products.csv", "styles.csv", "colors.csv", "typography.csv",
    "landing.csv", "charts.csv", "ux-guidelines.csv", "motion.csv",
    "icons.csv", "design.csv", "ui-reasoning.csv", "google-fonts.csv",
    "react-performance.csv", "app-interface.csv", "draft.csv"
]

SCRIPT_FILES = [
    "search.py", "core.py", "design_system.py"
]

STACK_FILES = [
    "html-tailwind", "react", "nextjs", "astro", "vue", "nuxtjs", "nuxt-ui",
    "svelte", "swiftui", "react-native", "flutter", "shadcn", "jetpack-compose",
    "threejs", "angular", "laravel", "javafx", "wpf", "winui", "avalonia", "uno", "uwp"
]


def download_file(url, dest):
    """Download a file from URL to dest path"""
    try:
        urllib.request.urlretrieve(url, dest)
        size = os.path.getsize(dest)
        print(f"  ✓ {os.path.basename(dest)} ({size:,} bytes)")
        return True
    except Exception as e:
        print(f"  ✗ {os.path.basename(dest)}: {e}")
        return False


def main():
    print("=" * 60)
    print("UI/UX Pro Max Skill - Data Downloader")
    print("=" * 60)

    success = 0
    failed = 0

    # Download data files
    print(f"\nDownloading {len(DATA_FILES)} data files...")
    for f in DATA_FILES:
        url = f"{BASE_URL}/src/ui-ux-pro-max/data/{f}"
        dest = os.path.join(DATA_DIR, f)
        if download_file(url, dest):
            success += 1
        else:
            failed += 1

    # Download scripts (overwrite with originals from repo)
    print(f"\nDownloading {len(SCRIPT_FILES)} script files...")
    for f in SCRIPT_FILES:
        url = f"{BASE_URL}/src/ui-ux-pro-max/scripts/{f}"
        dest = os.path.join(SCRIPTS_DIR, f)
        if download_file(url, dest):
            success += 1
        else:
            failed += 1

    # Download stack-specific files
    print(f"\nDownloading stack-specific guides...")
    for stack in STACK_FILES:
        url = f"{BASE_URL}/src/ui-ux-pro-max/data/stacks/{stack}.csv"
        dest = os.path.join(STACKS_DIR, f"{stack}.csv")
        if download_file(url, dest):
            success += 1
        # Stack files may not all exist, don't count as failure

    print(f"\n{'=' * 60}")
    print(f"Download complete: {success} succeeded, {failed} failed")
    print(f"{'=' * 60}")

    # Quick verification
    print("\nVerifying installation...")
    try:
        sys.path.insert(0, SCRIPTS_DIR)
        from core import CSV_CONFIG
        print(f"  ✓ Core module loaded ({len(CSV_CONFIG)} domains configured)")

        # Check data files exist
        existing = [f for f in DATA_FILES if os.path.exists(os.path.join(DATA_DIR, f))]
        print(f"  ✓ Data files present: {len(existing)}/{len(DATA_FILES)}")

        if existing:
            print(f"\n  Skill is ready! Try:")
            print(f'  python {os.path.join(SCRIPTS_DIR, "search.py")} "modern dashboard" --domain style')
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")


if __name__ == "__main__":
    main()
