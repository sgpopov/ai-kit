# Building the prompt set

The prompt set is the measurement instrument. A bad one produces a number that
looks precise and means nothing.

## The shift that makes this hard

A Google query averages 3.4 words: *"best hosting Bulgaria"*. Everyone typing
it gets the same ten links, so three brands win and the rest lose.

An AI prompt averages ~23 words:

> *"Which hosting provider in Bulgaria is best for a new WordPress site where I
> can count on reliable support even on Sundays, without the site going down?"*

The user described their situation, and the model answers *that situation*. The
inventory of winnable positions is therefore effectively unlimited — which is
why a small business can beat a much larger competitor here. But you only
capture that inventory if your prompt set contains real situations rather than
category keywords.

## What to ask

Interview the user. You need their buyers' actual questions, not yours.

Ask them directly:

- What does a customer ask you in the first sales call?
- What do people search for right before they buy — and what do they type into
  a chat window instead of a search box?
- Which competitors do prospects mention as alternatives?
- What use case are you unmistakably the right answer for?

Then check their evidence rather than guessing: support tickets, sales call
notes, Search Console queries, on-site search logs, and questions in the
communities where their buyers hang out. The exact phrasing matters — models
were trained on how people really write, so a marketing-brochure question will
not match a real one.

## Four shapes to cover

| Category | Shape | Notes |
|---|---|---|
| `comparison` | "X vs Y", "alternatives to X", "best X for [specific situation]" | Highest value. The buyer is choosing. |
| `brand` | "reviews of X", "is X any good", "X pricing" | Easy to win, low volume, but a bad answer here is a direct loss. |
| `topic` | "how do I solve [problem]", "what tools do [role] use for [task]" | The bulk of a good set. |
| `educational` | "what is X", "how does X work" | Visibility only. Rarely converts. Keep a few for coverage. |

## Purchase intent

Tag every prompt. This is what turns a report into a priority list.

**`high`** — the buyer is close to a decision. Comparisons, alternatives-to,
"best X for [narrow use case]", direct brand queries. Losing one of these is
lost revenue, not lost awareness. **Fix these first.**

**`medium`** — actively researching. "How do I…", "what do [role] use for…".
Worth winning, further from the transaction.

**`low`** — broad educational and trend questions. Real visibility, slow return.

A workable set for a first run is 15-25 prompts, with at least a third of them
`high`. Fewer than 10 and per-model percentages swing wildly on one answer.

## Rules of thumb

- **Write them in the buyers' language.** If customers ask in Bulgarian, the
  prompts are in Bulgarian. Translating to English measures a market that does
  not exist.
- **Be specific to the point of discomfort.** "Best HR software" is a coin
  flip. "HR software for a 30-50 person company in Bulgaria" is a question you
  can actually own — and it is what people type.
- **Include competitor-named prompts.** "Alternatives to [competitor]" is where
  their customers go looking, and it is often the cheapest win available.
- **Do not stuff the set with brand queries.** A model that knows the brand
  name will recite it, producing a flattering number that predicts nothing.
- **Keep the set stable between runs.** Changing prompts changes the baseline;
  the trend becomes meaningless. Add new prompts as a separate group and note
  when they entered.

## Format

`prompts.json`:

```json
[
  {
    "id": "p01",
    "text": "Which hosting provider is best for a WordPress site with weekend support?",
    "category": "comparison",
    "intent": "high"
  }
]
```

`id` must be stable across runs — it is how answers are matched over time. If
`intent` is omitted it is derived from `category` (`brand`/`comparison` → high,
`educational` → low, otherwise medium), but setting it deliberately is better.
