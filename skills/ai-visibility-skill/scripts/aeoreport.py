"""Turn per-answer results into the numbers a decision gets made on.

Metrics mirror what commercial AI-visibility platforms report, plus the two
that actually tell you what to do next: visibility split by purchase intent,
and the list of high-intent prompts you lost and who won them.
"""

from __future__ import annotations

import html as html_mod
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

INTENT_ORDER = {"high": 0, "medium": 1, "low": 2}


def load_runs(workspace: Path) -> list[dict[str, Any]]:
    """All analyzed runs, oldest first."""
    runs = []
    runs_dir = workspace / "runs"
    if not runs_dir.exists():
        return runs
    for d in sorted(runs_dir.iterdir()):
        f = d / "results.json"
        if f.exists():
            runs.append(json.loads(f.read_text(encoding="utf-8")))
    return runs


def compute_metrics(run: dict[str, Any]) -> dict[str, Any]:
    results = run["results"]
    scored = [r for r in results if r["mentioned"] != "error"]
    errors = len(results) - len(scored)

    yes = sum(1 for r in scored if r["mentioned"] == "yes")
    overall = {
        "yes": yes,
        "total": len(scored),
        "pct": round(yes / len(scored) * 100) if scored else 0,
        "errors": errors,
    }

    by_model: dict[str, dict[str, int]] = defaultdict(lambda: {"yes": 0, "total": 0})
    for r in scored:
        by_model[r["model"]]["total"] += 1
        if r["mentioned"] == "yes":
            by_model[r["model"]]["yes"] += 1
    model_stats = [
        {"model": m, "yes": v["yes"], "total": v["total"],
         "pct": round(v["yes"] / v["total"] * 100) if v["total"] else 0}
        for m, v in sorted(by_model.items())
    ]

    by_intent: dict[str, dict[str, int]] = defaultdict(lambda: {"yes": 0, "total": 0})
    for r in scored:
        by_intent[r["intent"]]["total"] += 1
        if r["mentioned"] == "yes":
            by_intent[r["intent"]]["yes"] += 1
    intent_stats = [
        {"intent": i, "yes": by_intent[i]["yes"], "total": by_intent[i]["total"],
         "pct": round(by_intent[i]["yes"] / by_intent[i]["total"] * 100)}
        for i in ("high", "medium", "low") if by_intent[i]["total"]
    ]

    # Share of voice: one vote per answer a brand appears in, so a brand named
    # five times in one answer does not outweigh five separate appearances.
    own = run["brand"]["domain"].lower().replace("www.", "")
    sov: Counter[str] = Counter()
    for r in scored:
        brands = {c.lower() for c in r["competitors"]}
        if r["mentioned"] == "yes":
            brands.add(own)
        for b in brands:
            sov[b] += 1
    total_votes = sum(sov.values())
    share_of_voice = [
        {"brand": b, "mentions": n,
         "pct": round(n / total_votes * 100) if total_votes else 0,
         "is_own": b == own}
        for b, n in sov.most_common(15)
    ]
    if own not in sov:
        share_of_voice.append({"brand": own, "mentions": 0, "pct": 0, "is_own": True})

    positions = [r["best_position"] for r in scored if r.get("best_position")]
    avg_position = round(sum(positions) / len(positions), 1) if positions else None

    pos_by_model: dict[str, list[int]] = defaultdict(list)
    for r in scored:
        if r.get("best_position"):
            pos_by_model[r["model"]].append(r["best_position"])
    position_stats = [
        {"model": m, "avg": round(sum(v) / len(v), 1), "samples": len(v)}
        for m, v in sorted(pos_by_model.items())
    ]

    sentiment = Counter(r["sentiment"] for r in scored if r["mentioned"] == "yes")

    competitors = Counter()
    for r in scored:
        competitors.update(r["competitors"])

    citations = Counter()
    for r in scored:
        citations.update(r.get("cited_urls", []))

    # The action list: high-intent prompts where competitors were recommended
    # and you were not. Everything else in this report is context for these.
    lost = sorted(
        [
            {"id": r["prompt_id"], "prompt": r["prompt"], "model": r["model"],
             "intent": r["intent"], "winners": r["competitors"][:6]}
            for r in scored
            if r["mentioned"] == "no" and r["competitors"]
        ],
        key=lambda x: (INTENT_ORDER.get(x["intent"], 3), x["id"]),
    )

    weak = [
        {"id": r["prompt_id"], "prompt": r["prompt"], "model": r["model"],
         "description": r["description"], "sentiment": r["sentiment"],
         "position": r.get("best_position")}
        for r in scored
        if r["mentioned"] == "yes" and (
            r["sentiment"] == "negative"
            or (r.get("best_position") or 0) > 3
            or len(r["description"]) < 40
        )
    ]

    return {
        "date": run["date"],
        "overall": overall,
        "models": model_stats,
        "by_intent": intent_stats,
        "share_of_voice": share_of_voice,
        "avg_position": avg_position,
        "position_by_model": position_stats,
        "sentiment": dict(sentiment),
        "top_competitors": competitors.most_common(15),
        "top_citations": citations.most_common(20),
        "lost_prompts": lost,
        "weak_mentions": weak,
    }


