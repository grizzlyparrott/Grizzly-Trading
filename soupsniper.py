from bs4 import BeautifulSoup
import os
import json

# Load titles from your search index
with open('search-index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

title_lookup = {}
for entry in index:
    url = entry['url'].strip('/')
    filename = os.path.basename(url)
    title_lookup[filename] = entry['title']

# Folders to scan
content_dirs = [
    'futures-basics',
    'market-basics',
    'platforms-tutorials',
    'prop-firm-trading'
]

# Allow common short link texts
safe_link_texts = {"Home", "Back", "More", "Next", "Previous", "Index", "Learn more"}

total_files = 0
total_fixes = 0

for folder in content_dirs:
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    html = f.read()

                soup = BeautifulSoup(html, 'lxml')
                links = soup.find_all('a')

                changes = 0

                for tag in links:
                    href = tag.get('href')
                    if not href or not href.endswith('.html'):
                        continue

                    filename = os.path.basename(href)
                    expected_title = title_lookup.get(filename)

                    if expected_title:
                        visible_text = tag.get_text(strip=True)

                        if visible_text != expected_title and visible_text not in safe_link_texts:
                            print(f'🧼 Would fix in: {path}')
                            print(f'    href="{href}" | was: "{visible_text}" → should be: "{expected_title}"')
                            changes += 1

                if changes > 0:
                    total_files += 1
                    total_fixes += changes

print('\n✅ DRY RUN COMPLETE')
print(f'📄 Files flagged: {total_files}')
print(f'🔗 Total broken link texts found: {total_fixes}')
