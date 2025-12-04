import os
import re

# Folders to scan
content_dirs = [
    'futures-basics',
    'market-basics',
    'platforms-tutorials',
    'prop-firm-trading'
]

# Regex: capture ANY substring ending in .html, 10–20 chars long,
# and check if it appears twice in the same line.
pattern = re.compile(r'([A-Za-z0-9\-\_]{5,20}\.html).*?\1')

total_hits = 0
total_files = 0

for folder in content_dirs:
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        match = pattern.search(line)
                        if match:
                            print(f'⚠️ Repeat found in {path} (line {i}):')
                            print(f'    → {line.strip()}')
                            print()
                            total_hits += 1
                            total_files += 1
                            break  # we only need to report the file once

print("\n🏁 SCAN COMPLETE")
print(f"📄 Files with repeated .html patterns: {total_files}")
print(f"🔁 Total repeat lines detected: {total_hits}")

