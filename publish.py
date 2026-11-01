import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
POSTS_DIR = BASE_DIR / "posts"
INDEX_FILE = BASE_DIR / "index.html"
SITEMAP_FILE = BASE_DIR / "sitemap.xml"
RSS_FILE = BASE_DIR / "rss.xml"

POST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Okan Yorulmaz</title>
  
  <meta name="description" content="{description}">
  <meta name="author" content="Okan Yorulmaz">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://yrlmz14.github.io/posts/{slug}.html">

  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://yrlmz14.github.io/posts/{slug}.html">

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "author": {{
      "@type": "Person",
      "name": "Okan Yorulmaz",
      "url": "https://github.com/yrlmz14"
    }},
    "datePublished": "{iso_date}",
    "description": "{description}"
  }}
  </script>

  <link rel="stylesheet" href="/style.css">
  <script src="/main.js" defer></script>
</head>
<body>
  <div id="reading-progress"></div>

  <header>
    <h1><a href="/">Okan Yorulmaz</a></h1>
    <div class="nav-container">
      <nav>
        <a href="/">Blog</a>
        <a href="/projects.html">Projects</a>
        <a href="https://github.com/yrlmz14" target="_blank" rel="noopener">GitHub</a>
      </nav>
      <button id="theme-toggle" class="theme-toggle" aria-label="Toggle theme">☀️</button>
    </div>
  </header>

  <main>
    <article>
      <h1>{title}</h1>
      <div class="post-meta">
        Published on {display_date} • {read_time} min read
        <span style="margin-left: 8px;">
          <img src="https://hits.sh/yrlmz14.github.io/posts/{slug}.html.svg?style=flat-square&label=views&color=58a6ff" alt="views" style="vertical-align: middle; height: 16px;">
        </span>
      </div>

      {content_html}
    </article>

    <div class="comments-section">
      <h3>💬 Discussion & Comments</h3>
      <p style="color: var(--meta); font-size: 0.9rem;">Join the conversation via GitHub Discussions:</p>
      <script src="https://giscus.app/client.js"
        data-repo="yrlmz14/yrlmz14.github.io"
        data-repo-id="R_kgDOVGWv7g"
        data-category="General"
        data-category-id="DIC_kwDOVGWv7s4DKJ0s"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="en"
        crossorigin="anonymous"
        async>
      </script>
    </div>

    <p style="margin-top: 2rem;"><a href="/">← Back to all posts</a></p>
  </main>

  <footer>
    <div class="footer-links">
      <a href="/">Blog</a> •
      <a href="/projects.html">Projects</a> •
      <a href="/rss.xml">RSS Feed</a> •
      <a href="https://github.com/yrlmz14" target="_blank" rel="noopener">GitHub</a>
    </div>
    <p>© 2026 Okan Yorulmaz • Hosted on GitHub Pages</p>
  </footer>
</body>
</html>
"""

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text)

def md_to_html(md_text):
    html = []
    lines = md_text.splitlines()
    in_code_block = False
    code_lines = []

    for line in lines:
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                in_code_block = False
                escaped = "\n".join(code_lines).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html.append(f"<pre><code>{escaped}</code></pre>")
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("### "):
            html.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            html.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            html.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html.append(f"<li>{stripped[2:]}</li>")
        else:
            p = stripped
            p = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p)
            p = re.sub(r'\*(.*?)\*', r'<em>\1</em>', p)
            p = re.sub(r'`(.*?)`', r'<code>\1</code>', p)
            p = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', p)
            html.append(f"<p>{p}</p>")

    res = "\n      ".join(html)
    res = re.sub(r'(<li>.*?</li>(?:\s*<li>.*?</li>)*)', r'<ul>\n      \1\n      </ul>', res)
    return res

def create_new_post(title):
    slug = slugify(title)
    md_file = POSTS_DIR / f"{slug}.md"
    today = datetime.now()
    
    if md_file.exists():
        print(f"Error: {md_file} already exists.")
        return

    content = f"""---
title: {title}
description: A short summary of your article for Google and social previews.
date: {today.strftime('%Y-%m-%d')}
tags: homelab, projects, tutorial
---

Write your article here using regular markdown!

## Subheading

You can write normal paragraphs, code blocks, and bullet points:

- First point
- Second point

