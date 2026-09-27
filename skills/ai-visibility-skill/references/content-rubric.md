# Scoring a page for AI citation

Run `aeo.py page <url>` first — it produces `page-signals.json` with the parts
of the page that matter here. Score against these seven criteria and give the
user rewritten text, not advice.

The question behind every criterion: **can an assistant lift a correct,
quotable answer out of this page without reading all of it?**

## The seven criteria

Use these exact keys so results stay comparable across pages and runs.

### 1. `first_sentence` — severity: critical

Does the page answer its own headline question in the first sentence, before
any preamble?

Assistants extract the top of a page most reliably. A page that opens with
"In today's fast-moving landscape…" has buried the answer below the extraction
window.

- **Pass:** first sentence states the answer or the core claim outright.
- **Fail:** intro, context-setting, or brand throat-clearing comes first.
- **Fix:** move the answer up. *"The short answer: X, because Y."* Keep the
  context — put it second.

### 2. `summary` — severity: major

Is there a visually distinct "key takeaways" block near the top?

- **Pass:** a labelled block of 3-5 short bullets, each a standalone fact.
- **Fail:** no summary, or a paragraph pretending to be one.
- **Fix:** write the bullets. Each must survive being quoted alone, with no
  pronouns pointing at surrounding text.

### 3. `numbers` — severity: minor

Does the page contain concrete figures, or only adjectives?

Specific numbers are quotable and attributable; "significantly faster" is not.
`page-signals.json` reports `numbers_found` as a rough count — verify they are
real facts and not prices in a nav bar.

- **Pass:** measured claims with figures, dates, percentages, prices.
- **Fail:** generalities throughout.
- **Fix:** replace three vague claims with measured ones. If the number is not
  known, that is itself worth telling the user.

### 4. `faq` — severity: major

Is there an FAQ, and does it use real user language?

Most FAQs are invented backwards by someone in marketing and answered in
corporate register. Models were trained on how people actually ask.

- **Pass:** questions phrased the way a person would type them into a chat.
- **Fail:** no FAQ, or questions like *"What are the benefits of using our
  solution?"*
- **Fix:** pull questions verbatim from support tickets, sales calls, and site
  search. Rewrite:
  - ✗ *"What are the benefits of AI-assisted WordPress hosting?"*
  - ✓ *"Is it worth paying extra for hosting with an AI site builder if I'm a
    small business and only need three pages?"*

### 5. `schema` — severity: critical

Does the page carry valid JSON-LD?

`page-signals.json` lists `schema.types`. Four types matter here:
`Organization`, `FAQPage`, `Article`, `Product`. Schema will not rescue weak
content, but on good content it is the difference between the model finding the
information and the model extracting it cleanly.

- **Pass:** valid JSON-LD of a type appropriate to the page.
- **Fail:** none present, or blocks that fail to parse (the signals file
  reports `malformed`).
- **Fix:** `aeo.py schema spec.json`. Validate at validator.schema.org.

### 6. `tables` — severity: minor

Where the page compares things, is the comparison a table?

Structured comparisons get pulled into answers far more often than the same
information buried in prose.

- **Pass:** a comparison table exists where the content warrants one.
- **Fail:** comparisons written as paragraphs.
- **Fix:** convert. Options as rows, criteria as columns.
- **N/A:** pages with nothing to compare. Do not penalise these — say so.

### 7. `unique_data` — severity: major

Does the page contain something that exists nowhere else?

If the content restates what a thousand other pages say, a model has no reason
to cite this one. Original data forces the citation: when you are the only
source for a fact, quoting the fact means quoting you.

You can only detect *linguistic signals* of this from HTML — "our survey of…",
"we analysed N…", "we found that…". Say so rather than overclaiming.

- **Pass:** signals of first-party research, proprietary data, or original
  measurement.
- **Fail:** entirely derivative.
- **Fix:** it does not take a large study. Survey 100 customers, interview 20,
  analyse your own product telemetry, publish patterns from real cases. Small
  and original beats large and borrowed.

## Structural signal

`page-signals.json` also reports `avg_words_between_headings`. Pages that break
content into sections of roughly 120-180 words between headings get cited
noticeably more than pages with sparse or chaotic structure. A value above ~400
means the page is a wall of text; flag it alongside the seven criteria.

## Output format

```json
{
  "url": "...",
  "overall_score": 0-100,
  "checks": [
    {"key": "first_sentence", "pass": false, "severity": "critical",
     "detail": "What you actually saw on this page."}
  ],
  "suggestions": [
    {"title": "Short imperative title",
     "body": "What to do and why it follows from the check that failed.",
     "example": "Paste-ready replacement text or markup, or null."}
  ]
}
```

All seven keys, every time. Weight `overall_score` by severity — a failed
`critical` should cost far more than a failed `minor`. Order suggestions by
impact per unit of effort, and fill `example` with real text whenever the fix is
something the user could paste. A suggestion without an example is usually a
suggestion you have not thought through.
