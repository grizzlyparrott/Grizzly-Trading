import os
import re
import json

# --- Load titles from search-index.json ---
with open('search-index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

# Build lookup: filename.html -> "Article Title"
title_lookup = {}
for entry in index:
    url = entry['url'].strip('/')
    filename = os.path.basename(url)
    title_lookup[filename] = entry['title']

# --- Folders to scan ---
content_dirs = [
    'futures-basics',
    'market-basics',
    'platforms-tutorials',
    'prop-firm-trading'
]

# Pattern to find links whose visible text contains ".html"
pattern = re.compile(
    r'<a([^>]*?)href=(["\'])([^"\']+\.html)\2([^>]*)>([^<]*\.html[^<]*)</a>',
    re.IGNORECASE
)

total_files_changed = 0
total_links_fixed = 0

for folder in content_dirs:
    for root, _, files in os.walk(folder):
        for file in files:
            if not file.endswith('.html'):
                continue

            path = os.path.join(root, file)

            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()

            def replacer(match):
                # Use the outer variable without "nonlocal"
                global total_links_fixed

                before_attrs = match.group(1)
                quote = match.group(2)
                href = match.group(3)
                after_attrs = match.group(4)
                old_text = match.group(5)

                filename = os.path.basename(href)
                title = title_lookup.get(filename)

                if not title:
                    return match.group(0)

                total_links_fixed += 1
                return f'<a{before_attrs}href={quote}{href}{quote}{after_attrs}>{title}</a>'

            # Apply the replacer
            new_html, count = pattern.subn(replacer, html)

            if count > 0 and new_html != html:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                total_files_changed += 1
                print(f'✅ Fixed {count} link(s) in {path}')

print("\n🏁 DONE")
print(f"📄 Files changed: {total_files_changed}")
print(f"🔗 Total links fixed: {total_links_fixed}")