```python
# Sample code
print("Hello from Okan!")
```
"""
    md_file.write_text(content, encoding="utf-8")
    print(f"Created new post draft: {md_file}")
    print(f"Edit this file, then run: python publish.py --push")

def build_all_posts():
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    post_cards = []
    rss_items = []
    urls_for_sitemap = [
        ("https://yrlmz14.github.io/", datetime.now().strftime("%Y-%m-%d"), "1.0"),
        ("https://yrlmz14.github.io/projects.html", datetime.now().strftime("%Y-%m-%d"), "0.9")
    ]

    md_files = sorted(POSTS_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)

    for md_file in md_files:
        slug = md_file.stem
        raw = md_file.read_text(encoding="utf-8")
        
        title = slug
        description = "Tech writeup by Okan Yorulmaz"
        date_str = datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%B %d, %Y")
        iso_date = datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d")
        tags = []
        body_md = raw

        # Match frontmatter even with backslashes or leading whitespace
        fm_match = re.match(r'^\s*\\?---\s*\r?\n(.*?)\r?\n\\?---\s*\r?\n(.*)', raw, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            body_md = fm_match.group(2)
            for line in fm.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    k, v = k.strip().lower(), v.strip()
                    if k == "title": title = v
                    elif k == "description": description = v
                    elif k == "date":
                        iso_date = v
                        try:
                            dt = datetime.strptime(v, "%Y-%m-%d")
                            date_str = dt.strftime("%B %d, %Y")
                        except: pass
                    elif k == "tags":
                        tags = [t.strip() for t in v.split(",") if t.strip()]

        content_html = md_to_html(body_md)
        word_count = len(body_md.split())
        read_time = max(1, round(word_count / 180))

        out_html = POST_TEMPLATE.format(
            title=title,
            description=description,
            slug=slug,
            iso_date=iso_date,
            display_date=date_str,
            read_time=read_time,
            content_html=content_html
        )
        (POSTS_DIR / f"{slug}.html").write_text(out_html, encoding="utf-8")
        print(f"Generated: posts/{slug}.html")

        tags_html = "".join([f'<span class="tag">#{t}</span>' for t in tags])
        post_card = f"""      <div class="post-card">
        <h2><a href="/posts/{slug}.html">{title}</a></h2>
        <div class="post-meta">
          {date_str} • {read_time} min read
          <span class="view-badge">
            <img src="https://hits.sh/yrlmz14.github.io/posts/{slug}.html.svg?style=flat-square&label=views&color=58a6ff" alt="views" style="vertical-align: middle; margin-left: 6px; height: 16px;">
          </span>
        </div>
        <p>{description}</p>
        <div>
          {tags_html}
        </div>
      </div>"""
        post_cards.append(post_card)
        urls_for_sitemap.append((f"https://yrlmz14.github.io/posts/{slug}.html", iso_date, "0.8"))
        
        rss_items.append(f"""    <item>
      <title>{title}</title>
      <link>https://yrlmz14.github.io/posts/{slug}.html</link>
      <guid>https://yrlmz14.github.io/posts/{slug}.html</guid>
      <pubDate>{iso_date}</pubDate>
      <description>{description}</description>
    </item>""")

    # Update index.html
    if INDEX_FILE.exists() and post_cards:
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        pattern = r"<!-- POSTS_LIST_START -->.*?<!-- POSTS_LIST_END -->"
        replacement = "<!-- POSTS_LIST_START -->\n" + "\n".join(post_cards) + "\n      <!-- POSTS_LIST_END -->"
        updated_index = re.sub(pattern, replacement, index_content, flags=re.DOTALL)
        INDEX_FILE.write_text(updated_index, encoding="utf-8")
        print("Updated: index.html with latest post cards.")

    # Update sitemap.xml
    sitemap_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, mdate, prio in urls_for_sitemap:
        sitemap_lines.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{mdate}</lastmod>\n    <priority>{prio}</priority>\n  </url>")
    sitemap_lines.append('</urlset>')
    SITEMAP_FILE.write_text("\n".join(sitemap_lines), encoding="utf-8")
    print("Updated: sitemap.xml with latest URLs.")

    # Update rss.xml
    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Okan Yorulmaz | Tech Blog</title>
    <link>https://yrlmz14.github.io/</link>
    <description>Technical blog and homelab writeups by Okan Yorulmaz.</description>
    <language>en</language>
    <atom:link href="https://yrlmz14.github.io/rss.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(rss_items)}
  </channel>
</rss>"""
    RSS_FILE.write_text(rss_content, encoding="utf-8")
    print("Updated: rss.xml RSS feed.")

def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "commit", "-m", f"Publish updates ({datetime.now().strftime('%Y-%m-%d %H:%M')})"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
        print("\n🚀 Successfully pushed updates to GitHub Pages!")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "new":
        title = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "New Tech Post"
        create_new_post(title)
    else:
        build_all_posts()
        if "--push" in sys.argv:
            git_push()
