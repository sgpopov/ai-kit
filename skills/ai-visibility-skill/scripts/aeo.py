#!/usr/bin/env python3
"""aeo — AI visibility toolkit.

One command per step of the workflow:

    python aeo.py init      <domain>        set up a workspace
    python aeo.py run       [--models ...]  create empty answer files to fill in
    python aeo.py collect   [--models ...]  fill them automatically (OpenRouter key)
    python aeo.py analyze                   score every answer
    python aeo.py report                    build report.html + summary.md
    python aeo.py tech                      robots.txt / llms.txt / sitemap / schema
    python aeo.py page      <url>           extract AEO signals from one page
    python aeo.py schema    <spec.json>     generate JSON-LD
    python aeo.py llmstxt                   generate llms.txt from the sitemap
    python aeo.py selftest                  verify the detection logic

Standard library only. Run with -h on any subcommand for its options.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date as _date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Windows consoles still default to a legacy code page, which turns any em
# dash or Cyrillic character in the output into a crash. Files are always
# written as UTF-8; this makes the terminal agree.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

import aeolib  # noqa: E402
import aeoreport  # noqa: E402
import aeoweb  # noqa: E402

DEFAULT_MODELS = ["chatgpt", "gemini", "perplexity", "claude"]

# OpenRouter slugs for `collect`. `:online` forces live web search, which is
# what a real user's assistant does — without it you measure stale training
# memory instead of today's answer.
OPENROUTER_MODELS = {
    "chatgpt": "openai/gpt-5-mini:online",
    "gemini": "google/gemini-2.5-flash:online",
    "claude": "anthropic/claude-sonnet-4.6:online",
    "perplexity": "perplexity/sonar",
    "grok": "x-ai/grok-4-fast:online",
    "deepseek": "deepseek/deepseek-chat:online",
}


def ws(args) -> Path:
    return Path(args.workspace).resolve()


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _load_brand(w: Path) -> aeolib.Brand:
    f = w / "brand.json"
    if not f.exists():
        die(f"no brand.json in {w} — run `aeo.py init <domain>` first")
    return aeolib.Brand.load(f)


# --------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------

BRAND_TEMPLATE = {
    "brand": "",
    "domain": "",
    "aliases": [],
    "keywords": [],
    "competitors": [],
    "language": "auto",
    "positioning": "",
}

PROMPTS_TEMPLATE = [
    {"id": "p01", "text": "", "category": "comparison", "intent": "high"},
]


def cmd_init(args) -> None:
    w = ws(args)
    w.mkdir(parents=True, exist_ok=True)
    (w / "runs").mkdir(exist_ok=True)

    brand_file = w / "brand.json"
    if brand_file.exists() and not args.force:
        print(f"brand.json already exists at {brand_file} (use --force to overwrite)")
    else:
        domain = args.domain.strip().lower().replace("https://", "").replace("http://", "")
        domain = domain.rstrip("/").removeprefix("www.")
        data = dict(BRAND_TEMPLATE)
        data["domain"] = domain
        data["brand"] = args.name or domain.split(".")[0].title()
        brand_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
        print(f"created {brand_file}")

    prompts_file = w / "prompts.json"
    if not prompts_file.exists():
        prompts_file.write_text(
            json.dumps(PROMPTS_TEMPLATE, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(f"created {prompts_file}")

    print(f"\nworkspace ready: {w}")
    print("next: fill in brand.json (aliases, keywords, competitors) and prompts.json")


# --------------------------------------------------------------------------
# run / collect
# --------------------------------------------------------------------------


def _run_dir(w: Path, run_id: str) -> Path:
    return w / "runs" / run_id


def cmd_run(args) -> None:
    w = ws(args)
    brand = _load_brand(w)
    prompts = aeolib.load_prompts(w / "prompts.json")
    if not prompts or not prompts[0]["text"]:
        die("prompts.json is empty — add the questions your buyers actually ask")

    run_id = args.run or _date.today().isoformat()
    models = args.models or DEFAULT_MODELS
    rd = _run_dir(w, run_id)
    (rd / "responses").mkdir(parents=True, exist_ok=True)

    created = skipped = 0
    for p in prompts:
        for model in models:
            f = rd / "responses" / f"{p['id']}__{model}.txt"
            if f.exists():
                skipped += 1
                continue
            aeolib.write_response_stub(f, p["id"], p["text"], model, run_id)
            created += 1

    (rd / "run.json").write_text(json.dumps(
        {"run_id": run_id, "models": models, "domain": brand.domain,
         "prompt_count": len(prompts)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    print(f"run {run_id}: {created} file(s) created, {skipped} kept")
    print(f"  {rd / 'responses'}")
    print("\nPaste each model's answer below the ==== line, replacing '(no response)'.")
    print("Then: python aeo.py analyze")


def _openrouter_call(model_slug: str, prompt: str, api_key: str,
                     timeout: int = 180) -> str:
    body = json.dumps({
        "model": model_slug,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "AI Visibility Skill",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"] or ""


def cmd_collect(args) -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        die("OPENROUTER_API_KEY is not set. Either export it, or use "
            "`aeo.py run` and paste answers manually (no key needed).")

    w = ws(args)
    _load_brand(w)
    prompts = aeolib.load_prompts(w / "prompts.json")
    run_id = args.run or _date.today().isoformat()
    models = args.models or ["chatgpt", "gemini", "perplexity"]

    unknown = [m for m in models if m not in OPENROUTER_MODELS]
    if unknown:
        die(f"unknown model(s): {', '.join(unknown)}. "
            f"Known: {', '.join(OPENROUTER_MODELS)}")

    rd = _run_dir(w, run_id)
    (rd / "responses").mkdir(parents=True, exist_ok=True)

    total = len(prompts) * len(models)
    done = failed = 0
    for p in prompts:
        for model in models:
            f = rd / "responses" / f"{p['id']}__{model}.txt"
            if f.exists() and not args.force:
                existing = aeolib.parse_response_file(f)
                if existing["body"]:
                    done += 1
                    continue
            try:
                answer = _openrouter_call(OPENROUTER_MODELS[model], p["text"], api_key)
            except (urllib.error.URLError, KeyError, TimeoutError, OSError) as e:
                print(f"  ! {p['id']} {model}: {type(e).__name__}: {str(e)[:90]}",
                      file=sys.stderr)
                failed += 1
                answer = ""
            aeolib.write_response_stub(f, p["id"], p["text"], model, run_id)
            if answer:
                f.write_text(
                    f"ID: {p['id']}\nPROMPT: {p['text']}\nMODEL: {model}\n"
                    f"DATE: {run_id}\n{'=' * 60}\n\n{answer}\n", encoding="utf-8")
            done += 1
            print(f"  [{done}/{total}] {p['id']} {model}"
                  + ("" if answer else "  (empty)"))

    (rd / "run.json").write_text(json.dumps(
        {"run_id": run_id, "models": models, "collected": done, "failed": failed},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ncollected {done - failed}/{total} answers into {rd / 'responses'}")


# --------------------------------------------------------------------------
# analyze
# --------------------------------------------------------------------------


def cmd_analyze(args) -> None:
    w = ws(args)
    brand = _load_brand(w)
    prompt_list = aeolib.load_prompts(w / "prompts.json")
    prompts = {p["id"]: p for p in prompt_list}
    # Answer files written by hand (or exported from another tool) often carry
    # only the prompt text, no id. Matching on text keeps their intent and
    # category instead of silently defaulting everything to "medium".
    by_text = {p["text"].strip().lower(): p for p in prompt_list if p["text"]}
    patterns = aeolib.build_mention_patterns(brand)

    run_ids = [args.run] if args.run else sorted(
        d.name for d in (w / "runs").iterdir() if d.is_dir()
    ) if (w / "runs").exists() else []
    if not run_ids:
        die("no runs found — `aeo.py run` first")

    for run_id in run_ids:
        rd = _run_dir(w, run_id)
        resp_dir = rd / "responses"
        if not resp_dir.exists():
            continue

        results: list[dict[str, Any]] = []
        empty = 0
        for f in sorted(resp_dir.glob("*.txt")) + sorted(resp_dir.glob("*.md")):
            parsed = aeolib.parse_response_file(f)
            pid = parsed["id"] or f.stem.split("__")[0]
            model = parsed["model"] or (
                f.stem.split("__")[1] if "__" in f.stem else "unknown")
            prompt = prompts.get(pid) or by_text.get(parsed["prompt"].strip().lower(), {})
            analysis = aeolib.analyze_response(parsed["body"], brand, patterns)
            if not parsed["body"]:
                empty += 1
            results.append({
                "prompt_id": prompt.get("id", pid),
                "prompt": prompt.get("text") or parsed["prompt"],
                "category": prompt.get("category", "topic"),
                "intent": prompt.get("intent", "medium"),
                "model": model,
                "file": f.name,
                **analysis,
            })

        out = {
            "date": run_id,
            "brand": {"brand": brand.brand, "domain": brand.domain},
            "results": results,
        }
        (rd / "results.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        m = aeoreport.compute_metrics(out)
        print(f"{run_id}: {len(results)} answers · visibility {m['overall']['pct']}% "
              f"({m['overall']['yes']}/{m['overall']['total']})"
              + (f" · {empty} still empty" if empty else ""))

    print("\nnext: python aeo.py report")


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------


def cmd_report(args) -> None:
    w = ws(args)
    brand = _load_brand(w)
    all_runs = aeoreport.load_runs(w)
    if not all_runs:
        die("no analyzed runs — `aeo.py analyze` first")

    # A run whose answers are all still placeholders would report 0% and read
    # as a collapse in visibility. Skip those rather than publish a lie.
    runs = [r for r in all_runs
            if any(x["mentioned"] != "error" for x in r["results"])]
    if not runs:
        die("every answer is still empty — paste the model answers first, "
            "or run `aeo.py collect`")
    for r in all_runs:
        if r not in runs:
            print(f"skipping run {r['date']}: no answers filled in yet")

    latest = runs[-1]
    metrics = aeoreport.compute_metrics(latest)
    timeline = aeoreport.build_timeline(runs)
    brand_d = {"brand": brand.brand, "domain": brand.domain}

    html_path = w / "report.html"
    md_path = w / "summary.md"
    html_path.write_text(aeoreport.html_report(metrics, brand_d, timeline), encoding="utf-8")
    md_path.write_text(aeoreport.markdown_summary(metrics, brand_d, timeline), encoding="utf-8")
    (w / "runs" / latest["date"] / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {html_path}")
    print(f"wrote {md_path}")
    o = metrics["overall"]
    print(f"\nvisibility {o['pct']}%  ·  {len(metrics['lost_prompts'])} lost prompt(s)"
          f"  ·  {len(metrics['weak_mentions'])} weak mention(s)")


# --------------------------------------------------------------------------
# technical audit
# --------------------------------------------------------------------------


def cmd_tech(args) -> None:
    w = ws(args)
    domain = args.domain
    if not domain:
        domain = _load_brand(w).domain
    base = aeoweb.base_url(domain)

    robots = aeoweb.fetch(base + "/robots.txt")
    llms = aeoweb.fetch(base + "/llms.txt")
    sitemap = aeoweb.fetch(base + "/sitemap.xml")
    home = aeoweb.fetch(base + "/")

    bots = [aeoweb.bot_status(robots.text, b) for b, _, _ in aeoweb.AI_BOTS]
    allowed = sum(1 for b in bots if b["allowed"])
    schema = aeoweb.parse_json_ld(home.text or "")

    # Weighted toward crawl access because nothing else matters if the bots
    # cannot read the page at all.
    score = (
        round(allowed / len(bots) * 50)
        + (20 if llms.ok else 0)
        + (10 if sitemap.ok else 0)
        + (20 if schema["ok"] else 0)
    )

    audit = {
        "domain": domain,
        "fetched_at": _date.today().isoformat(),
        "robots_txt": {"ok": robots.ok, "status": robots.status, "bytes": robots.size},
        "llms_txt": {"ok": llms.ok, "status": llms.status, "bytes": llms.size},
        "sitemap_xml": {"ok": sitemap.ok, "status": sitemap.status},
        "homepage_schema": schema,
        "bots": [dict(b, vendor=v, role=r)
                 for b, (_, v, r) in zip(bots, aeoweb.AI_BOTS)],
        "bots_allowed": f"{allowed}/{len(bots)}",
        "aeo_score": score,
    }

    out = w / "technical-audit.json" if (w / "brand.json").exists() else Path(
        "technical-audit.json")
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"AEO readiness: {score}/100   ({domain})\n")
    print(f"  robots.txt   {'found' if robots.ok else 'MISSING — ' + (robots.error or '')}")
    print(f"  llms.txt     {'found' if llms.ok else 'missing (worth adding)'}")
    print(f"  sitemap.xml  {'found' if sitemap.ok else 'MISSING'}")
    print(f"  homepage schema  {', '.join(schema['types']) if schema['ok'] else 'NONE — ' + str(schema['error'])}")
    print(f"\n  AI crawlers allowed: {allowed}/{len(bots)}")
    blocked = [dict(b, vendor=v, role=r) for b, (_, v, r) in zip(bots, aeoweb.AI_BOTS)
               if not b["allowed"]]
    for b in blocked:
        print(f"    BLOCKED  {b['bot']:<22} {b['vendor']} ({b['role']}) — {b['reason']}")
    if not blocked:
        print("    none blocked")
    print(f"\nwrote {out}")


# --------------------------------------------------------------------------
# page signals
# --------------------------------------------------------------------------


def cmd_page(args) -> None:
    signals = aeoweb.fetch_page_signals(args.url)
    if "error" in signals:
        die(f"{signals['error']} ({args.url})")

    out = Path(args.out) if args.out else ws(args) / "page-signals.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(signals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{args.url}  (HTTP {signals['status']}, {signals['word_count']} words)\n")
    print(f"  title      {signals['title'] or '— MISSING'}")
    print(f"  h1         {signals['h1'] or '— MISSING'}")
    print(f"  meta desc  {(signals['meta_description'] or '— MISSING')[:100]}")
    print(f"  headings   {len(signals['headings'])}  "
          f"(~{signals['avg_words_between_headings']} words between each)")
    print(f"  tables     {len(signals['tables'])}")
    print(f"  FAQ-ish    {len(signals['faq_signals'])}")
    print(f"  schema     {', '.join(signals['schema']['types']) if signals['schema']['ok'] else 'NONE'}")
    print(f"  numbers    {signals['numbers_found']} numeric facts detected")
    print(f"\nwrote {out}")
    print("Hand this file to the model with references/content-rubric.md to score it.")


# --------------------------------------------------------------------------
# generators
# --------------------------------------------------------------------------


def _jsonld(spec: dict[str, Any]) -> dict[str, Any]:
    t = spec.get("type")
    base = {"@context": "https://schema.org", "@type": t}

    if t == "Organization":
        out = {**base, "name": spec["name"], "url": spec["url"]}
        for k in ("logo", "description", "email", "telephone"):
            if spec.get(k):
                out[k] = spec[k]
        if spec.get("knowsAbout"):
            out["knowsAbout"] = [s for s in spec["knowsAbout"] if s]
        if spec.get("sameAs"):
            out["sameAs"] = [s for s in spec["sameAs"] if s]
        return out

    if t == "FAQPage":
        return {**base, "mainEntity": [
            {"@type": "Question", "name": i["question"],
             "acceptedAnswer": {"@type": "Answer", "text": i["answer"]}}
            for i in spec.get("items", []) if i.get("question") and i.get("answer")
        ]}

    if t == "Article":
        out = {**base, "headline": spec["headline"],
               "author": {"@type": "Person", "name": spec["author"]},
               "datePublished": spec["datePublished"]}
        for k in ("dateModified", "image", "description"):
            if spec.get(k):
                out[k] = spec[k]
        return out

    if t == "Product":
        out = {**base, "name": spec["name"]}
        if spec.get("description"):
            out["description"] = spec["description"]
        out["offers"] = {
            "@type": "Offer",
            "price": str(spec["price"]),
            "priceCurrency": spec.get("priceCurrency", "EUR"),
            "availability": f"https://schema.org/{spec.get('availability', 'InStock')}",
        }
        return out

    die(f"unsupported schema type: {t!r} "
        "(Organization | FAQPage | Article | Product)")
    return {}


def cmd_schema(args) -> None:
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    specs = spec if isinstance(spec, list) else [spec]
    blocks = []
    for s in specs:
        payload = json.dumps(_jsonld(s), ensure_ascii=False, indent=2)
        blocks.append(f'<script type="application/ld+json">\n{payload}\n</script>')
    output = "\n\n".join(blocks)

    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(output)
    print("\nPaste into <head>. Validate at https://validator.schema.org",
          file=sys.stderr)


def cmd_llmstxt(args) -> None:
    w = ws(args)
    brand = _load_brand(w) if (w / "brand.json").exists() else None
    domain = args.domain or (brand.domain if brand else None)
    if not domain:
        die("need --domain or a brand.json")

    urls = args.url or aeoweb.resolve_sitemap_urls(domain, limit=args.limit)
    if not urls:
        die(f"no URLs — sitemap.xml unreachable for {domain}; pass --url repeatedly")

    title = args.title or (brand.brand if brand else domain)
    desc = args.description or (brand.positioning if brand else "")

    lines = [f"# {title}", ""]
    if desc:
        lines += [f"> {desc}", ""]
    lines += ["## Docs", ""]
    for u in urls:
        from urllib.parse import urlsplit
        p = urlsplit(u)
        label = p.path.strip("/") or p.netloc
        lines.append(f"- [{label}]({u})")

    out = Path(args.out) if args.out else w / "llms.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}  ({len(urls)} entries)")
    print("Add a one-line description after each link, then upload to "
          f"https://{domain}/llms.txt")


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------


def cmd_selftest(args) -> None:
    import aeo_selftest
    raise SystemExit(aeo_selftest.main())


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aeo", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-w", "--workspace", default=".",
                   help="workspace directory (default: current)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="create a workspace")
    s.add_argument("domain")
    s.add_argument("--name", help="brand display name")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("run", help="create empty answer files to paste into")
    s.add_argument("--models", nargs="+", help=f"default: {' '.join(DEFAULT_MODELS)}")
    s.add_argument("--run", help="run id (default: today)")
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("collect", help="fetch answers via OpenRouter (needs API key)")
    s.add_argument("--models", nargs="+",
                   help=f"available: {' '.join(OPENROUTER_MODELS)}")
    s.add_argument("--run", help="run id (default: today)")
    s.add_argument("--force", action="store_true", help="re-fetch non-empty answers")
    s.set_defaults(func=cmd_collect)

    s = sub.add_parser("analyze", help="score answers into results.json")
    s.add_argument("--run", help="only this run (default: all)")
    s.set_defaults(func=cmd_analyze)

    s = sub.add_parser("report", help="build report.html and summary.md")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("tech", help="crawl access + llms.txt + sitemap + schema")
    s.add_argument("domain", nargs="?")
    s.set_defaults(func=cmd_tech)

    s = sub.add_parser("page", help="extract AEO signals from a page")
    s.add_argument("url")
    s.add_argument("--out")
    s.set_defaults(func=cmd_page)

    s = sub.add_parser("schema", help="generate JSON-LD from a spec file")
    s.add_argument("spec")
    s.add_argument("--out")
    s.set_defaults(func=cmd_schema)

    s = sub.add_parser("llmstxt", help="generate llms.txt")
    s.add_argument("--domain")
    s.add_argument("--url", action="append", help="explicit URL (repeatable)")
    s.add_argument("--title")
    s.add_argument("--description")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--out")
    s.set_defaults(func=cmd_llmstxt)

    s = sub.add_parser("selftest", help="verify detection logic against fixtures")
    s.set_defaults(func=cmd_selftest)

    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