def build_timeline(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for run in runs:
        m = compute_metrics(run)
        row: dict[str, Any] = {"date": m["date"], "overall": m["overall"]["pct"],
                               "_models": sorted(s["model"] for s in m["models"])}
        for ms in m["models"]:
            row[ms["model"]] = ms["pct"]
        out.append(row)
    return out


def comparable_delta(timeline: list[dict[str, Any]]) -> tuple[int, str] | None:
    """Change vs the previous run, but only when the runs are comparable.

    A run against three models and a run against one are not the same
    measurement. Reporting a drop between them invents a trend that is really
    just a different sample, so we withhold the number and say why.
    """
    if len(timeline) < 2:
        return None
    cur, prev = timeline[-1], timeline[-2]
    if cur.get("_models") != prev.get("_models"):
        return None
    return cur["overall"] - prev["overall"], prev["date"]


# --------------------------------------------------------------------------
# markdown
# --------------------------------------------------------------------------


def markdown_summary(m: dict[str, Any], brand: dict[str, Any],
                     timeline: list[dict[str, Any]] | None = None) -> str:
    L: list[str] = []
    name = brand.get("brand") or brand["domain"]
    L.append(f"# AI visibility — {name} ({brand['domain']})")
    L.append(f"\nRun date: **{m['date']}**\n")

    o = m["overall"]
    L.append(f"## Overall\n")
    L.append(f"- **Visibility: {o['pct']}%** — mentioned in {o['yes']} of {o['total']} answers")
    if m["avg_position"]:
        L.append(f"- Average position when listed: **{m['avg_position']}**")
    if o["errors"]:
        L.append(f"- {o['errors']} answer(s) missing or empty (not scored)")

    if timeline and len(timeline) > 1:
        d = comparable_delta(timeline)
        if d is None:
            L.append(f"- No trend vs {timeline[-2]['date']}: that run used a "
                     f"different set of models, so the two are not comparable")
        else:
            delta, prev_date = d
            arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "—")
            L.append(f"- Change since {prev_date}: **{arrow} {delta:+d} pp**")

    L.append("\n## By model\n")
    L.append("| Model | Mentioned | Visibility |")
    L.append("|---|---|---|")
    for s in m["models"]:
        L.append(f"| {s['model']} | {s['yes']}/{s['total']} | {s['pct']}% |")

    if m["by_intent"]:
        L.append("\n## By purchase intent\n")
        L.append("| Intent | Mentioned | Visibility |")
        L.append("|---|---|---|")
        for s in m["by_intent"]:
            L.append(f"| {s['intent']} | {s['yes']}/{s['total']} | {s['pct']}% |")

    L.append("\n## Share of voice\n")
    L.append("| Brand | Answers | Share |")
    L.append("|---|---|---|")
    for s in m["share_of_voice"][:12]:
        mark = " **(you)**" if s["is_own"] else ""
        L.append(f"| {s['brand']}{mark} | {s['mentions']} | {s['pct']}% |")

    if m["lost_prompts"]:
        L.append("\n## Prompts you lost (highest intent first)\n")
        for p in m["lost_prompts"][:20]:
            winners = ", ".join(p["winners"]) or "—"
            L.append(f"- **[{p['intent']}]** `{p['model']}` — {p['prompt']}")
            L.append(f"  - Recommended instead: {winners}")

    if m["weak_mentions"]:
        L.append("\n## Mentions worth fixing\n")
        L.append("_Present but buried, vague, or negatively framed._\n")
        for w in m["weak_mentions"][:15]:
            pos = f" (position {w['position']})" if w["position"] else ""
            L.append(f"- `{w['model']}` — {w['prompt']}{pos}")
            L.append(f"  - \"{w['description'][:220]}\"")

    if m["top_citations"]:
        L.append("\n## Most-cited pages\n")
        L.append("_Concrete outreach targets — these pages are already inside the answers._\n")
        for url, n in m["top_citations"][:15]:
            L.append(f"- {n}× {url}")

    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------
# html
# --------------------------------------------------------------------------

