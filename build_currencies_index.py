# build_currencies_index.py
# Run from repo root:  python build_currencies_index.py
# Requirements:
# 1) currencies/index.html must contain these markers INSIDE the <div class="grid grid-3">:
#    <!-- CARDS:AUTOGEN:START -->
#    <!-- CARDS:AUTOGEN:END -->
# 2) Currency articles are in /futures-basics and filenames start with 6a-, 6b-, 6c-, 6e-, 6j-, 6m-, 6n-, 6s-, 6z-.

import re
from pathlib import Path
from html import unescape

ROOT = Path(".").resolve()

FUTURES_DIR = ROOT / "futures-basics"
CURRENCIES_INDEX = ROOT / "currencies" / "index.html"

SITE = "https://grizzlyparrottrading.com"
HUB_PATH = "/futures-basics"

# Add/remove prefixes here if you want more/less included.
PREFIXES = ("6a-", "6b-", "6c-", "6e-", "6j-", "6m-", "6n-", "6s-", "6z-")

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
        desc = "Currency futures breakdown and trading behavior."

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

    if not CURRENCIES_INDEX.exists():
        raise SystemExit(f"Missing index file: {CURRENCIES_INDEX}")

    # Collect matching articles by filename prefix
    files = []
    for p in FUTURES_DIR.glob("*.html"):
        if p.name.lower().startswith(PREFIXES):
            files.append(p)

    if not files:
        raise SystemExit(
            "No matching currency files found in /futures-basics.\n"
            f"Expected filenames starting with: {', '.join(PREFIXES)}"
        )

    files.sort(key=lambda x: x.name.lower())

    # Build cards
    cards = []
    for p in files:
        html = read_text_auto(p)
        title, desc = extract_title_and_desc(html)

        # Link is always the real served path under /futures-basics
        href = f"{HUB_PATH}/{p.name}"

        # Optional sanity check: if file still references /market-basics anywhere, warn (doesn't stop build)
        if f"{SITE}/market-basics/" in html:
            print(f"WARNING: {p.name} still contains '{SITE}/market-basics/' somewhere (likely breadcrumbs).")

        cards.append(build_card(href, title, desc))

    # Inject into currencies/index.html between markers
    index_html = read_text_auto(CURRENCIES_INDEX)

    if START_MARKER not in index_html or END_MARKER not in index_html:
        raise SystemExit(
            "Markers not found in currencies/index.html.\n"
            "Add these inside your <div class=\"grid grid-3\">:\n"
            f"{START_MARKER}\n{END_MARKER}"
        )

    new_block = START_MARKER + "\n\n" + "".join(cards) + "        " + END_MARKER
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    updated = pattern.sub(new_block, index_html, count=1)

    CURRENCIES_INDEX.write_text(updated, encoding="utf-8")

    print(f"Built {len(files)} currency cards into {CURRENCIES_INDEX}")

if __name__ == "__main__":
    main()
