#!/usr/bin/env python3
"""Static doc + blog generator for the Lifeline site.

Converts the curated markdown (site/content/*.md), the repo's deep docs (docs/*.md), and the blog
(site/content/blog/*.md) into crawlable HTML that shares the site's Linear-grade shell, then emits
the GEO surface: sitemap.xml, robots.txt, llms.txt, and llms-full.txt. Output is committed (no
deploy-time deps).

Run from the repo root or from site/:  python site/build.py
"""
import datetime
import json
import os
import re
import sys

try:
    import markdown as md
except ImportError:
    sys.exit("This generator needs the 'markdown' package:  pip install markdown")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS_OUT = os.path.join(HERE, "docs")
BLOG_OUT = os.path.join(HERE, "blog")
BLOG_SRC = os.path.join(HERE, "content", "blog")
BASE = "https://lifelinecontext.com/"

# slug, nav-title, <title>/meta description, source markdown (relative to repo root)
PAGES = [
    ("getting-started", "Getting started", "Install Lifeline, run the loop, and bootstrap an existing project. Git for reasoning, in minutes.", "site/content/getting-started.md"),
    ("concepts",        "Concepts & laws", "The Entry, content-addressing, the 3 memory layers, supersession, the anti-hallucination anchor, and the 7 laws.", "site/content/concepts.md"),
    ("architecture",    "Architecture",    "Lifeline's architecture: the deterministic event model, reducers, recall, projection, and the store-is-source cutover.", "docs/ARCHITECTURE.md"),
    ("integration",     "Integration",     "Wire Lifeline into Claude Code, Cursor, Claude Desktop, and Gemini CLI via MCP — with auto-connect.", "docs/INTEGRATION.md"),
    ("mcp",             "MCP & remote",    "The MCP surface: local stdio, remote HTTP/SSE, the OAuth Resource Server, and multi-tenant cloud.", "docs/MCP_REMOTE.md"),
    ("cli",             "CLI reference",   "Every Lifeline command: log, propose/review/approve, context, verify, migrate, init, push/pull/clone.", "site/content/cli.md"),
]
NAV = [
    ("Start", [("getting-started", "Getting started"), ("concepts", "Concepts & laws"), ("cli", "CLI reference")]),
    ("Deep dive", [("architecture", "Architecture"), ("integration", "Integration"), ("mcp", "MCP & remote")]),
]

# cross-document link rewrites so repo-relative links resolve on the site
LINK_MAP = {
    "docs/ARCHITECTURE.md": "architecture.html", "ARCHITECTURE.md": "architecture.html",
    "docs/INTEGRATION.md": "integration.html", "INTEGRATION.md": "integration.html",
    "docs/MCP_REMOTE.md": "mcp.html", "MCP_REMOTE.md": "mcp.html",
    "docs/M3_TIER1_SUPABASE.md": "https://github.com/lifeline-context/lifeline/blob/main/docs/M3_TIER1_SUPABASE.md",
    "docs/DEPLOY.md": "https://github.com/lifeline-context/lifeline/blob/main/docs/DEPLOY.md",
    "LIFELINE.md": "https://github.com/lifeline-context/lifeline/blob/main/LIFELINE.md",
    "CONTRIBUTING.md": "https://github.com/lifeline-context/lifeline/blob/main/CONTRIBUTING.md",
    "PRD.md": "https://github.com/lifeline-context/lifeline/blob/main/PRD.md",
    ".mcp.json": "https://github.com/lifeline-context/lifeline/blob/main/.mcp.json",
    "llms.txt": "../llms.txt", "AGENTS.md": "https://github.com/lifeline-context/lifeline/blob/main/AGENTS.md",
}

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__ — Lifeline docs</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__CANON__">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Lifeline">
<meta property="og:title" content="__TITLE__ — Lifeline docs">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__CANON__">
<meta property="og:image" content="__BASE__assets/og.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#08090a">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;560;600&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"TechArticle","headline":"__TITLE__","description":"__DESC__","url":"__CANON__","author":{"@type":"Person","name":"jessianmart"},"publisher":{"@type":"Organization","name":"Lifeline","url":"__BASE__"},"isPartOf":{"@type":"WebSite","name":"Lifeline","url":"__BASE__"},"inLanguage":"en","license":"https://opensource.org/licenses/MIT"}
</script>
</head>
<body class="docs">
<div class="bg-fx"></div>
<header class="topbar">
  <a class="brand" href="../"><svg class="brandmark" viewBox="0 0 1024 1024" aria-hidden="true"><g fill="currentColor"><path d="M120 120 L270 120 L270 754 L660 754 L660 904 L210 904 Q120 904 120 814 L120 120 Z"/><path d="M364 120 L814 120 Q904 120 904 210 L904 904 L754 904 L754 270 L364 270 Z"/><rect x="412" y="330" width="72" height="364"/><rect x="540" y="330" width="72" height="364"/><rect x="330" y="412" width="364" height="72"/><rect x="330" y="540" width="364" height="72"/></g></svg> Lifeline <span class="ver">v0.3.0</span></a>
  <nav class="topnav">
    <a href="index.html">Docs</a>
    <a href="../blog/">Blog</a>
    <a href="https://pypi.org/project/lifeline-context/" target="_blank" rel="noopener">PyPI</a>
    <a class="pill" href="https://github.com/lifeline-context/lifeline" target="_blank" rel="noopener">GitHub ↗</a>
  </nav>
