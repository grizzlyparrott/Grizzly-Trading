import os
import re
import json
from pathlib import Path

# --- CONFIG ---
ROOT_DIR = Path(__file__).parent.resolve()

# Only index HTML files inside these folders (relative to root)
ALLOWED_DIRS = {
    "futures-basics",
    "prop-firm-trading",
    "platforms-tutorials",
    "market-basics",
}

OUTPUT_FILE = ROOT_DIR / "search-index.json"


def is_allowed_html(path: Path) -> bool:
    # Must be .html and inside one of the allowed dirs
    if path.suffix.lower() != ".html":
        return False

    # Get parts relative to root: ["futures-basics", "some-article.html"]
    rel_parts = path.relative_to(ROOT_DIR).parts
    if not rel_parts:
        return False

    # First folder name decides if we include it
    first_part = rel_parts[0]
    return first_part in ALLOWED_DIRS


def extract_title_and_description(html: str):
    # Find <title>...</title>
    title_match = re.search(
        r"<title>\s*(.*?)\s*</title>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    title = title_match.group(1).strip() if title_match else ""

    # Find <meta name="description" content="...">
    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    description = desc_match.group(1).strip() if desc_match else ""

    return title, description


def main():
    entries = []

    for root, dirs, files in os.walk(ROOT_DIR):
        for fname in files:
            path = Path(root) / fname

            if not is_allowed_html(path):
                continue

            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    html = f.read()
            except Exception as e:
                print(f"Skipping {path} (read error: {e})")
                continue

            title, description = extract_title_and_description(html)

            # Build URL path like "/futures-basics/my-article.html"
            rel = path.relative_to(ROOT_DIR)
            url = "/" + str(rel).replace(os.sep, "/")

            # Category = first folder name (nicer label)
            parts = rel.parts
            category_folder = parts[0] if parts else ""
            category_map = {
                "futures-basics": "Futures Basics",
                "prop-firm-trading": "Prop Firm Trading",
                "platforms-tutorials": "Platforms & Tutorials",
                "market-basics": "Market Basics",
            }
            category = category_map.get(category_folder, category_folder)

            entry = {
                "title": title,
                "url": url,
                "description": description,
                "category": category,
            }
            entries.append(entry)

    # Sort alphabetically by title so it is stable
    entries.sort(key=lambda x: x["title"].lower())

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(entries)} entries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
