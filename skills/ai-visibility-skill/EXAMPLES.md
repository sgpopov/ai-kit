# What to ask Claude

Copy one of these, replace the bracketed parts, send. The skill triggers on its
own — you don't need to name it.

Not to be confused with `prompts.json`, which holds the questions that get sent
*to* the AI assistants as the measurement. These are the things you say *to
Claude* to get work done.

Each one is given in English and Bulgarian. Use whichever fits — and write the
bracketed details in your buyers' language, not in English out of politeness.
The audit measures the market you actually sell to.

---

## 1. Start here — the full audit

Use when you have no idea where you stand. Takes 30-60 minutes of your time,
mostly pasting answers.

```
I run [what you do] at [yourdomain.com]. My buyers are [who they are and what
they're trying to do]. I have no idea whether ChatGPT, Claude, Gemini or
Perplexity ever recommend us, and I want to find out and fix it.

Walk me through the whole audit: help me write the questions my actual buyers
would type, tell me exactly which answers to paste where, then show me where
I'm losing and what to do about it.

Competitors I know of: [a.com, b.com]. Tell me if the answers name others I
should be watching.
```

```
Имам [какво правиш] на [моятсайт.bg]. Клиентите ми са [кои са и какво търсят].
Нямам представа дали ChatGPT, Claude, Gemini или Perplexity изобщо ни
препоръчват, и искам да разбера и да го оправя.

Преведи ме през целия одит: помогни ми да напиша въпросите, които реалните ми
клиенти биха написали, кажи ми точно кои отговори къде да поставя, после ми
покажи къде губя и какво да направя.

Конкуренти, за които знам: [a.bg, b.bg]. Кажи ми, ако в отговорите излязат
други, които трябва да следя.
```

**You get:** a `report.html` dashboard, visibility % per model and per purchase
intent, share of voice, the list of high-intent questions you lost and who won
them, and a ranked fix list.

---

## 2. Five minutes, zero setup — can AI even read my site?

Use first if you want one quick answer before committing to anything. Nothing to
fill in, no pasting.

```
Check whether AI crawlers can actually read [yourdomain.com]. I want to know
whether GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot and Google-Extended are
blocked, whether I have llms.txt and a working sitemap, and what schema my
homepage exposes.

Then tell me which of those actually affects whether I get recommended, and give
me the exact robots.txt lines and JSON-LD to paste. Explain the trade-off on
training crawlers rather than deciding for me.
```

```
Провери дали AI ботовете реално могат да четат [моятсайт.bg]. Искам да знам
блокирани ли са GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot и
Google-Extended, имам ли llms.txt и работещ sitemap, и каква schema излага
началната ми страница.

После ми кажи кое от това наистина влияе дали ще бъда препоръчан, и ми дай
точните редове за robots.txt и JSON-LD за поставяне. Обясни ми компромиса при
тренировъчните ботове, вместо да решаваш вместо мен.
```

**You get:** an AEO readiness score out of 100, which of 19 AI crawlers are
blocked and why, and paste-ready fixes. This is the one to run first — a blocked
crawler makes every other effort pointless.

---

## 3. Find out what your buyers actually ask

Use before measuring anything, if you're not sure what to test.

```
I sell [product/service] to [audience] in [market]. Before I measure anything,
help me work out which questions they actually type into ChatGPT right before
they decide — the unbranded, situation-specific ones, not the keyword versions.

Ask me whatever you need about my customers first. Aim for 20 questions in
[language], tagged by purchase intent, with at least a third of them high
intent. Save them so I can reuse the same set every month.
```

```
Продавам [продукт/услуга] на [аудитория] в [пазар]. Преди да меря каквото и да
е, помогни ми да разбера какви въпроси реално пишат в ChatGPT точно преди да
решат — небрандираните, конкретните за ситуацията, не варианта с ключови думи.

Питай ме каквото ти трябва за клиентите ми. Целта са 20 въпроса на български,
маркирани по намерение за покупка, поне една трета с високо намерение. Запази
ги, за да ползвам същия набор всеки месец.
```

**You get:** a `prompts.json` you can reuse — which is what makes month-over-
month comparison meaningful. Brand-name questions produce flattering numbers
that predict nothing; this step is how you avoid that.

---

## 4. A competitor keeps winning — why?

Use when you have one specific loss that bothers you. Works with a single pasted
answer; no full audit needed.

```
When I ask ChatGPT "[the exact question]", it recommends [competitor.com] and
never mentions [mydomain.com]. Here is the full answer it gave me, including the
links:

[paste the whole answer]

Work out why. Is this a coverage, consistency or specificity problem? Use the
evidence in the answer itself, not general advice. Then give me three concrete
things to do, cheapest first — a page with a working title, a specific site to
get listed on, an exact sentence to standardise.
```

