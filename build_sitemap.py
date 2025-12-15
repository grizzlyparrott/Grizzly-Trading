#!/usr/bin/env python3
# build_sitemap.py
# Generates sitemap.xml using each HTML file's canonical URL.
# Safe defaults: ignores common build/cache folders, dedupes URLs, skips canonicals ending in /index.html.

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urlunparse

BASE_URL = "https://grizzlyparrottrading.com"
OUTPUT_FILE = "sitemap.xml"

# Folders to skip while walking the repo
SKIP_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "site",
    ".jekyll-cache",
    ".sass-cache",
    ".cache",
    ".idea",
}

# Files to skip explicitly
SKIP_FILES = {
    "404.html",
}

CANONICAL_RE = re.compile(
    r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\'][^>]*>',
    re.IGNORECASE,
)

def norm_url(url: str) -> str:
    url = url.strip()
    p = urlparse(url)

    # If canonical is relative, resolve against BASE_URL
    if not p.scheme:
        # Ensure it starts with /
        path = url if url.startswith("/") else f"/{url}"
        p = urlparse(BASE_URL)
        url = urlunparse((p.scheme, p.netloc, path, "", "", ""))
        p = urlparse(url)

    # Force https and exact host from BASE_URL
    base = urlparse(BASE_URL)
    scheme = "https"
    netloc = base.netloc

    # Normalize path
    path = p.path or "/"
    # Collapse multiple slashes
    path = re.sub(r"/{2,}", "/", path)

    # Drop fragments/query for sitemap
    return urlunparse((scheme, netloc, path, "", "", ""))

def fallback_canonical_for_file(html_path: Path, repo_root: Path) -> str:
    rel = html_path.relative_to(repo_root).as_posix()

    # Root index.html => /
    if rel == "index.html":
        return f"{BASE_URL}/"

    # Hub index.html => /hub/
    if rel.endswith("/index.html"):
        hub = rel[: -len("/index.html")]
        return f"{BASE_URL}/{hub}/"

    # Regular html page => /path/file.html
    return f"{BASE_URL}/{rel}"

def find_canonical_in_html(text: str) -> str | None:
    m = CANONICAL_RE.search(text)
    if not m:
        return None
    return m.group(1).strip()

def iso_date_from_mtime(path: Path) -> str:
    # Google accepts date or datetime; keep it simple and stable (UTC date)
    ts = path.stat().st_mtime
    return time.strftime("%Y-%m-%d", time.gmtime(ts))

def should_skip_dir(dirname: str) -> bool:
    return dirname in SKIP_DIRS or dirname.startswith(".")

def main() -> int:
    repo_root = Path(__file__).resolve().parent

    urls: dict[str, str] = {}  # url -> lastmod
    scanned = 0
    used_fallback = 0
    missing_canonical = 0
    skipped_index_canonicals = 0

    for root, dirs, files in os.walk(repo_root):
        # prune dirs
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        root_path = Path(root)

        for fname in files:
            if not fname.lower().endswith(".html"):
                continue
            if fname in SKIP_FILES:
                continue

            html_path = root_path / fname

            # Skip files in hidden directories even if os.walk didn't prune (extra safety)
            if any(part.startswith(".") for part in html_path.relative_to(repo_root).parts):
                continue

            scanned += 1
            try:
                text = html_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            canonical = find_canonical_in_html(text)
            if canonical is None:
                missing_canonical += 1
                canonical = fallback_canonical_for_file(html_path, repo_root)
                used_fallback += 1

            canonical = norm_url(canonical)

            # If a page declares /index.html as canonical, that is not sitemap-worthy
            if canonical.endswith("/index.html"):
                skipped_index_canonicals += 1
                continue

            lastmod = iso_date_from_mtime(html_path)

            # Keep newest lastmod if duplicates happen
            if canonical in urls:
                if lastmod > urls[canonical]:
                    urls[canonical] = lastmod
            else:
                urls[canonical] = lastmod

    # Always ensure homepage exists in sitemap
    home = norm_url(f"{BASE_URL}/")
    if home not in urls:
        # best effort lastmod from root index.html if it exists
        idx = repo_root / "index.html"
        urls[home] = iso_date_from_mtime(idx) if idx.exists() else time.strftime("%Y-%m-%d", time.gmtime())

    out_path = repo_root / OUTPUT_FILE
    sorted_items = sorted(urls.items(), key=lambda x: x[0])

    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url, lastmod in sorted_items:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{url}</loc>")
        xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")
    out_path.write_text("\n".join(xml_lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUTPUT_FILE} with {len(sorted_items)} URLs.")
    print(f"Scanned HTML files: {scanned}")
    print(f"Missing canonical tags: {missing_canonical} (fallback used: {used_fallback})")
    print(f"Skipped canonicals ending in /index.html: {skipped_index_canonicals}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
