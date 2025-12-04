import os
import re

content_dirs = [
    'futures-basics',
    'market-basics',
    'platforms-tutorials',
    'prop-firm-trading'
]

# <a ... href="something.html" ...> ... .html ... </a>
pattern = re.compile(
    r'<a[^>]*href=(["\'])([^"\']+\.html)\1[^>]*>[^<]*\.html[^<]*</a>',
    re.IGNORECASE
)

total_files = 0
total_matches = 0

for folder in content_dirs:
    for root, _, files in os.walk(folder):
        for file in files:
            if not file.endswith('.html'):
                continue

            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        print(f'⚠️ Leftover bad link in {path} (line {i}):')
                        print(f'    {line.strip()}')
                        print()
                        total_files += 1
                        total_matches += 1
                        break  # one line per file is enough

print("\n🏁 SCAN COMPLETE")
print(f"📄 Files with leftover .html link text: {total_files}")
print(f"🔗 Total bad lines found: {total_matches}")