```
Когато питам ChatGPT „[точният въпрос]", той препоръчва [конкурент.bg] и никога
не споменава [моятсайт.bg]. Ето целия отговор, който получих, заедно с линковете:

[постави целия отговор]

Разбери защо. Проблем с покритие, с последователност или с конкретика? Използвай
доказателствата в самия отговор, не общи съвети. После ми дай три конкретни
неща, най-евтиното първо — страница с работно заглавие, конкретен сайт, в който
да вляза, точно изречение, което да уеднаквя.
```

**You get:** a root-cause diagnosis with three specific actions. The three
causes need genuinely different work — off-site presence, message alignment, or
one narrow page — so naming the right one saves months.

---

## 5. Audit one page and rewrite it

Use on the page that should be winning a query but never gets cited.

```
[url] is supposed to be the page that wins "[the query]", but AI never cites it.

Audit it: can an assistant lift a quotable answer out of it without reading the
whole thing? Score it, then give me the actual text — the rewritten first
paragraph, the key-takeaways block, the FAQ questions in the language real
people use, the comparison table, and the JSON-LD. Paste-ready, not advice to
"improve clarity".

Tell me honestly which criteria don't apply to this page instead of inventing
work.
```

```
[url] трябва да е страницата, която печели „[заявката]", но AI никога не я
цитира.

Одитирай я: може ли асистент да извади цитируем отговор от нея, без да я чете
цялата? Оцени я, после ми дай самия текст — пренаписан първи параграф, блок с
ключови изводи, FAQ въпроси на езика, на който хората реално питат, сравнителна
таблица и JSON-LD. Готово за поставяне, не съвети да „подобря яснотата".

Кажи ми честно кои критерии не важат за тази страница, вместо да измисляш работа.
```

**You get:** a score against seven criteria plus the replacement text. The one
that surprises most people: if your first sentence isn't the answer, assistants
often never reach it.

---

## 6. AI describes my brand wrong

Use when you *are* mentioned but the description is off. Often more valuable
than a missing mention.

```
AI describes us wrong. When Gemini mentions [mydomain.com] it calls us
"[the wrong description you saw]", but we're actually [what you really are, for
whom, and what makes you different].

Here are the answers where it happened: [paste one or more]

Where is that impression coming from, and what do I change to correct it? Check
whether my own pages and profiles are telling one story or several. I'd rather
have a short honest list than a content plan.
```

```
AI ни описва грешно. Когато Gemini спомене [моятсайт.bg], ни нарича
„[грешното описание, което видя]", а всъщност сме [какви сте наистина, за кого,
и с какво сте различни].

Ето отговорите, в които се случи: [постави един или няколко]

Откъде идва това впечатление и какво да променя, за да го поправя? Провери дали
собствените ми страници и профили разказват една история или няколко. Предпочитам
кратък честен списък, отколкото план за съдържание.
```

**You get:** a consistency diagnosis. When your own sources contradict each
other, models hedge or skip you in favour of a brand they can describe cleanly —
and fixing that is usually free.

---

## 7. Monthly re-check

Use every month. Thirty minutes, and it's the step that makes the rest worth
doing.

```
Re-run my AI visibility audit in [path to workspace]. Same questions, same
models, new run for [month].

Then tell me what changed: did I gain or lose ground, are there new competitors
in the answers, and have my descriptions drifted from my positioning? Sort by
purchase intent — I care about the questions near a decision, not the overall
average. If the two runs aren't comparable, say so instead of showing me a
trend.
```

```
Пусни отново одита за AI видимост в [път до работната папка]. Същите въпроси,
същите модели, нов run за [месец].

После ми кажи какво се е променило: спечелих ли или загубих позиции, има ли нови
конкуренти в отговорите, и отклонили ли са се описанията ми от позиционирането
ми? Подреди по намерение за покупка — интересуват ме заявките близо до решение,
не общата средна стойност. Ако двата run-а не са сравними, кажи го, вместо да ми
показваш тренд.
```

**You get:** the delta per model and per intent. Overall visibility can rise
while every question that matters gets worse — which is why the intent split
matters more than the headline number.

---

## Which to start with

- **Never checked anything** → 2, then 1.
- **Don't know what to measure** → 3.
- **One specific loss that bothers you** → 4.
- **Already know the page that should be winning** → 5.
- **Mentioned, but described badly** → 6.
- **Audited once already** → 7, monthly.

You don't need an API key or an account for any of them. Prompts 1, 3, 4, 6 and
7 work entirely from answers you paste in yourself. Prompt 2 needs internet
access; 5 needs it unless you paste the page HTML.
