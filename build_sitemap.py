import os

# Your live domain
BASE_URL = "https://grizzlyparrottrading.com"

# Automatically use the folder this script is in as the site root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

urls = set()

for root, dirs, files in os.walk(ROOT_DIR):
    for filename in files:
        # Skip non-HTML and the 404 page
        if not filename.lower().endswith(".html"):
            continue
        if filename.lower() == "404.html":
            continue

        full_path = os.path.join(root, filename)
        rel_path = os.path.relpath(full_path, ROOT_DIR)
        rel_url = rel_path.replace(os.sep, "/")

        # Root index.html -> "/"
        if rel_url.lower() == "index.html":
            loc = BASE_URL + "/"
        else:
            loc = BASE_URL + "/" + rel_url

        urls.add(loc)

sitemap_path = os.path.join(ROOT_DIR, "sitemap.xml")

with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for loc in sorted(urls):
        f.write("  <url>\n")
        f.write("    <loc>{}</loc>\n".format(loc))
        f.write("  </url>\n")
    f.write("</urlset>\n")

print("Written sitemap with {} URLs to {}".format(len(urls), sitemap_path))
