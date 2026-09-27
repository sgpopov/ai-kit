#!/usr/bin/env python3
"""Verify the detection logic against realistic AI answers.

Fixtures are trimmed from real ChatGPT / Gemini / Claude answers (Bulgarian and
English) so the checks exercise the shapes that actually break parsers:
markdown link lists, numbered headings, inline domains, tables, and answers
where the brand is absent but competitors are not.

Run: python aeo.py selftest
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import aeolib  # noqa: E402
import aeoweb  # noqa: E402

PASS, FAIL = 0, 0


def check(name: str, got, want) -> None:
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ok    {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}\n          got:  {got!r}\n          want: {want!r}")


def check_true(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok    {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


BRAND = aeolib.Brand(
    brand="Nauka.bg",
    domain="nauka.bg",
    aliases=["Българска Наука"],
    keywords=["научно списание"],
    competitors=["offnews.bg"],
)

# A markdown list with linked brands — the common Gemini/ChatGPT shape.
GEMINI_LIST = """\
Изборът зависи от това какво търсите. Ето безспорните лидери:

### 1. **[Nauka.bg (Българска Наука)](https://nauka.bg)** – Най-изчерпателният ресурс
Това е най-голямата и популярна платформа за наука в България.

### 2. **[Obekti.bg (Обекти)](https://www.obekti.bg)** – За любопитни факти
Ежедневно съдържание на достъпен език.

### 3. **[Nauka.offnews.bg](https://nauka.offnews.bg)** – Актуални научни новини
Бързо отразяване на световните научни събития.

### 4. **[National Geographic България](https://www.nationalgeographic.bg)**
Екология, география и археология.
"""

# Bullet list where the brand is missing entirely.
ABSENT = """\
For Bulgarian science news I'd suggest:

