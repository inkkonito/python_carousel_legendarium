#!/usr/bin/env python3

"""
Legendarium Carousel Pipeline

Run this single script from the project folder:

    python3 run.py

Pipeline:

1. Generate content_.json from raw.txt
2. Generate image_prompt.txt from content_.json
3. Display the exact instructions for the image-research step

The image-research step is performed manually using ChatGPT/Work.

It must:

- search every carousel slide
- find exactly one real existing Tolkien artwork per slide
- display the selected image
- download the selected images
- name them 0.jpg, 1.jpg, 2.jpg, etc.
- keep the numbering aligned with slide order
- create content.json as a copy of content_.json
- add the verified artist/author to every slide's credit field
- make sure each credit matches the downloaded artwork

After the image-research step:

4. Run add_text.py
5. Review the generated carousel
6. Run archive_iteration.py

The archive step:

- moves images/* → published/YYMMDD[_N]/
- copies content.json → published/YYMMDD[_N]/content.json
- moves output/* → src_archive/YYMMDD[_N]/
- copies raw.txt → src_archive/YYMMDD[_N]/raw.txt
- resets content.json to an empty file
- resets raw.txt to an empty file
- leaves images/ empty
- leaves output/ empty

If an archive folder already exists, the script automatically uses:

    YYMMDD
    YYMMDD_1
    YYMMDD_2
    ...

The same suffix is used for both published/ and src_archive/.
"""

import subprocess
import sys
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CONTENT_SCRIPT = BASE_DIR / "generate_content_.py"
IMAGE_PROMPT_SCRIPT = BASE_DIR / "generate_image_research_prompt.py"
ADD_TEXT_SCRIPT = BASE_DIR / "add_text.py"
ARCHIVE_SCRIPT = BASE_DIR / "archive_iteration.py"

RAW_FILE = BASE_DIR / "../txt/raw.txt"
CONTENT_FILE = BASE_DIR / "../json/content.json"
IMAGE_PROMPT_FILE = BASE_DIR / "../txt/image_prompt.txt"

IMAGES_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"


# ============================================================
# Run another Python script
# ============================================================

def run_script(script_path):
    print()
    print("=" * 60)
    print(f"Running: {script_path.name}")
    print("=" * 60)
    print()

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
    )

    if result.returncode != 0:
        print()
        print("=" * 60)
        print(f"FAILED: {script_path.name}")
        print("=" * 60)
        print(f"Process exited with code {result.returncode}.")
        return False

    print()
    print(f"Completed: {script_path.name}")

    return True


# ============================================================
# Check required scripts
# ============================================================

def check_required_scripts():
    missing = []

    for file_path in (
        CONTENT_SCRIPT,
        IMAGE_PROMPT_SCRIPT,
        ADD_TEXT_SCRIPT,
        ARCHIVE_SCRIPT,
    ):
        if not file_path.exists():
            missing.append(file_path.name)

    if missing:
        print(
            "ERROR: Missing required script(s): "
            + ", ".join(missing),
            file=sys.stderr,
        )
        sys.exit(1)


# ============================================================
# Check generated files
# ============================================================

def check_file_exists(file_path):
    if not file_path.exists():
        print(
            f"ERROR: {file_path.name} was not created.",
            file=sys.stderr,
        )
        sys.exit(1)


# ============================================================
# Print image research instructions
# ============================================================