_CSS = """
:root{--bg:#faf9f7;--card:#fff;--ink:#1c1b19;--muted:#6b675f;--line:#e8e4dd;
--accent:#c15f3c;--accent2:#8a8578;--good:#5d7a52;--warn:#c9a227}
@media (prefers-color-scheme:dark){:root{--bg:#171614;--card:#201f1c;--ink:#f0ede7;
--muted:#a29d93;--line:#332f2a;--accent:#e08a63;--accent2:#7d786c;--good:#8fae82}}
*{box-sizing:border-box}
body{margin:0;padding:32px 20px;background:var(--bg);color:var(--ink);
font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1000px;margin:0 auto}
h1{font-size:28px;margin:0 0 4px;font-weight:650;letter-spacing:-.01em}
h2{font-size:18px;margin:34px 0 12px;font-weight:600}
.sub{color:var(--muted);margin:0 0 28px;font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:20px;margin-bottom:14px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
.tile .n{font-size:32px;font-weight:650;letter-spacing:-.02em;line-height:1.1}
.tile .l{color:var(--muted);font-size:12px;text-transform:uppercase;
letter-spacing:.06em;margin-top:6px}
.delta{font-size:13px;font-weight:600}
.up{color:var(--good)}.down{color:var(--accent)}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;color:var(--muted);font-weight:600;font-size:12px;
text-transform:uppercase;letter-spacing:.05em;padding:6px 8px;border-bottom:1px solid var(--line)}
td{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:middle}
tr:last-child td{border-bottom:none}
.bar{height:8px;border-radius:4px;background:var(--accent2);opacity:.45;min-width:2px}
.bar.own{background:var(--accent);opacity:1}
.scroll{overflow-x:auto}
.pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;
font-weight:600;text-transform:uppercase;letter-spacing:.04em;border:1px solid var(--line)}
.pill.high{background:var(--accent);color:#fff;border-color:transparent}
.pill.medium{background:var(--warn);color:#2a2510;border-color:transparent}
.pill.low{background:transparent;color:var(--muted)}
.lost{border-left:3px solid var(--accent);padding:10px 0 10px 14px;margin-bottom:12px}
.lost .q{font-weight:600}
.lost .w{color:var(--muted);font-size:13px;margin-top:3px}
.quote{color:var(--muted);font-size:13px;font-style:italic;margin-top:3px}
code{background:var(--bg);padding:1px 5px;border-radius:4px;font-size:12px}
a{color:var(--accent);text-decoration:none;word-break:break-all}
a:hover{text-decoration:underline}
.empty{color:var(--muted);font-size:14px}
"""


def _e(s: Any) -> str:
    return html_mod.escape(str(s if s is not None else ""))


def _bar(pct: float, own: bool = False, scale: float = 1.0) -> str:
    w = max(2, min(100, pct * scale))
    return f'<div class="bar{" own" if own else ""}" style="width:{w:.1f}%"></div>'