- **Obekti.bg** (https://obekti.bg) — daily popular science
- **Kaldata.com** (https://kaldata.com) — technology coverage
- **BNR.bg** (https://bnr.bg) — public radio science desk

Each of these publishes regularly in Bulgarian.
"""

# Prose mention with a bare brand name plus context word, no domain.
CONTEXTUAL = """\
Ако търсите достоверни научни източници, порталът Nauka е сред най-старите
и утвърдени в страната. Съдържанието е безплатно.
"""

# Answer with negative framing near the mention.
NEGATIVE = """\
Nauka.bg има богат архив, но част от материалите са остарели и неактуални,
а навигацията е проблем за нови читатели.
"""

CITATIONS = """\
According to https://nauka.bg/article/42?utm_source=chatgpt&id=7 and
[this overview](https://obekti.bg/nauka/), plus https://bnr.bg/science.
See also https://nauka.bg/article/42?id=7#top for the same piece.
"""

ROBOTS_BLOCKED = """\
User-agent: *
Allow: /

User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /wp-admin/
"""

ROBOTS_WILDCARD_BLOCK = """\
User-agent: *
Disallow: /
"""

HTML_PAGE = """\
<html><head><title>Best hosting for WordPress</title>
<meta name="description" content="A comparison of 8 providers.">
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[{"@type":"FAQPage"},{"@type":"Organization"}]}
</script></head>
<body><h1>Best hosting for WordPress in 2026</h1>
<p>The short answer: SuperHost wins for 24/7 weekend support, at 12 EUR per month.</p>
<h2>How we tested</h2><p>We measured 8 providers over 90 days.</p>
<h2>Често задавани въпроси</h2>
<h3>Is it worth paying more for managed hosting?</h3>
<table><tr><th>Provider</th><th>Price</th></tr><tr><td>SuperHost</td><td>12 EUR</td></tr></table>
</body></html>
"""


def test_mention_detection() -> None:
    print("\nmention detection")
    pats = aeolib.build_mention_patterns(BRAND)

    r = aeolib.analyze_response(GEMINI_LIST, BRAND, pats)
    check("linked brand in list is found", r["mentioned"], "yes")
    check("strongest evidence wins (url beats contextual)", r["match_type"], "url")
    check_true("description is the surrounding sentence",
               "най-голямата" in r["description"], r["description"][:80])

    r2 = aeolib.analyze_response(ABSENT, BRAND, pats)
    check("absent brand reported as no", r2["mentioned"], "no")
    check_true("competitors still collected when absent",
               {"obekti.bg", "kaldata.com", "bnr.bg"} <= set(r2["competitors"]),
               str(r2["competitors"]))

    r3 = aeolib.analyze_response(CONTEXTUAL, BRAND, pats)
    check("bare name + context word counts", r3["mentioned"], "yes")
    check("contextual match is labelled as such", r3["match_type"], "contextual")

    r4 = aeolib.analyze_response("", BRAND, pats)
    check("empty answer is an error, not a miss", r4["mentioned"], "error")


def test_positions() -> None:
    print("\nlist positions")
    pats = aeolib.build_mention_patterns(BRAND)
    r = aeolib.analyze_response(GEMINI_LIST, BRAND, pats)
    check("own brand ranked first", r["best_position"], 1)
    check("list size captured", r["list_positions"][0]["list_size"], 4)

    entries = aeolib.extract_brand_list(ABSENT, pats)
    check("bullet list parsed", len(entries), 3)
    check("second entry position", entries[1].position, 2)
    check_true("no false own-brand match", not any(e.is_own for e in entries))


def test_competitors() -> None:
    print("\ncompetitor extraction")
    comps = aeolib.find_competitors(
        "Compare nauka.bg with obekti.bg and see report.pdf plus main.py notes.",
        "nauka.bg", ["offnews.bg"])
    check("own domain excluded", "nauka.bg" not in comps, True)
    check("real competitor found", "obekti.bg" in comps, True)
    check("file names are not domains", [c for c in comps if c in ("report.pdf", "main.py")], [])

    subs = aeolib.find_competitors("See nauka.offnews.bg for news", "nauka.bg", [])
    check("subdomain of a competitor kept", "nauka.offnews.bg" in subs, True)


def test_sentiment() -> None:
    print("\nsentiment")
    check("negative wording detected", aeolib.analyze_sentiment(NEGATIVE), "negative")
    check("positive wording detected",
          aeolib.analyze_sentiment("Отличен и надежден източник, силно препоръчвам."),
          "positive")
    check("english positive detected",
          aeolib.analyze_sentiment("A reliable and comprehensive resource, highly recommend."),
          "positive")
    check("neutral by default", aeolib.analyze_sentiment("It exists."), "neutral")


def test_citations() -> None:
    print("\ncitations")
    urls = aeolib.extract_citations(CITATIONS)
    check("tracking params stripped and fragment deduped",
          "https://nauka.bg/article/42?id=7" in urls, True)
    check("markdown link url captured", "https://obekti.bg/nauka" in urls, True)
    check("trailing period trimmed", "https://bnr.bg/science" in urls, True)
    check("deduped", len(urls), 3)


def test_robots() -> None:
    print("\nrobots.txt parsing")
    check("explicit block detected",
          aeoweb.bot_status(ROBOTS_BLOCKED, "GPTBot")["allowed"], False)
    check("path-only disallow is not a block",
          aeoweb.bot_status(ROBOTS_BLOCKED, "ClaudeBot")["allowed"], True)
    check("path rule recorded",
          aeoweb.bot_status(ROBOTS_BLOCKED, "ClaudeBot")["partial"], ["/wp-admin/"])
    check("unlisted bot inherits allow",
          aeoweb.bot_status(ROBOTS_BLOCKED, "PerplexityBot")["allowed"], True)
    check("wildcard block applies to everyone",
          aeoweb.bot_status(ROBOTS_WILDCARD_BLOCK, "PerplexityBot")["allowed"], False)
    check("no robots.txt means allowed",
          aeoweb.bot_status(None, "GPTBot")["allowed"], True)


def test_page_signals() -> None:
    print("\npage signals")
    s = aeoweb.extract_page_signals(HTML_PAGE)
    check("title", s["title"], "Best hosting for WordPress")
    check("h1", s["h1"], "Best hosting for WordPress in 2026")
    check_true("first paragraph is the answer sentence",
               s["first_paragraph"].startswith("The short answer"), s["first_paragraph"])
    check("schema types from @graph", s["schema"]["types"], ["FAQPage", "Organization"])
    check("faq signals found", len(s["faq_signals"]), 2)
    check("table sampled", len(s["tables"]), 1)
    check_true("numeric facts counted", s["numbers_found"] >= 3, str(s["numbers_found"]))


def test_response_files(tmp: Path) -> None:
    print("\nresponse files")
    f = tmp / "p01__chatgpt.txt"
    aeolib.write_response_stub(f, "p01", "Which is best?", "chatgpt", "2026-08-01")
    parsed = aeolib.parse_response_file(f)
    check("stub id", parsed["id"], "p01")
    check("stub model", parsed["model"], "chatgpt")
    check("placeholder body treated as empty", parsed["body"], "")

    f.write_text("PROMPT: Which is best?\nMODEL: gemini\nDATE: 2026-08-01\n"
                 + "=" * 60 + "\n\nAnswer text here.\n", encoding="utf-8")
    parsed = aeolib.parse_response_file(f)
    check("legacy header without ID still parses", parsed["model"], "gemini")
    check("body extracted", parsed["body"], "Answer text here.")


def test_metrics() -> None:
    print("\nmetrics")
    import aeoreport
    run = {
        "date": "2026-08-01",
        "brand": {"brand": "Nauka.bg", "domain": "nauka.bg"},
        "results": [
            {"prompt_id": "p01", "prompt": "best?", "intent": "high", "model": "chatgpt",
             "mentioned": "no", "description": "", "competitors": ["obekti.bg"],
             "sentiment": "neutral", "best_position": None, "cited_urls": []},
            {"prompt_id": "p01", "prompt": "best?", "intent": "high", "model": "gemini",
             "mentioned": "yes", "description": "a" * 60, "competitors": ["obekti.bg"],
             "sentiment": "positive", "best_position": 1,
             "cited_urls": ["https://nauka.bg/x"]},
            {"prompt_id": "p02", "prompt": "where?", "intent": "low", "model": "gemini",
             "mentioned": "error", "description": "", "competitors": [],
             "sentiment": "neutral", "best_position": None, "cited_urls": []},
        ],
    }
    m = aeoreport.compute_metrics(run)
    check("errors excluded from the denominator", m["overall"]["total"], 2)
    check("visibility percentage", m["overall"]["pct"], 50)
    check("errors counted separately", m["overall"]["errors"], 1)
    check("lost high-intent prompt surfaced", len(m["lost_prompts"]), 1)
    check("share of voice includes own brand",
          any(s["is_own"] and s["mentions"] == 1 for s in m["share_of_voice"]), True)
    check("average position", m["avg_position"], 1.0)


def main() -> int:
    import tempfile
    print("aeo selftest")
    test_mention_detection()
    test_positions()
    test_competitors()
    test_sentiment()
    test_citations()
    test_robots()
    test_page_signals()
    with tempfile.TemporaryDirectory() as d:
        test_response_files(Path(d))
    test_metrics()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
