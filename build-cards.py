import re
from pathlib import Path

ROOT = Path(__file__).parent

INDEX = ROOT / "futures-basics" / "index.html"
FOLDER = ROOT / "futures-basics"

GRID_RE = re.compile(r'<div class="grid grid-3">', re.IGNORECASE)
LINK_RE = re.compile(r'<a href="([^"]+\.html)"')
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DESC_RE = re.compile(r'<meta name="description" content="(.*?)"', re.IGNORECASE)

index_html = INDEX.read_text(encoding="utf-8")

# find existing article links already in cards
existing_links = set(LINK_RE.findall(index_html))

new_cards = []

# newest first based on file modified time
articles = sorted(
    [f for f in FOLDER.glob("*.html") if f.name != "index.html"],
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

for file in articles:
    if file.name in existing_links:
        continue

    html = file.read_text(encoding="utf-8")

    title_match = TITLE_RE.search(html)
    desc_match = DESC_RE.search(html)

    if not title_match or not desc_match:
        continue

    title = title_match.group(1).strip()
    desc = desc_match.group(1).strip()

    card = f'''
<article class="card">
  <h3><a href="{file.name}">{title}</a></h3>
  <p>{desc}</p>
</article>
'''

    new_cards.append(card)

if new_cards:
    insert_position = GRID_RE.search(index_html).end()

    index_html = (
        index_html[:insert_position]
        + "\n".join(new_cards)
        + index_html[insert_position:]
    )

    INDEX.write_text(index_html, encoding="utf-8")
    print(f"Added {len(new_cards)} new cards.")
else:
    print("No new cards needed.")