</header>
<div class="docs-shell">
  <aside class="docs-side">__SIDENAV__</aside>
  <main class="docs-main">
    <h1>__H1__</h1>
    <p class="docs-lead">__DESC__</p>
__BODY__
    <div class="docs-foot">
      <span>Lifeline — MIT licensed · <a href="__EDIT__">Edit on GitHub</a></span>
      <span><a href="../">← Back to the lifeline</a></span>
    </div>
  </main>
</div>
</body>
</html>
"""

# Blog shell: same Linear-grade chrome, article schema (BlogPosting + FAQPage) injected per post.
BLOG_SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<meta name="keywords" content="__KEYWORDS__">
<link rel="canonical" href="__CANON__">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="__AUTHOR__">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Lifeline">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__CANON__">
<meta property="og:image" content="__BASE__assets/og.svg">
<meta property="article:published_time" content="__DATE__">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__DESC__">
<meta name="theme-color" content="#08090a">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/logo/lifeline-tile-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;560;600&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
<script type="application/ld+json">
__JSONLD__
</script>
</head>
<body class="docs">
<div class="bg-fx"></div>
<header class="topbar">
  <a class="brand" href="../"><svg class="brandmark" viewBox="0 0 1024 1024" aria-hidden="true"><g fill="currentColor"><path d="M120 120 L270 120 L270 754 L660 754 L660 904 L210 904 Q120 904 120 814 L120 120 Z"/><path d="M364 120 L814 120 Q904 120 904 210 L904 904 L754 904 L754 270 L364 270 Z"/><rect x="412" y="330" width="72" height="364"/><rect x="540" y="330" width="72" height="364"/><rect x="330" y="412" width="364" height="72"/><rect x="330" y="540" width="364" height="72"/></g></svg> Lifeline <span class="ver">v0.3.0</span></a>
  <nav class="topnav">
    <a href="../docs/">Docs</a>
    <a href="index.html">Blog</a>
    <a href="https://pypi.org/project/lifeline-context/" target="_blank" rel="noopener">PyPI</a>
    <a class="pill" href="https://github.com/lifeline-context/lifeline" target="_blank" rel="noopener">GitHub ↗</a>
  </nav>
</header>
<div class="docs-shell">
  <aside class="docs-side">__SIDENAV__</aside>
  <main class="docs-main">
    <h1>__H1__</h1>
    <p class="docs-lead">__DESC__</p>
__BODY__
    <div class="docs-foot">
      <span>Lifeline — MIT licensed · <a href="__EDIT__">Edit on GitHub</a></span>
      <span><a href="../">← Back to the lifeline</a></span>
    </div>
  </main>
</div>
</body>
</html>
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def sidenav(current):
    out = []
    for group, items in NAV:
        out.append('<div class="group">%s</div>' % group)
        for slug, label in items:
            cls = ' class="current"' if slug == current else ''
            out.append('<a href="%s.html"%s>%s</a>' % (slug, cls, label))
    return "\n      ".join(out)


def strip_first_h1(text):
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("# "):
            return "\n".join(lines[:i] + lines[i + 1:]).strip()
        if ln.strip():
            break
    return text


def rewrite_links(text):
    for src, dst in LINK_MAP.items():
        text = text.replace("(%s)" % src, "(%s)" % dst)
    return text


def render(slug, title, desc, src_rel):
    raw = open(os.path.join(ROOT, src_rel), encoding="utf-8").read()
    body_md = rewrite_links(strip_first_h1(raw))
    body_html = md.markdown(body_md, extensions=["fenced_code", "tables", "sane_lists"])
    edit = "https://github.com/lifeline-context/lifeline/blob/main/" + src_rel
    html = (SHELL
            .replace("__TITLE__", title).replace("__DESC__", desc)
            .replace("__CANON__", BASE + "docs/" + slug + ".html")
            .replace("__BASE__", BASE).replace("__SIDENAV__", sidenav(slug))
            .replace("__H1__", title).replace("__BODY__", body_html).replace("__EDIT__", edit))
    open(os.path.join(DOCS_OUT, slug + ".html"), "w", encoding="utf-8").write(html)
    return raw


def docs_index():
    cards = []
    for slug, title, desc, _ in PAGES:
        cards.append('<a class="doclink" href="%s.html"><span class="t">%s →</span><span class="d">%s</span></a>'
                     % (slug, title, desc))
    body = '<div class="doclist" style="grid-template-columns:repeat(2,1fr)">%s</div>' % "".join(cards)
    html = (SHELL
            .replace("__TITLE__", "Documentation").replace("__DESC__", "Everything about Lifeline — install, concepts, architecture, integration, MCP, and the CLI.")
            .replace("__CANON__", BASE + "docs/").replace("__BASE__", BASE)
            .replace("__SIDENAV__", sidenav(None)).replace("__H1__", "Documentation")
            .replace("__BODY__", body).replace("__EDIT__", "https://github.com/lifeline-context/lifeline/tree/main/docs"))
    open(os.path.join(DOCS_OUT, "index.html"), "w", encoding="utf-8").write(html)


# ---- blog ---------------------------------------------------------------------------------
def parse_frontmatter(path):
    """Minimal YAML-frontmatter parser for the controlled blog format (scalars + a faq list)."""
    raw = open(path, encoding="utf-8").read()
    meta = {"faq": []}
    body = raw
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        cur, in_faq = None, False
        for line in fm.splitlines():
            if not line.strip():
                continue
            if line.startswith("faq:"):
                in_faq = True
                continue
            stripped = line.lstrip()
            if in_faq and stripped.startswith("- q:"):
                cur = {"q": stripped.split(":", 1)[1].strip().strip('"'), "a": ""}
                meta["faq"].append(cur)
            elif in_faq and stripped.startswith("a:") and cur is not None:
                cur["a"] = stripped.split(":", 1)[1].strip().strip('"')
            elif not line.startswith(" ") and ":" in line:
                in_faq = False
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    return meta, body.strip()


def blog_sidenav(current, posts):
    out = ['<div class="group">Articles</div>']
    for m in posts:
        cls = ' class="current"' if m["slug"] == current else ''
        out.append('<a href="%s.html"%s>%s</a>' % (m["slug"], cls, esc(m["title"])))
    return "\n      ".join(out)


def blog_jsonld(meta, canon):
    article = {"@type": "BlogPosting", "headline": meta["title"], "description": meta["description"],
               "url": canon, "mainEntityOfPage": canon, "datePublished": meta.get("date", ""),
               "author": {"@type": "Person", "name": meta.get("author", "jessianmart")},
               "publisher": {"@type": "Organization", "name": "Lifeline", "url": BASE},
               "keywords": meta.get("keywords", ""), "inLanguage": "en",
               "license": "https://opensource.org/licenses/MIT"}
    graph = [article]
    if meta.get("faq"):
        graph.append({"@type": "FAQPage",
                      "mainEntity": [{"@type": "Question", "name": f["q"],
                                      "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                                     for f in meta["faq"]]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def render_blog_post(meta, body_md, posts):
    slug = meta["slug"]
    canon = BASE + "blog/" + slug + ".html"
    body_html = md.markdown(rewrite_links(strip_first_h1(body_md)),
                            extensions=["fenced_code", "tables", "sane_lists"])
    edit = "https://github.com/lifeline-context/lifeline/blob/main/site/content/blog/" + slug + ".md"
    html = (BLOG_SHELL
            .replace("__TITLE__", esc(meta["title"])).replace("__DESC__", esc(meta["description"]))
            .replace("__KEYWORDS__", esc(meta.get("keywords", ""))).replace("__AUTHOR__", esc(meta.get("author", "jessianmart")))
            .replace("__DATE__", meta.get("date", "")).replace("__CANON__", canon).replace("__BASE__", BASE)
            .replace("__SIDENAV__", blog_sidenav(slug, posts)).replace("__H1__", esc(meta["title"]))
            .replace("__JSONLD__", blog_jsonld(meta, canon)).replace("__BODY__", body_html).replace("__EDIT__", edit))
    open(os.path.join(BLOG_OUT, slug + ".html"), "w", encoding="utf-8").write(html)


def blog_index(posts):
    canon = BASE + "blog/"
    cards = []
    for m in posts:
        cards.append('<a class="doclink" href="%s.html"><span class="t">%s →</span><span class="d">%s</span></a>'
                     % (m["slug"], esc(m["title"]), esc(m["description"])))
    body = '<div class="doclist" style="grid-template-columns:1fr">%s</div>' % "".join(cards)
    graph = {"@context": "https://schema.org", "@type": "Blog", "url": canon, "name": "Lifeline blog",
             "description": "Essays on time-to-context, context engineering, and AI context handoff.",
             "blogPost": [{"@type": "BlogPosting", "headline": m["title"], "url": canon + m["slug"] + ".html",
                           "description": m["description"], "datePublished": m.get("date", "")} for m in posts]}
    html = (BLOG_SHELL
            .replace("__TITLE__", "Blog — Lifeline")
            .replace("__DESC__", "Essays on time-to-context, context engineering, and how AIs inherit each other's context.")
            .replace("__KEYWORDS__", "context engineering, time to context, AI context handoff, AI memory, MCP")
            .replace("__AUTHOR__", "jessianmart").replace("__DATE__", "").replace("__CANON__", canon).replace("__BASE__", BASE)
            .replace("__SIDENAV__", blog_sidenav(None, posts)).replace("__H1__", "Blog")
            .replace("__JSONLD__", json.dumps(graph, ensure_ascii=False)).replace("__BODY__", body)
            .replace("__EDIT__", "https://github.com/lifeline-context/lifeline/tree/main/site/content/blog"))
    open(os.path.join(BLOG_OUT, "index.html"), "w", encoding="utf-8").write(html)


def load_posts():
    posts = []
    if os.path.isdir(BLOG_SRC):
        for fn in sorted(os.listdir(BLOG_SRC)):
            if fn.endswith(".md"):
                m, b = parse_frontmatter(os.path.join(BLOG_SRC, fn))
                m["_body"] = b
                posts.append(m)
    posts.sort(key=lambda m: m.get("date", ""), reverse=True)
    return posts


def geo_files(full_text, posts=()):
    today = datetime.date.today().isoformat()
    urls = [(BASE, "1.0"), (BASE + "docs/", "0.9")] + [(BASE + "docs/" + s + ".html", "0.8") for s, *_ in PAGES]
    if posts:
        urls.append((BASE + "blog/", "0.7"))
        urls += [(BASE + "blog/" + m["slug"] + ".html", "0.7") for m in posts]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, pri in urls:
        sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (url, today, pri))
    sm.append("</urlset>")
    open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")

    robots = (
        "# Lifeline — all crawlers welcome, AI engines explicitly invited.\n"
        "User-agent: *\nAllow: /\n\n"
        "User-agent: GPTBot\nAllow: /\n"
        "User-agent: OAI-SearchBot\nAllow: /\n"
        "User-agent: ChatGPT-User\nAllow: /\n"
        "User-agent: ClaudeBot\nAllow: /\n"
        "User-agent: Claude-Web\nAllow: /\n"
        "User-agent: anthropic-ai\nAllow: /\n"
        "User-agent: PerplexityBot\nAllow: /\n"
        "User-agent: Google-Extended\nAllow: /\n"
        "User-agent: Applebot-Extended\nAllow: /\n"
        "User-agent: CCBot\nAllow: /\n\n"
        "Sitemap: %ssitemap.xml\n" % BASE
    )
    open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8").write(robots)

    llms = [
        "# Lifeline",
        "",
        "> A context runtime for AI-assisted development — \"git for reasoning\". An append-only,",
        "> content-addressed, anchored ledger of a project's WHY, delivered to any AI over MCP so a",
        "> fresh model connects and already knows what / why / decided / next. Time-to-Context -> 0.",
        "",
        "Key facts: open source (MIT); install `pip install lifeline-context`; Python 3.10+; MCP-native;",
        "writes are human-in-the-loop (AI proposes, human approves); every context item is anchored to",
        "the cryptographic hash of its source event (anti-hallucination); append-only with supersession.",
        "",
        "## Docs",
    ]
    for slug, title, desc, _ in PAGES:
        llms.append("- [%s](%sdocs/%s.html): %s" % (title, BASE, slug, desc))
    if posts:
        llms += ["", "## Articles"]
        for m in posts:
            llms.append("- [%s](%sblog/%s.html): %s" % (m["title"], BASE, m["slug"], m["description"]))
    llms += [
        "",
        "## Source",
        "- [GitHub repository](https://github.com/lifeline-context/lifeline)",
        "- [PyPI package: lifeline-context](https://pypi.org/project/lifeline-context/)",
        "- [Full text for LLMs](%sllms-full.txt)" % BASE,
    ]
    open(os.path.join(HERE, "llms.txt"), "w", encoding="utf-8").write("\n".join(llms) + "\n")
    open(os.path.join(HERE, "llms-full.txt"), "w", encoding="utf-8").write(full_text)


def main():
    os.makedirs(DOCS_OUT, exist_ok=True)
    os.makedirs(BLOG_OUT, exist_ok=True)
    full = ["# Lifeline — full documentation for LLMs\n",
            "Source: %s — MIT licensed. https://github.com/lifeline-context/lifeline\n" % BASE]
    for slug, title, desc, src in PAGES:
        raw = render(slug, title, desc, src)
        full.append("\n\n" + "=" * 78 + "\n# " + title + "\n" + "=" * 78 + "\n\n" + raw.strip())
    docs_index()

    posts = load_posts()
    for m in posts:
        render_blog_post(m, m["_body"], posts)
    if posts:
        blog_index(posts)
        for m in posts:
            full.append("\n\n" + "=" * 78 + "\n# " + m["title"] + "\n" + "=" * 78 + "\n\n" + m["_body"].strip())

    geo_files("\n".join(full) + "\n", posts)
    print("built %d doc pages + %d blog posts + indexes + sitemap.xml + robots.txt + llms.txt + llms-full.txt"
          % (len(PAGES), len(posts)))


if __name__ == "__main__":
    main()
