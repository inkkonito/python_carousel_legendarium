from pathlib import Path
from datetime import datetime
import shutil


# =========================
# Configuration
# =========================

IMAGES_DIR = Path("../images")
OUTPUT_DIR = Path("../output")

CONTENT_FILE = Path("../json/content.json")
RAW_FILE = Path("../txt/raw.txt")

PUBLISHED_DIR = Path("../published")
SRC_ARCHIVE_DIR = Path("../src")


# =========================
# Helpers
# =========================

def move_contents(source_dir: Path, destination_dir: Path):
    """Move everything inside source_dir into destination_dir."""

    if not source_dir.exists():
        print(f"⚠️ Source directory does not exist: {source_dir}")
        return

    destination_dir.mkdir(parents=True, exist_ok=True)

    items = list(source_dir.iterdir())

    if not items:
        print(f"ℹ️ {source_dir} is already empty.")
        return

    for item in items:
        destination = destination_dir / item.name

        if destination.exists():
            raise FileExistsError(
                f"Destination already contains: {destination}"
            )

        print(f"Moving: {item} → {destination}")
        shutil.move(str(item), str(destination))


def copy_file(source: Path, destination: Path):
    """Copy a file while preserving metadata."""

    if not source.exists():
        print(f"⚠️ File does not exist: {source}")
        return False

    if destination.exists():
        raise FileExistsError(
            f"Destination already contains: {destination}"
        )

    print(f"Copying: {source} → {destination}")
    shutil.copy2(source, destination)
    return True


# =========================
# Main
# =========================

def main():

    # Current date: YYMMDD
    date_folder = datetime.now().strftime("%y%m%d")

    # Find the first available suffix.
    # Example:
    #   260920
    #   260920_1
    #   260920_2
    #   ...
    suffix = 0

    while True:
        if suffix == 0:
            folder_name = date_folder
        else:
            folder_name = f"{date_folder}_{suffix}"

        published_destination = PUBLISHED_DIR / folder_name
        archive_destination = SRC_ARCHIVE_DIR / folder_name

        # Both folders must be available for the same iteration.
        if not published_destination.exists() and not archive_destination.exists():
            break

        suffix += 1

    print()
    print("=" * 60)
    print("ARCHIVING ITERATION")
    print("=" * 60)
    print(f"Date: {folder_name}")
    print()

    # -------------------------
    # Create archive folders
    # -------------------------

    published_destination.mkdir(parents=True, exist_ok=False)
    archive_destination.mkdir(parents=True, exist_ok=False)

    # -------------------------
    # Images → published
    # -------------------------

    print("📸 Archiving images...")
    move_contents(IMAGES_DIR, published_destination)

    # -------------------------
    # content.json → published
    # -------------------------

    print()
    print("📄 Archiving content.json...")
    copy_file(
        CONTENT_FILE,
        published_destination / CONTENT_FILE.name
    )

    # -------------------------
    # Output → src_archive
    # -------------------------

    print()
    print("🎨 Archiving output...")
    move_contents(OUTPUT_DIR, archive_destination)

    # -------------------------
    # raw.txt → src_archive
    # -------------------------

    print()
    print("📝 Archiving raw.txt...")

    raw_archived = copy_file(
        RAW_FILE,
        archive_destination / RAW_FILE.name
    )

    # -------------------------
    # Reset raw.txt
    # -------------------------

    if raw_archived:
        RAW_FILE.write_text("", encoding="utf-8")
        print("📝 Created new empty raw.txt")

    # -------------------------
    # Done
    # -------------------------

    print()
    print("=" * 60)
    print("✅ ARCHIVE COMPLETE")
    print("=" * 60)
    print()
    print(f"Published: {published_destination}")
    print(f"Source:    {archive_destination}")
    print()
    print("📸 images/      → empty")
    print("🎨 output/      → empty")
    print("📄 content.json → kept")
    print("📝 raw.txt      → reset to empty")
    print()
    print("Ready for the next iteration.")


if __name__ == "__main__":
    main()
