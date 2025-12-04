import os
import re

# Folders to scan – same as your content dirs
content_dirs = [
    'futures-basics',
    'market-basics',
    'platforms-tutorials',
    'prop-firm-trading'
]

# This is literally ".html" followed by anything, then another ".html"
pattern = re.compile(r'\.html.*\.html')

total_lines = 0
total_files = 0

for folder in content_dirs:
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        if pattern.search(line):
                            print(f'⚠️  Match in {path} (line {i}):')
                            print(f'    {line.strip()}')
                            print()
                            total_lines += 1
                            total_files += 1
                            break  # only report each file once

print("\n🏁 SCAN COMPLETE")
print(f"📄 Files with .html*.html pattern: {total_files}")
print(f"🔁 Total lines detected (1 per file): {total_lines}")
