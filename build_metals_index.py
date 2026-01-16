# build_metals_index.py
# Run from repo root: python build_metals_index.py
# Scans /futures-basics for metal articles and writes cards into /metals/index.html between markers.

import re
from pathlib import Path
from html import unescape

ROOT = Path(".").resolve()

FUTURES_DIR = ROOT / "futures-basics"
METALS_INDEX = ROOT / "metals" / "index.html"

HUB_PATH = "/futures-basics"

# Metal prefixes by filename
PREFIXES = ("gc-", "si-", "hg-", "pl-", "pa-")

START_MARKER = "<!-- CARDS:AUTOGEN:START -->"
END_MARKER = "<!-- CARDS:AUTOGEN:END -->"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
    re.IGNORECASE | re.DOTALL
)
TAG_RE = re.compile(r"<[^>]+>")

def read_text_auto(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")

def strip_tags(s: str) -> str:
    s = unescape(s)
    s = TAG_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_title_and_desc(html: str) -> tuple[str, str]:
    title = ""
    desc = ""

    m = TITLE_RE.search(html)
    if m:
        title = strip_tags(m.group(1)).replace(" | Grizzly Parrot Trading", "").strip()

    m = DESC_RE.search(html)
    if m:
        desc = strip_tags(m.group(1))

    if not title:
        title = "Untitled"
    if not desc:
        desc = "Metal futures breakdown and trading behavior."

    return title, desc

def build_card(href: str, title: str, desc: str) -> str:
    return (
        '        <article class="card">\n'
        f'          <h3><a href="{href}">{title}</a></h3>\n'
        f"          <p>{desc}</p>\n"
        "        </article>\n\n"
    )

def main() -> None:
    if not FUTURES_DIR.exists():
        raise SystemExit(f"Missing folder: {FUTURES_DIR}")

    if not METALS_INDEX.exists():
        raise SystemExit(f"Missing index file: {METALS_INDEX}")

    files = []
    for p in FUTURES_DIR.glob("*.html"):
        if p.name.lower().startswith(PREFIXES):
            files.append(p)

    if not files:
        raise SystemExit(
            "No matching metal files found in /futures-basics.\n"
            f"Expected filenames starting with: {', '.join(PREFIXES)}"
        )

    files.sort(key=lambda x: x.name.lower())

    cards = []
    for p in files:
        html = read_text_auto(p)
        title, desc = extract_title_and_desc(html)
        href = f"{HUB_PATH}/{p.name}"
        cards.append(build_card(href, title, desc))

    index_html = read_text_auto(METALS_INDEX)

    if START_MARKER not in index_html or END_MARKER not in index_html:
        raise SystemExit(
            "Markers not found in metals/index.html.\n"
            "Add these inside your <div class=\"grid grid-3\">:\n"
            f"{START_MARKER}\n{END_MARKER}"
        )

    new_block = START_MARKER + "\n\n" + "".join(cards) + "        " + END_MARKER
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    updated = pattern.sub(new_block, index_html, count=1)

    METALS_INDEX.write_text(updated, encoding="utf-8")
    print(f"Built {len(files)} metal cards into {METALS_INDEX}")

if __name__ == "__main__":
    main()
