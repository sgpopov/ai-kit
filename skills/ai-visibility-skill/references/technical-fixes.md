# Technical fixes

Run `aeo.py tech <domain>` first. Everything here responds to something in its
output.

## 1. Crawler access

Two different jobs, and blocking them has different consequences:

- **Live browsing / search bots** (`ChatGPT-User`, `OAI-SearchBot`,
  `Claude-User`, `Claude-SearchBot`, `PerplexityBot`, `Perplexity-User`,
  `Bingbot`) fetch pages *during* a conversation. Blocking these makes you
  invisible **today**.
- **Training crawlers** (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`,
  `Applebot-Extended`, `meta-externalagent`, `Bytespider`) build the model's
  background knowledge. Blocking these costs you the **next** model — and
  whether that is a bad trade is a legitimate business decision, not a
  self-evident mistake.

Present it that way. Some publishers block training crawlers deliberately;
telling them they have made an error is wrong. What is almost never
intentional is blocking the live/search bots, because that removes the brand
from answers with no compensating benefit.

`aeo.py tech` only flags a blanket `Disallow: /` as blocked. Path-level rules
are reported as `partial` — usually deliberate (admin, checkout, staging) and
not an AI-visibility problem.

**Allow everything (default for most businesses):**

```
User-agent: *
Allow: /
Sitemap: https://example.com/sitemap.xml
```

**Allow answering, refuse training:**

```
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: CCBot
Disallow: /

# Live retrieval stays allowed so the brand can still be recommended
User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /
```

Note that `robots.txt` is a request, not enforcement, and that some crawlers
ignore it. If the user needs enforcement, that is a WAF or server-rules
conversation, not a robots.txt one.

## 2. Schema markup

Structured data does not rescue weak content, but on decent content it is the
difference between a model finding your information and extracting it cleanly.

Four types carry most of the weight:

| Type | Where | What it settles |
|---|---|---|
| `Organization` | Homepage | Who you are, what you know about, where else you exist |
| `FAQPage` | Any page with an FAQ | Turns prose Q&A into extractable pairs |
| `Article` | Editorial content | Author, dates, headline — feeds attribution |
| `Product` | Product pages | Price, currency, availability |

Generate with `aeo.py schema spec.json`, where the spec is one object or a list:

```json
[
  {"type": "Organization",
   "name": "Example", "url": "https://example.com",
   "description": "One clear sentence about what you do and for whom.",
   "knowsAbout": ["topic one", "topic two"],
   "sameAs": ["https://linkedin.com/company/example"]},
  {"type": "FAQPage",
   "items": [{"question": "…", "answer": "…"}]}
]
```

Paste the output into `<head>`, then validate at
[validator.schema.org](https://validator.schema.org).

Two things people get wrong: `knowsAbout` on `Organization` is the most
underused field — it is a direct statement of what topics you should be
associated with. And `FAQPage` markup must match visible page content; marking
up questions that are not on the page is a violation, not a shortcut.

## 3. llms.txt

An emerging convention (`example.com/llms.txt`) — a markdown index pointing
assistants at the pages that best explain you. Adoption is not universal, so
treat it as cheap insurance rather than a fix with measurable return. It costs
fifteen minutes and cannot hurt.

```bash
python scripts/aeo.py -w <workspace> llmstxt --limit 40
```

Generates from the sitemap. Then do the part that matters: **replace the
auto-generated labels with real one-line descriptions.** A list of bare URLs
adds nothing over the sitemap that already exists.

```markdown
# Example

> Hosting for WordPress agencies in Bulgaria, with 24/7 support including weekends.

## Docs

- [/pricing](https://example.com/pricing): Plans, prices in EUR, what each tier includes.
- [/support](https://example.com/support): Response times, channels, weekend coverage.
- [/wordpress](https://example.com/wordpress): Managed WordPress specifics and migration.
```

Include the pages that answer buying questions. Leave out the blog archive.

## 4. Bing Webmaster Tools

ChatGPT's web search runs on Bing's index, and Copilot is Bing with a model on
top. A site indexed well in Google but poorly in Bing is invisible to a large
share of AI traffic — and most people have never opened Bing Webmaster Tools
because they have spent their careers on Google.

1. Register at [bing.com/webmasters](https://www.bing.com/webmasters).
2. Import from Google Search Console (one click) or verify manually.
3. Submit the sitemap.
4. Check the crawl-error report for pages Bing cannot reach.
5. Use URL Submission for important new or updated pages instead of waiting.

Verify a week later: search `site:example.com` on Bing. If pages are missing
there, they are missing from ChatGPT.

## 5. Measuring AI traffic in GA4

GA4 already collects visits from assistants — it just files them under
"Referral" with everything else. Fifteen minutes to separate them:

1. **Admin → Data Display → Channel Groups.**
2. **Create New Channel Group** → **Add New Channel** → name it "AI Traffic".
3. **Add Condition Group** → **Source** → **matches regex**:

```
^(?:chatgpt\.com|chat\.openai\.com|openai\.com|claude\.ai|perplexity\.ai|www\.perplexity\.ai|copilot\.microsoft\.com|copilot\.cloud\.microsoft|gemini\.google\.com|aistudio\.google\.com|(?:\w+\.)?mistral\.ai|chat\.deepseek\.com|you\.com|phind\.com|pi\.ai|grok\.com|x\.ai|meta\.ai|openrouter\.ai|poe\.com|kagi\.com)$
```

4. **Reorder** the group so "AI Traffic" sits **above** "Referral". GA4
   evaluates top-down; skip this and everything still lands in Referral. This
   step is not optional.
5. **Reports → Acquisition → Traffic acquisition**, then switch the dimension
   to *Session Custom Channel Group*. If it is missing: Customize report →
   Dimensions → add it → Apply → Save.

Caveat worth stating to the user: many assistants strip or omit the referrer,
so this undercounts — often substantially. It shows the trend and the relative
mix, not the true total.
