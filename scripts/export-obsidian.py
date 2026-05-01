#!/usr/bin/env python3
"""
Export all converted articles from history.json to Obsidian vault.

Usage:
    python3 scripts/export-obsidian.py

Output:
    ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Laban/YouTube-Articles/
    Each file: YAML frontmatter (title, source, date) + full Markdown article.
    Overwrites existing files with the same sanitized filename.
"""

import json, os, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")
OBSIDIAN_DIR = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Laban/YouTube-Articles"
)


def sanitize_filename(title, max_len=80):
    """Remove special chars, keep CJK + alphanumeric, truncate at word boundary."""
    name = re.sub(r'[^\w\s\-\.\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', '', title)
    name = re.sub(r'\s+', ' ', name).strip()
    if len(name) > max_len:
        name = name[:max_len].rsplit(' ', 1)[0]
    return name + '.md'


def main():
    if not os.path.exists(HISTORY_FILE):
        print(f"History file not found: {HISTORY_FILE}")
        return 1

    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)

    os.makedirs(OBSIDIAN_DIR, exist_ok=True)
    existing = set(os.listdir(OBSIDIAN_DIR))

    exported = 0
    for item in history:
        title = item.get("title", "untitled")
        article = item.get("article", "")
        fname = sanitize_filename(title)
        fpath = os.path.join(OBSIDIAN_DIR, fname)

        content = f"---\ntitle: \"{title}\"\nsource: \"{item.get('url', '')}\"\ndate: \"{item.get('date', '')}\"\n---\n\n{article}"

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)

        status = "overwritten" if fname in existing else "new"
        print(f"  [{status:>10}] {fname}")
        exported += 1

    print(f"\nExported {exported} articles to:\n  {OBSIDIAN_DIR}")
    return 0


if __name__ == "__main__":
    exit(main())
