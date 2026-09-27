"""Web-side checks: can AI crawlers reach you, and is the page extractable.

Standard library only. Every fetch is time-boxed and size-capped so a slow or
hostile server cannot hang the audit.
"""

from __future__ import annotations

import gzip
import json
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

USER_AGENT = "AI-Visibility-Skill/1.0 (+https://github.com/; AEO audit)"
TIMEOUT = 12
MAX_BYTES = 2_000_000

# Who actually reads your site on behalf of an assistant. Two distinct jobs:
# training crawlers build the model's background knowledge, live/search bots
# fetch pages *during* a conversation. Blocking the live ones is what makes
# you invisible today; blocking the training ones costs you next model.
AI_BOTS: list[tuple[str, str, str]] = [
    ("GPTBot", "OpenAI", "training"),
    ("ChatGPT-User", "OpenAI", "live browsing"),
    ("OAI-SearchBot", "OpenAI", "search index"),
    ("ClaudeBot", "Anthropic", "training"),
    ("Claude-User", "Anthropic", "live browsing"),
    ("Claude-SearchBot", "Anthropic", "search index"),
    ("anthropic-ai", "Anthropic", "legacy"),
    ("PerplexityBot", "Perplexity", "search index"),
    ("Perplexity-User", "Perplexity", "live browsing"),
    ("Google-Extended", "Google Gemini", "training"),
    ("GoogleOther", "Google", "generic"),
    ("Bingbot", "Microsoft / Copilot", "search index"),
    ("CCBot", "Common Crawl", "training (many models)"),
    ("Applebot-Extended", "Apple Intelligence", "training"),
    ("Amazonbot", "Amazon", "training"),
    ("Bytespider", "ByteDance", "training"),
    ("meta-externalagent", "Meta AI", "training"),
    ("cohere-ai", "Cohere", "training"),
    ("MistralAI-User", "Mistral", "live browsing"),
]

# Referrer hostnames that mean "a human arrived here from an AI assistant".
AI_REFERRER_REGEX = (
    r"^(?:chatgpt\.com|chat\.openai\.com|openai\.com|claude\.ai|"
    r"perplexity\.ai|www\.perplexity\.ai|copilot\.microsoft\.com|"
    r"copilot\.cloud\.microsoft|bing\.com|gemini\.google\.com|"
    r"aistudio\.google\.com|(?:\w+\.)?mistral\.ai|chat\.deepseek\.com|"
    r"you\.com|phind\.com|pi\.ai|grok\.com|x\.ai|meta\.ai|"
    r"duckduckgo\.com|openrouter\.ai|poe\.com|kagi\.com)$"
)


@dataclass
class FetchResult:
    ok: bool
    status: int | None
    text: str | None
    error: str | None = None

    @property
    def size(self) -> int:
        return len(self.text or "")


