"""Core detection logic for AI visibility analysis.

Ported from a production AEO monitoring platform (TypeScript) and its
predecessor Python CLI. Standard library only — no dependencies to install.

The functions here answer one question about a single AI answer:
  "Is this brand in here, where, how is it described, and who else is?"
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# --------------------------------------------------------------------------
# brand config
# --------------------------------------------------------------------------

# Words that, near a bare brand name, make a match much more likely to be
# about the site rather than a coincidental noun. Extend per language via
# brand.json -> context_words.
DEFAULT_CONTEXT_WORDS = [
    # Bulgarian
    "сайт", "портал", "уебсайт", "страница", "платформа", "блог", "медия",
    "магазин", "марка", "бранд", "компания", "фирма", "услуга",
    # English
    "site", "website", "portal", "page", "platform", "blog", "brand",
    "company", "store", "shop", "service", "tool", "app",
]

# Stems, not full words. Bulgarian inflects heavily ("остарял" / "остарели" /
# "остаряло"), so matching whole forms misses most real sentences. The
# `(?<!не)` / `(?<!un)` guards stop a positive stem from firing inside its own
# negation — "ненадежден" must not count as "надежден".
POSITIVE_WORDS = [
    # Bulgarian
    r"препоръч", r"отлич", r"качествен", r"полез", r"(?<!не)надежд",
    r"(?<!не)достовер", r"водещ", r"популяр", r"авторитет", r"изчерпател",
    r"богат", r"(?<!не)актуал", r"ценен", r"ценна", r"ценни",
    r"най-добр", r"добър", r"добра", r"добро", r"добри", r"предпочитан",
    r"утвърд", r"безплат", r"обширен",
    # English
    r"recommend", r"excellent", r"great\b", r"(?<!un)reliable", r"trusted",
    r"leading", r"popular", r"authoritative", r"comprehensive", r"valuable",
    r"\bbest\b", r"top-rated", r"well-established", r"solid", r"go-to",
]

NEGATIVE_WORDS = [
    # Bulgarian
    r"ненадежд", r"недостовер", r"слаб", r"остаря", r"неактуал", r"непълн",
    r"неточ", r"съмнител", r"проблем", r"оплакван", r"разочарова", r"лош",
    r"остарял", r"липсва", r"трудно се",
    # English
    r"unreliable", r"outdated", r"incomplete", r"inaccurate", r"questionable",
    r"problematic", r"complaint", r"disappointing", r"lacking", r"\bpoor\b",
    r"hard to navigate", r"no longer",
]


@dataclass
class Brand:
    """Everything the analysis needs to know about the site under test."""

    brand: str
    domain: str
    aliases: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    competitors: list[str] = field(default_factory=list)
    context_words: list[str] = field(default_factory=list)
    language: str = "auto"
    positioning: str = ""

    @classmethod
    def load(cls, path: str | Path) -> "Brand":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})

    @property
    def all_context_words(self) -> list[str]:
        return self.context_words or DEFAULT_CONTEXT_WORDS


# --------------------------------------------------------------------------
# mention detection
# --------------------------------------------------------------------------


@dataclass
class WeightedPattern:
    pattern: re.Pattern[str]
    weight: int
    label: str


@dataclass
class MentionMatch:
    start: int
    end: int
    weight: int
    label: str


def _esc(s: str) -> str:
    return re.escape(s)


def build_mention_patterns(brand: Brand) -> list[WeightedPattern]:
    """Weighted patterns, strongest evidence first.

    Weight encodes confidence, not frequency: a literal domain hit (10) is
    proof; a capitalised brand name sitting next to the word "website" (5) is
    strong circumstantial evidence; a bare brand name alone is too noisy to
    count on its own, so it only exists in the contextual pattern.
    """
    domain = brand.domain.lower().lstrip("www.")
    base = domain.split(".")[0]
    pats: list[WeightedPattern] = [
        WeightedPattern(re.compile(rf"https?://(?:www\.)?{_esc(domain)}", re.I), 10, "url"),
        WeightedPattern(re.compile(rf"\bwww\.{_esc(domain)}", re.I), 10, "www"),
        WeightedPattern(re.compile(rf"\b{_esc(domain)}\b", re.I), 10, "domain"),
    ]

    for alias in brand.aliases:
        if alias.strip():
            pats.append(
                WeightedPattern(re.compile(rf"\b{_esc(alias.strip())}\b", re.I), 9, "alias")
            )

    if brand.brand and brand.brand.lower() not in (domain, base):
        pats.append(
            WeightedPattern(re.compile(rf"\b{_esc(brand.brand)}\b", re.I), 9, "brand")
        )

    for kw in brand.keywords:
        if kw.strip():
            pats.append(
                WeightedPattern(re.compile(rf"\b{_esc(kw.strip())}\b", re.I), 7, "keyword")
            )

    ctx = "|".join(_esc(w) for w in brand.all_context_words)
    cap = base[:1].upper() + base[1:]
    pats.append(
        WeightedPattern(
            re.compile(
                rf"(?:(?:{ctx}).{{0,40}}\b{_esc(cap)}\b|\b{_esc(cap)}\b.{{0,40}}(?:{ctx}))",
                re.I | re.S,
            ),
            5,
            "contextual",
        )
    )
    return pats


def find_best_match(text: str, patterns: Iterable[WeightedPattern]) -> MentionMatch | None:
    best: MentionMatch | None = None
    for wp in patterns:
        m = wp.pattern.search(text)
        if m and (best is None or wp.weight > best.weight):
            best = MentionMatch(m.start(), m.end(), wp.weight, wp.label)
    return best


_SENT_START = (". ", ".\n", "? ", "! ", "\n\n")
_SENT_END = (re.compile(r"\. "), re.compile(r"\.\n"), re.compile(r"\? "), re.compile(r"! "))


def extract_mention_context(text: str, start: int, end: int, window: int = 200) -> str:
    """The sentence the brand appears in — this is the description AI gives you.

    Reading it matters more than the yes/no: it is your positioning as the
    model understands it, and you did not write it.
    """
    before, after = text[:start], text[end:]

    starts = [before.rfind(d) + len(d) for d in _SENT_START if before.rfind(d) >= 0]
    sent_start = max(starts) if starts else 0

    ends = []
    for pat in _SENT_END:
        m = pat.search(after)
        if m:
            ends.append(end + m.end())
    sent_end = min(ends) if ends else min(end + window, len(text))

    return " ".join(text[sent_start:sent_end].split()).strip()


# --------------------------------------------------------------------------
# competitors
# --------------------------------------------------------------------------

# Latin-script hostnames only. AI answers are full of file names and version
# strings that look domain-ish, so we exclude the usual suspects rather than
# maintaining a TLD allowlist that goes stale.
_DOMAIN_RE = re.compile(
    r"\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24})\b", re.I
)

_NOT_TLDS = {
    "js", "ts", "py", "md", "txt", "html", "htm", "css", "json", "xml", "csv",
    "png", "jpg", "jpeg", "gif", "svg", "pdf", "zip", "gz", "sh", "yml", "yaml",
    "php", "asp", "jsx", "tsx", "sql", "log", "ini", "env", "lock", "toml",
}


def _norm_domain(raw: str) -> str:
    d = raw.strip().lower().rstrip(".")
    d = re.sub(r"^https?://", "", d)
    d = re.sub(r"^www\.", "", d)
    return d.split("/")[0]


def find_competitors(text: str, own_domain: str, known: Iterable[str] = ()) -> list[str]:
    """Every other brand domain the model put in front of the user.

    Anyone listed beside you owns attention you did not get. Known competitors
    are matched by substring so `example.com` also catches `shop.example.com`.
    """
    own = _norm_domain(own_domain)
    own_base = own.split(".")[0]
    found: set[str] = set()
    lower = text.lower()

    for comp in known:
        c = _norm_domain(comp)
        if c and c != own and c in lower:
            found.add(c)

    for m in _DOMAIN_RE.finditer(text):
        d = _norm_domain(m.group(1))
        tld = d.rsplit(".", 1)[-1]
        if tld in _NOT_TLDS:
            continue
        if d == own or d.endswith("." + own):
            continue
        if d.split(".")[0] == own_base and len(d.split(".")) == 2:
            continue
        found.add(d)

    return sorted(found)


# --------------------------------------------------------------------------
# sentiment
# --------------------------------------------------------------------------

_POS_RE = re.compile("|".join(POSITIVE_WORDS), re.I)
_NEG_RE = re.compile("|".join(NEGATIVE_WORDS), re.I)


def analyze_sentiment(text: str) -> str:
    """Keyword tally, deliberately crude.

    It is a triage signal for "which descriptions should a human read", not a
    verdict. Treat every `negative` as a prompt to open the raw answer.
    """
    pos = len(_POS_RE.findall(text))
    neg = len(_NEG_RE.findall(text))
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


# --------------------------------------------------------------------------
# ranked lists
# --------------------------------------------------------------------------

_BULLET_RE = re.compile(r"^\s*[-*+•]\s+")
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+")
_HEADING_NUM_RE = re.compile(r"^\s*#{1,6}\s*\d+[.)]\s+")
_TABLE_ROW_RE = re.compile(r"^\s*\|")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


@dataclass
class BrandListEntry:
    brand: str
    domain: str
    list_index: int
    position: int
    list_size: int
    is_own: bool


def _marker_kind(line: str) -> tuple[str, int | None] | None:
    """Classify a line as a list item, returning its kind and explicit number."""
    if _TABLE_ROW_RE.match(line):
        return None
    m = _HEADING_NUM_RE.match(line)
    if m:
        return "numbered", int(re.search(r"\d+", m.group(0)).group(0))
    if _BULLET_RE.match(line):
        return "bullet", None
    m = _NUMBERED_RE.match(line)
    if m:
        return "numbered", int(re.search(r"\d+", m.group(0)).group(0))
    return None


def _strip_marker(line: str) -> str:
    line = _HEADING_NUM_RE.sub("", line)
    line = _BULLET_RE.sub("", line)
    line = _NUMBERED_RE.sub("", line)
    return line.strip()


def _extract_anchor(item: str) -> tuple[str, str | None]:
    link = _MD_LINK_RE.search(item)
    if link:
        label, url = link.group(1).strip(), link.group(2).strip()
        dm = _DOMAIN_RE.search(url)
        if dm:
            return (label or dm.group(1)), _norm_domain(dm.group(1))

    dm = _DOMAIN_RE.search(item)
    if dm and dm.group(1).rsplit(".", 1)[-1].lower() not in _NOT_TLDS:
        before = item[: dm.start()]
        if ":" in before:
            return item[:60].strip(), None
        return dm.group(1), _norm_domain(dm.group(1))

    bold = _BOLD_RE.search(item)
    if bold:
        return bold.group(1).strip(), None

    return item[:60].strip(), None


MAX_GAP_LINES = 12


def _find_list_blocks(text: str) -> list[list[tuple[str, int]]]:
    """Group list items into ranked lists, returning (item_text, position) pairs.

    AI answers rarely give you a tidy contiguous list. The common shape is a
    numbered heading followed by two or three lines of prose, then the next
    heading. Splitting on the first non-marker line would turn a top-5 into
    five lists of one and lose every position.

    So items are grouped by proximity instead: same marker kind, no more than
    MAX_GAP_LINES apart, and — for numbered lists — an increasing counter. A
    counter that restarts means a genuinely new list.
    """
    items: list[tuple[int, str, str, int | None]] = []
    for lineno, line in enumerate(text.splitlines()):
        marked = _marker_kind(line)
        if marked is None:
            continue
        kind, number = marked
        stripped = _strip_marker(line)
        if stripped:
            items.append((lineno, kind, stripped, number))

    blocks: list[list[tuple[str, int]]] = []
    current: list[tuple[str, int]] = []
    prev_line = prev_kind = prev_num = None

    for lineno, kind, item, number in items:
        restart = (
            prev_kind is not None
            and (kind != prev_kind
                 or lineno - prev_line > MAX_GAP_LINES
                 or (number is not None and prev_num is not None and number <= prev_num))
        )
        if restart:
            if len(current) >= 2:
                blocks.append(current)
            current = []
        current.append((item, number if number is not None else len(current) + 1))
        prev_line, prev_kind, prev_num = lineno, kind, number

    if len(current) >= 2:
        blocks.append(current)
    return blocks


def extract_brand_list(text: str, own_patterns: list[WeightedPattern]) -> list[BrandListEntry]:
    """Find enumerations and record where each brand sits.

    "Mentioned" is too coarse a signal. Being 1st of 5 in one model and 5th of
    5 in another is the difference between winning the click and padding
    someone else's list.
    """
    out: list[BrandListEntry] = []
    for list_index, items in enumerate(_find_list_blocks(text)):
        seen: set[str] = set()
        for item, position in items:
            name, domain = _extract_anchor(item)
            if not domain or domain in seen:
                continue
            seen.add(domain)
            out.append(
                BrandListEntry(
                    brand=name,
                    domain=domain,
                    list_index=list_index,
                    position=position,
                    list_size=len(items),
                    is_own=find_best_match(item, own_patterns) is not None,
                )
            )
    return out


# --------------------------------------------------------------------------
# citations
# --------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://[^\s)\"'<>\]]+", re.I)
_TRAILING_PUNCT_RE = re.compile(r"[.,;:!?')\]\"'»]+$")

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "ref", "ref_src", "mc_cid", "mc_eid", "igshid",
}


def normalize_url(raw: str) -> str | None:
    trimmed = _TRAILING_PUNCT_RE.sub("", raw.strip())
    try:
        parts = urlsplit(trimmed)
    except ValueError:
        return None
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None

    query = urlencode(
        [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
         if k.lower() not in _TRACKING_PARAMS]
    )
    path = parts.path
    if path == "/":
        path = ""
    elif path.endswith("/"):
        path = path[:-1]

    return urlunsplit((parts.scheme, parts.netloc.lower(), path, query, ""))


def extract_citations(text: str) -> list[str]:
    """Which *pages* the model cited, not just which brands.

    A competitor's cited article is a concrete outreach target: that page is
    already inside the model's answer, so getting mentioned on it is the
    cheapest way in.
    """
    out: list[str] = []
    seen: set[str] = set()
    for m in _URL_RE.finditer(text or ""):
        norm = normalize_url(m.group(0))
        if norm and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out


# --------------------------------------------------------------------------
# top-level analysis
# --------------------------------------------------------------------------

SENTIMENT_WINDOW = 200


def analyze_response(response: str | None, brand: Brand,
                     patterns: list[WeightedPattern] | None = None) -> dict[str, Any]:
    """Full analysis of one model answer to one prompt."""
    patterns = patterns or build_mention_patterns(brand)

    if not response or not response.strip():
        return {
            "mentioned": "error",
            "match_type": None,
            "description": "",
            "competitors": [],
            "sentiment": "neutral",
            "list_positions": [],
            "best_position": None,
            "cited_urls": [],
            "brands_in_lists": [],
        }

    entries = extract_brand_list(response, patterns)
    competitors = set(find_competitors(response, brand.domain, brand.competitors))
    own = _norm_domain(brand.domain)
    for e in entries:
        if not e.is_own and e.domain and e.domain != own:
            competitors.add(e.domain)

    positions = [
        {"list_index": e.list_index, "position": e.position, "list_size": e.list_size}
        for e in entries if e.is_own
    ]
    best_position = min((p["position"] for p in positions), default=None)

    best = find_best_match(response, patterns)
    if best is None:
        return {
            "mentioned": "no",
            "match_type": None,
            "description": "",
            "competitors": sorted(competitors),
            "sentiment": "neutral",
            "list_positions": [],
            "best_position": None,
            "cited_urls": extract_citations(response),
            "brands_in_lists": [asdict(e) for e in entries],
        }

    ctx_start = max(0, best.start - SENTIMENT_WINDOW)
    ctx_end = min(len(response), best.end + SENTIMENT_WINDOW)

    return {
        "mentioned": "yes",
        "match_type": best.label,
        "description": extract_mention_context(response, best.start, best.end),
        "competitors": sorted(competitors),
        "sentiment": analyze_sentiment(response[ctx_start:ctx_end]),
        "list_positions": positions,
        "best_position": best_position,
        "cited_urls": extract_citations(response),
        "brands_in_lists": [asdict(e) for e in entries],
    }


# --------------------------------------------------------------------------
# response files
# --------------------------------------------------------------------------

_HEADER_RE = re.compile(r"^([A-Za-z_]+)\s*:\s*(.*)$")
_SEPARATOR_RE = re.compile(r"^=+\s*$")


def parse_response_file(path: str | Path) -> dict[str, Any]:
    """Read a pasted answer file.

    Format (the `====` line ends the header; everything after it is the answer):

        ID: p01
        PROMPT: Which is the best ...?
        MODEL: chatgpt
        DATE: 2026-08-01
        ============================================================

        <the answer>
    """
    text = Path(path).read_text(encoding="utf-8", errors="replace").lstrip("﻿")
    lines = text.splitlines()

    meta: dict[str, str] = {}
    body_start = 0
    for i, line in enumerate(lines):
        if _SEPARATOR_RE.match(line):
            body_start = i + 1
            break
        m = _HEADER_RE.match(line)
        if m:
            meta[m.group(1).strip().lower()] = m.group(2).strip()
        elif line.strip() == "" and meta:
            continue
        elif line.strip():
            body_start = i
            break

    body = "\n".join(lines[body_start:]).strip()
    if body.lower() in ("(no response)", "(none)", "n/a", "-"):
        body = ""

    return {
        "id": meta.get("id", ""),
        "prompt": meta.get("prompt", ""),
        "model": meta.get("model", "unknown"),
        "date": meta.get("date", ""),
        "body": body,
        "path": str(path),
    }


def write_response_stub(path: Path, prompt_id: str, prompt_text: str,
                        model: str, date: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"ID: {prompt_id}\n"
        f"PROMPT: {prompt_text}\n"
        f"MODEL: {model}\n"
        f"DATE: {date}\n"
        f"{'=' * 60}\n\n"
        f"(no response)\n",
        encoding="utf-8",
    )


def slugify(text: str, max_len: int = 60) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip()
    text = re.sub(r"[\s]+", "_", text)
    return text[:max_len] or "untitled"


def load_prompts(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("prompts", [])
    out = []
    for i, p in enumerate(data):
        if isinstance(p, str):
            p = {"text": p}
        out.append({
            "id": p.get("id") or f"p{i + 1:02d}",
            "text": p["text"],
            "category": p.get("category", "topic"),
            "intent": p.get("intent") or intent_from_category(p.get("category")),
        })
    return out


def intent_from_category(category: str | None) -> str:
    if category in ("brand", "comparison"):
        return "high"
    if category == "educational":
        return "low"
    return "medium"
