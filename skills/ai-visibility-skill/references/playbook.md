# The five levers

Consult this when the user asks *what to do* rather than *what is broken*.

These are not sequential steps. They are levers you pull based on what the
audit showed is actually holding the brand back. Most businesses need two of
them; almost none need all five at once.

---

## Lever 1 — Clarity

**Make the brand machine-readable.**

A model has to be able to establish three things:

- what the business does
- who it is for
- what makes it different

Not from a clever tagline — from plain, structured, extractable language,
everywhere the brand controls the message. If an assistant cannot work out what
the business does from the homepage, nothing downstream matters.

In practice:

- Homepage, product pages, and the about page answer those three questions
  directly. Not in brand poetry or clever headlines. Plainly.
- Clear heading hierarchy. Sections of roughly **120-180 words between
  headings** get cited measurably more than loose or chaotic structure.
- Comparison tables wherever there is something to compare. Structured data
  gets pulled into answers; the same facts buried in paragraphs do not.
- **The help centre, FAQ, and product documentation are the most underrated
  assets here.** Most businesses treat them as a support cost. They map almost
  perfectly onto the long, specific questions people ask assistants — *"does it
  integrate with X?"*, *"can I use it for Y?"*, *"is it suitable for Z?"* This
  is where small businesses beat large ones cheaply.

---

## Lever 2 — Positioning

**One story, everywhere.**

Traditional SEO tolerated weak positioning: strong content and links could
carry a page to number one regardless. AI does not work that way. The model
builds its picture of a brand by reconciling everything it has read. If the
sources disagree, the picture blurs — and a blurry brand loses to a sharp one.

The failure looks like this: the site says "for small business owners", the
LinkedIn bio says "built for solo founders", the reviews talk about people
leaving their nine-to-five. Three positions, no confidence, no recommendation.

The work is not more content. It is one sentence — *what, for whom, why
different* — propagated everywhere: site, social bios, directory listings,
review-site profiles, press boilerplate, partner pages, documentation.

Cheap, unglamorous, and frequently the highest-return action in the whole
audit.

---

## Lever 3 — Win on other people's ground

**Roughly 85% of brand mentions in AI answers come from third-party sources.**

This is the number that reframes the whole exercise. The brand's own site is a
minority input. What moves the needle is being present where the model reads
about the category:

- Roundups and listicles — *"best X for Y"* articles already being cited. The
  report's **Most-cited pages** section names them; those are your targets.
- Review platforms relevant to the category.
- Communities where buyers discuss the problem — including Reddit and
  category-specific forums, which are heavily represented in AI answers.
- Podcasts, interviews, and guest pieces where the positioning sentence gets
  repeated by someone else.
- Comparison pages, including competitors' — being the named alternative on
  someone else's comparison page is a real position.

This is slower than editing a page and it is usually what actually fixes a
coverage problem.

---

## Lever 4 — Content structure

**Be specific to the point of discomfort, and own data nobody else has.**

Assistants do not look for the best answer in general. They look for the best
answer *to this situation*. A page matching the situation beats a better page
about the category.

So build for variations that real buyers actually describe:

- *"[Category] for [industry]"*
- *"[Category] for companies in [country] with [size]"*
- *"[Category] for [specific constraint]"*

One page, one persona, one question.

Then the harder half: **publish something that exists nowhere else.** Most
content restates the same handful of claims, so a model has no reason to prefer
any particular source. Original data removes the choice — if you are the only
source for a fact, citing the fact means citing you.

It does not require a large study. Survey 100 customers. Interview 20.
Analyse your own product telemetry. Publish patterns from real cases.
*"Our survey of 400 Bulgarian online stores found…"* is something a competitor
cannot copy.

And rewrite the FAQ in real language. Not what marketing imagines people ask —
what they actually asked, pulled verbatim from tickets, sales calls, and site
search.

---

## Lever 5 — Measurement

**Re-measure monthly, and watch the trend rather than the number.**

A single run is a photograph. What you need is the direction of travel, per
model, on a fixed prompt set:

- Same prompts, same models, once a month. Changing the set resets the
  baseline.
- Watch high-intent visibility separately from the overall figure. Overall
  visibility can rise while every prompt that matters gets worse.
- Watch the descriptions, not only the mentions — a description drifting away
  from the intended positioning is an early warning.
- Watch new competitors entering the answers. A name that was not there last
  month is doing something worth understanding.
- Add GA4 AI-channel tracking (see `technical-fixes.md`) so visibility can be
  connected to actual traffic.

Thirty minutes a month.

---

## Where to start

Start where the diagnosis pointed, not at Lever 1.

- Losses diagnosed as **coverage** → Lever 3.
- Losses diagnosed as **consistency** → Lever 2.
- Losses diagnosed as **specificity** → Lever 4.
- Blocked crawlers, missing schema, no sitemap → fix those first regardless;
  see `technical-fixes.md`. Nothing else works while the door is shut.

And do not let the user skip Lever 5. Without re-measurement they cannot tell
whether any of this worked, which is how AEO work quietly gets abandoned.