def html_report(m: dict[str, Any], brand: dict[str, Any],
                timeline: list[dict[str, Any]]) -> str:
    name = brand.get("brand") or brand["domain"]
    o = m["overall"]
    P: list[str] = []

    delta_html = ""
    if len(timeline) > 1:
        cmp = comparable_delta(timeline)
        if cmp is None:
            delta_html = ('<div class="delta" style="color:var(--muted)">'
                          'no trend — previous run used other models</div>')
        else:
            d, prev_date = cmp
            cls = "up" if d > 0 else ("down" if d < 0 else "")
            arrow = "▲" if d > 0 else ("▼" if d < 0 else "—")
            delta_html = (f'<div class="delta {cls}">{arrow} {d:+d} pp '
                          f'vs {_e(prev_date)}</div>')

    P.append(f"<h1>AI visibility — {_e(name)}</h1>")
    P.append(f'<p class="sub">{_e(brand["domain"])} · run {_e(m["date"])} · '
             f'{o["total"]} answers analyzed'
             + (f' · {o["errors"]} missing' if o["errors"] else "") + "</p>")

    P.append('<div class="tiles">')
    P.append(f'<div class="tile"><div class="n">{o["pct"]}%</div>'
             f'<div class="l">Visibility</div>{delta_html}</div>')
    P.append(f'<div class="tile"><div class="n">{o["yes"]}/{o["total"]}</div>'
             f'<div class="l">Answers mentioning you</div></div>')
    pos = m["avg_position"] if m["avg_position"] else "—"
    P.append(f'<div class="tile"><div class="n">{pos}</div>'
             f'<div class="l">Avg. position in lists</div></div>')
    own_sov = next((s["pct"] for s in m["share_of_voice"] if s["is_own"]), 0)
    P.append(f'<div class="tile"><div class="n">{own_sov}%</div>'
             f'<div class="l">Share of voice</div></div>')
    P.append("</div>")

    # by model
    P.append("<h2>By model</h2><div class='card scroll'><table>")
    P.append("<tr><th>Model</th><th>Mentioned</th><th style='width:45%'>Visibility</th><th></th></tr>")
    for s in m["models"]:
        P.append(f"<tr><td><code>{_e(s['model'])}</code></td>"
                 f"<td>{s['yes']}/{s['total']}</td>"
                 f"<td>{_bar(s['pct'])}</td><td>{s['pct']}%</td></tr>")
    P.append("</table></div>")

    if m["by_intent"]:
        P.append("<h2>By purchase intent</h2><div class='card scroll'><table>")
        P.append("<tr><th>Intent</th><th>Mentioned</th>"
                 "<th style='width:45%'>Visibility</th><th></th></tr>")
        for s in m["by_intent"]:
            P.append(f"<tr><td><span class='pill {s['intent']}'>{_e(s['intent'])}</span></td>"
                     f"<td>{s['yes']}/{s['total']}</td>"
                     f"<td>{_bar(s['pct'])}</td><td>{s['pct']}%</td></tr>")
        P.append("</table></div>")

    # share of voice
    P.append("<h2>Share of voice</h2><div class='card scroll'><table>")
    P.append("<tr><th>Brand</th><th>Answers</th><th style='width:45%'></th><th></th></tr>")
    top = max((s["pct"] for s in m["share_of_voice"]), default=1) or 1
    for s in m["share_of_voice"][:12]:
        label = f"<strong>{_e(s['brand'])}</strong> (you)" if s["is_own"] else _e(s["brand"])
        P.append(f"<tr><td>{label}</td><td>{s['mentions']}</td>"
                 f"<td>{_bar(s['pct'], s['is_own'], 100 / top)}</td><td>{s['pct']}%</td></tr>")
    P.append("</table></div>")

    # timeline
    if len(timeline) > 1:
        P.append("<h2>Trend</h2><div class='card scroll'><table>")
        cols = sorted({c for row in timeline for c in row
                       if c not in ("date", "overall", "_models")})
        P.append("<tr><th>Date</th><th>Overall</th>"
                 + "".join(f"<th>{_e(c)}</th>" for c in cols) + "</tr>")
        for row in timeline:
            cells = "".join(
                f"<td>{row[c]}%</td>" if c in row else "<td>—</td>" for c in cols)
            P.append(f"<tr><td>{_e(row['date'])}</td>"
                     f"<td><strong>{row['overall']}%</strong></td>{cells}</tr>")
        P.append("</table></div>")

    # lost prompts
    P.append("<h2>Prompts you lost</h2>")
    if m["lost_prompts"]:
        P.append("<div class='card'>")
        for p in m["lost_prompts"][:25]:
            winners = ", ".join(_e(w) for w in p["winners"]) or "—"
            P.append(f"<div class='lost'><span class='pill {p['intent']}'>{_e(p['intent'])}</span> "
                     f"<span class='q'>{_e(p['prompt'])}</span>"
                     f"<div class='w'><code>{_e(p['model'])}</code> recommended: {winners}</div></div>")
        P.append("</div>")
    else:
        P.append("<div class='card empty'>None — you appear wherever competitors do.</div>")

    if m["weak_mentions"]:
        P.append("<h2>Mentions worth fixing</h2><div class='card'>")
        for w in m["weak_mentions"][:15]:
            pos = f" · position {w['position']}" if w["position"] else ""
            P.append(f"<div class='lost'><span class='q'>{_e(w['prompt'])}</span>"
                     f"<div class='w'><code>{_e(w['model'])}</code> · {_e(w['sentiment'])}{pos}</div>"
                     f"<div class='quote'>“{_e(w['description'][:260])}”</div></div>")
        P.append("</div>")

    if m["top_citations"]:
        P.append("<h2>Most-cited pages</h2><div class='card scroll'><table>")
        P.append("<tr><th>#</th><th>Page</th></tr>")
        for url, n in m["top_citations"][:20]:
            P.append(f"<tr><td>{n}×</td><td><a href='{_e(url)}' target='_blank' "
                     f"rel='noopener'>{_e(url)}</a></td></tr>")
        P.append("</table></div>")

    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>AI visibility — {_e(name)}</title><style>{_CSS}</style></head>"
        f"<body><div class='wrap'>{''.join(P)}</div></body></html>"
    )