def print_image_research_instructions():

    print()
    print("=" * 60)
    print("PIPELINE READY FOR IMAGE RESEARCH")
    print("=" * 60)
    print()

    print("Generated:")
    print(f"  ✓ {CONTENT_FILE.name}")
    print(f"  ✓ {IMAGE_PROMPT_FILE.name}")

    print()

    print("IMAGE RESEARCH")
    print("-----------------------------")
    print()
    print("Now copy image_prompt.txt and paste it into ChatGPT/Work.")
    print()
    print("The image-research step must:")
    print()
    print("  1. Search EVERY slide, including the intro.")
    print()
    print("  2. Find EXACTLY ONE real existing Tolkien artwork")
    print("     per slide.")
    print()
    print("  3. Display the selected image.")
    print()
    print("  4. Verify the artwork attribution.")
    print()
    print("  5. Download the selected images.")
    print()
    print("  6. Save them in slide order as:")
    print()
    print("       0.jpg  → Slide 1")
    print("       1.jpg  → Slide 2")
    print("       2.jpg  → Slide 3")
    print("       ...")
    print()
    print("  7. Create content.json from content_.json.")
    print()
    print("  8. Keep content_.json unchanged.")
    print()
    print("  9. Add the VERIFIED artist/author to every slide's")
    print("     'credit' field in content.json.")
    print()
    print(" 10. Make sure each credit matches the downloaded image.")
    print()
    print("IMPORTANT:")
    print("  Do not use AI-generated images.")
    print("  Use real existing Tolkien artwork.")
    print()


# ============================================================
# Print post-research instructions
# ============================================================

def print_post_research_instructions():

    print()
    print("=" * 60)
    print("IMAGE RESEARCH COMPLETE")
    print("=" * 60)
    print()

    print("Before continuing, make sure:")
    print()
    print("  ✓ images/ contains one image per slide")
    print("  ✓ Images are numbered in slide order")
    print("  ✓ content.json exists")
    print("  ✓ Every slide has a verified credit")
    print()
    print("Then run:")
    print()
    print("    python3 add_text.py")
    print()
    print("This will generate the final carousel in:")
    print()
    print("    output/")
    print()
    print("Review the generated carousel before archiving it.")
    print()
    print("When everything is correct, run:")
    print()
    print("    python3 archive_iteration.py")
    print()
    print("The archive script will:")
    print()
    print("  • Move images/* → published/YYMMDD[_N]/")
    print("  • Copy content.json → published/YYMMDD[_N]/")
    print("  • Move output/* → src_archive/YYMMDD[_N]/")
    print("  • Copy raw.txt → src_archive/YYMMDD[_N]/")
    print("  • Reset content.json")
    print("  • Reset raw.txt")
    print("  • Leave images/ empty")
    print("  • Leave output/ empty")
    print()
    print("The project will then be ready for the next carousel.")
    print()


# ============================================================
# Main
# ============================================================

def main():

    check_required_scripts()

    print()
    print("=" * 60)
    print("LEGENDARIUM CAROUSEL PIPELINE")
    print("=" * 60)
    print()

    print("Step 1 → Generate content_.json")
    print("Step 2 → Generate image_prompt.txt")
    print("Step 3 → Research and download real Tolkien artwork")
    print("Step 4 → Run add_text.py")
    print("Step 5 → Review the carousel")
    print("Step 6 → Archive the iteration")
    print()

    # --------------------------------------------------------
    # Step 1
    # --------------------------------------------------------

    print("=" * 60)
    print("STEP 1 — GENERATE CONTENT")
    print("=" * 60)

    if not run_script(CONTENT_SCRIPT):
        print()
        print("Pipeline stopped.")
        sys.exit(1)

    check_file_exists(CONTENT_FILE)

    # --------------------------------------------------------
    # Step 2
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 2 — GENERATE IMAGE RESEARCH PROMPT")
    print("=" * 60)

    if not run_script(IMAGE_PROMPT_SCRIPT):
        print()
        print("Pipeline stopped.")
        sys.exit(1)

    check_file_exists(IMAGE_PROMPT_FILE)

    # --------------------------------------------------------
    # Step 3
    # --------------------------------------------------------

    print_image_research_instructions()

    # --------------------------------------------------------
    # Stop here.
    #
    # Image research is performed manually using ChatGPT/Work.
    # --------------------------------------------------------

    print("run.py has finished.")
    print()
    print("Continue with the image-research step above.")
    print()
    print("After image research:")
    print("    python3 add_text.py")
    print()
    print("After reviewing the carousel:")
    print("    python3 archive_iteration.py")
    print()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print()
        print("Pipeline cancelled.")
        sys.exit(130)

    except Exception as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )
        sys.exit(1)