def fetch(url: str, timeout: int = TIMEOUT) -> FetchResult:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Accept-Encoding": "gzip",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read(MAX_BYTES)
            if resp.headers.get("Content-Encoding") == "gzip":
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
            charset = resp.headers.get_content_charset() or "utf-8"
            return FetchResult(True, resp.status, raw.decode(charset, errors="replace"))
    except urllib.error.HTTPError as e:
        return FetchResult(False, e.code, None, f"HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network errors are all equivalent here
        return FetchResult(False, None, None, type(e).__name__ + ": " + str(e)[:120])


def base_url(domain: str) -> str:
    d = re.sub(r"^https?://", "", domain.strip()).rstrip("/")
    return "https://" + d


# --------------------------------------------------------------------------
# robots.txt
# --------------------------------------------------------------------------


def _robots_blocks(robots: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in robots.splitlines():
        line = raw.split("#")[0].strip()
        if not line:
            continue
        m = re.match(r"^([A-Za-z-]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        directive, value = m.group(1).lower(), m.group(2).strip()
        if directive == "user-agent":
            if current is None or current["rules"]:
                current = {"agents": [value], "rules": []}
                blocks.append(current)
            else:
                current["agents"].append(value)
        elif current is not None:
            current["rules"].append((directive, value))
    return blocks


def bot_status(robots: str | None, bot: str) -> dict[str, Any]:
    """Resolve one crawler against robots.txt.

    Only a blanket `Disallow: /` counts as blocked. Path-level rules are
    reported separately because they usually reflect a deliberate choice
    (admin areas, checkout) rather than an AI-visibility mistake.
    """
    entry = {"bot": bot, "allowed": True, "reason": "no rule — allowed by default",
             "partial": []}
    if not robots:
        return entry

    blocks = _robots_blocks(robots)
    explicit = [b for b in blocks if any(a.lower() == bot.lower() for a in b["agents"])]
    wildcard = [b for b in blocks if "*" in b["agents"]]
    applicable = explicit or wildcard
    source = f"explicit rule for {bot}" if explicit else "inherited from User-agent: *"

    if not applicable:
        return entry

    for block in applicable:
        for directive, value in block["rules"]:
            if directive != "disallow":
                continue
            if value == "/":
                entry["allowed"] = False
                entry["reason"] = f"blocked — Disallow: / ({source})"
                return entry
            if value:
                entry["partial"].append(value)

    entry["reason"] = f"allowed ({source})"
    return entry


# --------------------------------------------------------------------------
# JSON-LD / sitemap
# --------------------------------------------------------------------------

_JSONLD_RE = re.compile(
    r"<script[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>([\s\S]*?)</script\s*>", re.I
)


def _collect_types(node: Any, out: set[str]) -> None:
    if isinstance(node, list):
        for x in node:
            _collect_types(x, out)
        return
    if not isinstance(node, dict):
        return
    t = node.get("@type")
    if isinstance(t, str):
        out.add(t)
    elif isinstance(t, list):
        out.update(x for x in t if isinstance(x, str))
    if "@graph" in node:
        _collect_types(node["@graph"], out)
    for v in node.values():
        if isinstance(v, (dict, list)):
            _collect_types(v, out)


def parse_json_ld(html: str) -> dict[str, Any]:
    types: set[str] = set()
    matched = valid = 0
    for m in _JSONLD_RE.finditer(html):
        matched += 1
        try:
            _collect_types(json.loads(m.group(1).strip()), types)
            valid += 1
        except (json.JSONDecodeError, ValueError):
            continue
    if matched == 0:
        return {"ok": False, "types": [], "error": "no JSON-LD found"}
    if valid == 0:
        return {"ok": False, "types": [], "error": f"{matched} JSON-LD block(s), all malformed"}
    return {"ok": True, "types": sorted(types), "error": None,
            "blocks": matched, "malformed": matched - valid}


_LOC_RE = re.compile(r"<loc>\s*([^<]+?)\s*</loc>", re.I)


def parse_sitemap(xml: str, limit: int = 200) -> list[str]:
    return [m.group(1).strip() for m in _LOC_RE.finditer(xml)][:limit]


def resolve_sitemap_urls(domain: str, limit: int = 200) -> list[str]:
    """Follow a sitemap index one level down to reach real page URLs."""
    res = fetch(base_url(domain) + "/sitemap.xml")
    if not res.ok or not res.text:
        return []
    urls = parse_sitemap(res.text, limit)
    if not urls:
        return []
    if re.search(r"<sitemapindex\b", res.text, re.I):
        child = fetch(urls[0])
        if child.ok and child.text:
            return parse_sitemap(child.text, limit)
        return []
    return urls


# --------------------------------------------------------------------------
# page content signals
# --------------------------------------------------------------------------


def strip_html(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    return re.sub(r"\s+", " ", s).strip()


def _first(pattern: str, html: str, group: int = 1) -> str | None:
    m = re.search(pattern, html, re.I | re.S)
    if not m:
        return None
    text = strip_html(m.group(group)).strip()
    return text or None


def extract_page_signals(html: str) -> dict[str, Any]:
    """Pull out exactly what an AEO judgement needs — not the whole page.

    Feeding a full HTML document to a model wastes context and buries the
    signal. These are the parts that decide whether an assistant can lift a
    quotable answer out of the page.
    """
    title = _first(r"<title[^>]*>([\s\S]*?)</title>", html)
    meta_desc = None
    for pat in (r"<meta[^>]+name=[\"']description[\"'][^>]*content=[\"']([^\"']*)[\"']",
                r"<meta[^>]+content=[\"']([^\"']*)[\"'][^>]*name=[\"']description[\"']"):
        m = re.search(pat, html, re.I)
        if m:
            meta_desc = m.group(1).strip() or None
            break

    h1 = _first(r"<h1[^>]*>([\s\S]*?)</h1>", html)

    first_para = None
    for m in re.finditer(r"<p[^>]*>([\s\S]*?)</p>", html, re.I):
        text = strip_html(m.group(1))
        if len(text) >= 50:
            first_para = text
            break

    headings: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"<h([1-3])[^>]*>([\s\S]*?)</h\1>", html, re.I):
        text = strip_html(m.group(2))
        if text and text not in seen:
            seen.add(text)
            headings.append(text)
        if len(headings) >= 30:
            break

    tables: list[str] = []
    for tm in re.finditer(r"<table[^>]*>([\s\S]*?)</table>", html, re.I):
        rows: list[str] = []
        for rm in re.finditer(r"<tr[^>]*>([\s\S]*?)</tr>", tm.group(1), re.I):
            cells = [strip_html(c.group(1))
                     for c in re.finditer(r"<t[hd][^>]*>([\s\S]*?)</t[hd]>", rm.group(1), re.I)]
            if cells:
                rows.append(" | ".join(cells))
            if len(rows) >= 3:
                break
        if rows:
            tables.append("\n".join(rows))
        if len(tables) >= 3:
            break

    faq = [h for h in headings
           if h.rstrip().endswith("?") or re.search(r"често\s+задавани|faq|въпрос", h, re.I)][:10]

    body_text = strip_html(html)
    words = body_text.split()

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "first_paragraph": first_para,
        "headings": headings,
        "tables": tables,
        "faq_signals": faq,
        "schema": parse_json_ld(html),
        "word_count": len(words),
        "numbers_found": len(re.findall(r"\b\d[\d.,]*\s*(?:%|percent|процента|лв|€|\$)?", body_text))
                         if body_text else 0,
        "avg_words_between_headings": (
            round(len(words) / max(1, len(headings))) if headings else len(words)
        ),
        "excerpt": body_text[:1500],
    }


def fetch_page_signals(url: str) -> dict[str, Any]:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return {"error": "URL must start with http:// or https://", "url": url}
    res = fetch(url)
    if not res.ok or not res.text:
        return {"error": res.error or "fetch failed", "url": url, "status": res.status}
    signals = extract_page_signals(res.text)
    signals.update({"url": url, "status": res.status, "html_bytes": len(res.text)})
    return signals
