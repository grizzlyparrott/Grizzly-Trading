import re
import json
import os

# === Load the search index
with open('search-index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

# Build a lookup: "filename.html" → "Article Title"
title_lookup = {}
for entry in index:
    url = entry['url'].strip('/')
    filename = os.path.basename(url)
    title_lookup[filename] = entry['title']

# === Folders to scan in your repo
content_dirs = [
    'futures-basics',
    'market-basics',
    'platforms-tutorials',
    'prop-firm-trading'
]

# === Regex to catch sloppy links like:
# <a href="something.html">something.html</a>
# EVEN if attributes are weird, spaced out, or uppercase.
pattern = re.compile(
    r'<a\s+[^>]*href=["\']([^"\']+\.html)["\'][^>]*>\s*\1\s*</a>',
    re.IGNORECASE
)

# === DRY RUN: We do NOT write changes yet.
total_files = 0
total_links = 0

for folder in content_dirs:
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    html = f.read()

                matches = list(pattern.finditer(html))
                if matches:
                    print(f"👀 Would fix in: {path}")
                    total_files += 1

                    for m in matches:
                        filename = m.group(1)
                        title = title_lookup.get(filename)

                        if title:
                            print(f"   🔗 {filename}  →  {title}")
                            total_links += 1
                        else:
                            print(f"   ⚠️ {filename} — NO TITLE FOUND in search-index.json")

print("\n🏁 DRY RUN COMPLETE")
print(f"📄 Files flagged: {total_files}")
print(f"🔗 Total broken links found: {total_links}")
