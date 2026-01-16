# build_metals_index_from_search.py
# Run from repo root: python build_metals_index_from_search.py
# Reads search-index.json, tries to identify METALS-primary pages, writes cards into /metals/index.html between markers,
# and prints the final count. If count != 100, we iterate the heuristics.

import json
import re
from pathlib import Path

ROOT = Path(".").resolve()
SEARCH_INDEX = ROOT / "search-index.json"
METALS_INDEX = ROOT / "metals" / "index.html"

START_MARKER = "<!-- CARDS:AUTOGEN:START -->"
END_MARKER = "<!-- CARDS:AUTOGEN:END -->"

# Metals signals
METAL_TICKERS = {"gc", "si", "hg", "pl", "pa"}
METAL_WORDS = {"gold", "silver", "copper", "platinum", "palladium"}

# Non-metals instrument signals that commonly cause false positives (correlation / cross-market pages)
# Expand this list if needed after first run.
NON_METAL_TICKERS = {
    "6a", "6b", "6c", "6e", "6j", "6m", "6n", "6s", "6z",
    "cl", "ng", "rb", "ho",
    "es", "nq", "ym", "rty",
    "zb", "zn", "zf", "zt",
    "le", "gf", "he",
    "zq", "sr3",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")

def load_search_index(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("pages", "items", "documents", "data", "index"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise SystemExit("search-index.json format not recognized (expected a list or a dict containing a list).")

def get_field(item, *keys, default=""):
    for k in keys:
        if k in item and isinstance(item[k], str):
            return item[k]
    return default

def tokens(s: str):
    return set(TOKEN_RE.findall(s.lower()))

def is_futures_basics_url(url: str) -> bool:
    # Only classify pages that actually live under /futures-basics/
    return "/futures-basics/" in url

def is_metals_primary(title: str, url: str, desc: str, content: str) -> bool:
    # We intentionally do NOT rely on "starts with".
    # We require: futures-basics URL AND strong metal signal in title/slug,
    # and we reject: obvious cross-market pages with multiple other tickers in title/slug.
    t = (title or "").lower()
    u = (url or "").lower()
    d = (desc or "").lower()

    # Strong signal should appear in title OR slug, not just deep body content.
    strong = tokens(t) | tokens(u)
    has_metal = bool((strong & METAL_TICKERS) or (strong & METAL_WORDS))

    if not has_metal:
        # allow one fallback: metal word in description if title/slug is generic "how/why"
        desc_tokens = tokens(d)
        has_metal = bool(desc_tokens & METAL_WORDS)

    if not has_metal:
        return False

    # Reject if it looks like a comparison/correlation cross-market piece.
    # Heuristic: title/slug contains metal + at least 2 non-metal tickers OR contains explicit compare words.
    nonmetal_hits = len(strong & NON_METAL_TICKERS)
    compare_words = {"vs", "versus", "correlation", "correlated", "relationship", "spread", "pairs", "cross"}
    looks_compare = bool(tokens(t) & compare_words) or bool(tokens(u) & compare_words)

    # If it has lots of other tickers AND looks like a compare page, reject.
    if looks_compare and nonmetal_hits >= 1:
        return False

    # If it contains 2+ other tickers in title/slug, it's almost certainly not metals-primary.
    if nonmetal_hits >= 2:
        return False

    return True

def build_card(url: str, title: str, desc: str) -> str:
    safe_title = (title or "Untitled").strip()
    safe_desc = (desc or "Metal futures breakdown and trading behavior.").strip()
    return (
        '        <article class="card">\n'
        f'          <h3><a href="{url}">{safe_title}</a></h3>\n'
        f"          <p>{safe_desc}</p>\n"
        "        </article>\n\n"
    )

def inject_cards(index_html: str, cards_html: str) -> str:
    if START_MARKER not in index_html or END_MARKER not in index_html:
        raise SystemExit(
            "Markers not found in metals/index.html. Add these inside your <div class=\"grid grid-3\">:\n"
            f"{START_MARKER}\n{END_MARKER}"
        )
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    new_block = START_MARKER + "\n\n" + cards_html + "        " + END_MARKER
    return pattern.sub(new_block, index_html, count=1)

def main():
    if not SEARCH_INDEX.exists():
        raise SystemExit("Missing search-index.json in repo root.")
    if not METALS_INDEX.exists():
        raise SystemExit("Missing metals/index.html.")

    items = load_search_index(SEARCH_INDEX)

    picked = []
    for item in items:
        if not isinstance(item, dict):
            continue

        url = get_field(item, "url", "href", "path", default="")
        title = get_field(item, "title", "name", default="")
        desc = get_field(item, "description", "desc", "summary", default="")
        content = get_field(item, "content", "text", "body", default="")

        if not url:
            continue
        if not is_futures_basics_url(url):
            continue

        if is_metals_primary(title, url, desc, content):
            picked.append((url, title, desc))

    picked.sort(key=lambda x: x[0].lower())

    cards = "".join(build_card(url, title, desc) for (url, title, desc) in picked)

    index_html = METALS_INDEX.read_text(encoding="utf-8")
    updated = inject_cards(index_html, cards)
    METALS_INDEX.write_text(updated, encoding="utf-8")

    # Write a plain list so you can eyeball outliers fast
    (ROOT / "metals-picked-urls.txt").write_text("\n".join(url for url, _, _ in picked) + "\n", encoding="utf-8")

    print(f"Metals candidates written: {len(picked)}")
    print("Also wrote metals-picked-urls.txt")

if __name__ == "__main__":
    main()
