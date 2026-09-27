# Workspace format

Everything is plain text. Read it, edit it, put it in git, hand it to another
tool.

```
<workspace>/
├── brand.json
├── prompts.json
├── runs/
│   └── 2026-08-01/
│       ├── run.json
│       ├── responses/
│       │   ├── p01__chatgpt.txt
│       │   └── p01__gemini.txt
│       ├── results.json
│       └── metrics.json
├── report.html
├── summary.md
├── technical-audit.json
└── page-signals.json
```

## brand.json

```json
{
  "brand": "Example",
  "domain": "example.com",
  "aliases": ["Example Ltd", "Примерна фирма"],
  "keywords": ["ExampleCloud", "Example Suite"],
  "competitors": ["competitor-a.com", "competitor-b.com"],
  "context_words": [],
  "language": "auto",
  "positioning": "Managed WordPress hosting for Bulgarian agencies, with weekend support."
}
```

| Field | Effect |
|---|---|
| `domain` | Weight-10 mention signal. Bare host, no scheme, no `www`. |
| `brand` | Weight-9. The display name. |
| `aliases` | Weight-9 each. Add every real-world variant, including other scripts and legal-entity forms. This is the most common cause of undercounting. |
| `keywords` | Weight-7 each. Distinctive product names that identify the brand without naming it. Do not put generic category words here — they cause false positives. |
| `competitors` | Matched by substring, so `example.com` also catches `shop.example.com`. Unlisted competitors are still discovered automatically. |
| `context_words` | Words that, near a bare brand name, make a match credible ("website", "platform", "brand"). Defaults cover Bulgarian and English; override for other languages. |
| `positioning` | Not used in scoring. Used by you when judging whether the model's description is right, and as the `llms.txt` description. |

## prompts.json

```json
[
  {"id": "p01", "text": "…", "category": "comparison", "intent": "high"}
]
```

`id` must stay stable across runs — it is how answers line up over time.
`category` is one of `brand`, `topic`, `educational`, `comparison`. `intent` is
`high`, `medium`, or `low`; omitted values are derived from `category`.

A bare array of strings also works for a quick start; ids are then assigned by
position, which means inserting a prompt later reshuffles the history.

## Answer files

One file per prompt × model, named `<prompt_id>__<model>.txt`. Both `.txt` and
`.md` are read.

```
ID: p01
PROMPT: Which hosting provider is best for a WordPress site?
MODEL: chatgpt
DATE: 2026-08-01
============================================================

<the assistant's full answer, verbatim, including links>
```

Rules that matter:

- Everything after the `====` line is the answer. The header ends there.
- `(no response)` — the placeholder written by `aeo.py run` — is treated as
  empty, and empty answers are excluded from percentages rather than counted as
  misses. This is what lets a user fill the set in over several sittings.
- **Paste links.** Citations are extracted from the answer body and become the
  "most-cited pages" target list.
- Headers without `ID:` still work: the prompt is matched by its text, and
  failing that by the filename prefix. That makes it possible to import answer
  files exported from other tools.

## results.json

```json
{
  "date": "2026-08-01",
  "brand": {"brand": "Example", "domain": "example.com"},
  "results": [
    {
      "prompt_id": "p01",
      "prompt": "…",
      "category": "comparison",
      "intent": "high",
      "model": "chatgpt",
      "file": "p01__chatgpt.txt",
      "mentioned": "yes",
      "match_type": "url",
      "description": "The sentence the brand appears in.",
      "competitors": ["competitor-a.com"],
      "sentiment": "positive",
      "list_positions": [{"list_index": 0, "position": 2, "list_size": 5}],
      "best_position": 2,
      "cited_urls": ["https://…"],
      "brands_in_lists": [{"brand": "…", "domain": "…", "position": 1,
                           "list_size": 5, "is_own": false}]
    }
  ]
}
```

`mentioned` is `yes`, `no`, or `error` (empty/missing answer — excluded from
the denominator).

`match_type` records *what* matched: `url`, `www`, `domain`, `alias`, `brand`,
`keyword`, or `contextual`. A run where most hits are `contextual` deserves
scrutiny — that is the weakest evidence and the likeliest source of false
positives.

## metrics.json

Written by `report`. Aggregates for the most recent run with filled answers:
`overall`, `models`, `by_intent`, `share_of_voice`, `avg_position`,
`position_by_model`, `sentiment`, `top_competitors`, `top_citations`,
`lost_prompts`, `weak_mentions`.

Two definitions worth knowing when quoting these numbers:

- **Share of voice** counts one vote per answer a brand appears in, so a brand
  named five times inside a single answer does not outweigh five separate
  appearances.
- **`weak_mentions`** flags answers where the brand is present but the mention
  is negative, ranked below third, or described in fewer than 40 characters.

## Adding a model

Model names are free-form strings — they come from the filename and the
`MODEL:` header, and nothing validates them. To track Copilot, use
`p01__copilot.txt` with `MODEL: copilot`. It will appear in the report on its
own row.

For `aeo.py collect`, the model must exist in `OPENROUTER_MODELS` in
`scripts/aeo.py`; adding one is a single line.
