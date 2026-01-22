from pathlib import Path

# Auto-root: the folder where this script lives (your repo root)
SITE_ROOT = Path(__file__).resolve().parent

# Folder to scan
SCAN_DIR = SITE_ROOT / "futures-basics"

# Output file
OUTPUT_FILE = SITE_ROOT / "_slug_lists" / "gc-pages.txt"

# Filter: filename must include one of these
KEYWORDS = ("gc", "gold")

INCLUDE_INDEX = False


def main():
    if not SCAN_DIR.exists():
        # Show you what folders DO exist so you can spot the real name
        dirs = sorted([p.name for p in SITE_ROOT.iterdir() if p.is_dir()])
        raise RuntimeError(
            f"Folder not found: {SCAN_DIR}\n"
            f"Repo root detected as: {SITE_ROOT}\n"
            f"Top-level folders here: {dirs}\n"
            f"If your folder is named differently, change SCAN_DIR to match."
        )

    pages = []
    for file in SCAN_DIR.glob("*.html"):
        name = file.name.lower()

        if not INCLUDE_INDEX and name == "index.html":
            continue

        if any(k in name for k in KEYWORDS):
            slug = "/" + file.relative_to(SITE_ROOT).as_posix()
            pages.append(slug)

    pages.sort()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(pages) + ("\n" if pages else ""), encoding="utf-8")

    print(f"Wrote {len(pages)} GC pages to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
