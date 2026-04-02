---
title: Hoist Static I/O to Module Level
impact: HIGH
impactDescription: avoids repeated file/network I/O per request
tags: server, io, performance, remix, loaders, og-image
---

## Hoist Static I/O to Module Level

When loading static assets (fonts, logos, images, config files) in loaders or
resource routes, hoist the I/O operation to module level. Module-level code runs
once when the module is first imported, not on every request.

**Incorrect: reads font file on every request**

```typescript
// app/routes/og.tsx
import { readFileSync } from "fs";
import { join } from "path";

export async function loader({ request }: LoaderFunctionArgs) {
  // Runs on EVERY request - expensive!
  const fontData = readFileSync(join(process.cwd(), "public/fonts/Inter.ttf"));
  const logoData = readFileSync(join(process.cwd(), "public/images/logo.png"));

  const png = await generateOgImage({ fontData, logoData });
  return new Response(png, { headers: { "Content-Type": "image/png" } });
}
```

**Correct: loads once at module initialization**

```typescript
// app/routes/og.tsx
import { readFileSync } from "fs";
import { join } from "path";
import type { LoaderFunctionArgs } from "@remix-run/node";

// Module-level: runs ONCE when module is first imported
const fontData = readFileSync(join(process.cwd(), "public/fonts/Inter.ttf"));
const logoData = readFileSync(join(process.cwd(), "public/images/logo.png"));

export async function loader({ request }: LoaderFunctionArgs) {
  const png = await generateOgImage({ fontData, logoData });
  return new Response(png, { headers: { "Content-Type": "image/png" } });
}
```

**Alternative: async fetch hoisted to module level**

```typescript
// app/routes/og.tsx
import type { LoaderFunctionArgs } from "@remix-run/node";

// Promises start immediately at import time
const fontData = fetch(new URL("../fonts/Inter.ttf", import.meta.url)).then(
  (res) => res.arrayBuffer(),
);
const logoData = fetch(new URL("../images/logo.png", import.meta.url)).then(
  (res) => res.arrayBuffer(),
);

export async function loader({ request }: LoaderFunctionArgs) {
  const [font, logo] = await Promise.all([fontData, logoData]);

  const png = await generateOgImage({ fontData: font, logoData: logo });
  return new Response(png, { headers: { "Content-Type": "image/png" } });
}
```

**General example: loading config or templates**

```typescript
// Incorrect: reads config on every loader call
export async function loader({ request }: LoaderFunctionArgs) {
  const config = JSON.parse(await fs.readFile("./config.json", "utf-8"));
  const template = await fs.readFile("./template.html", "utf-8");
  return json(render(template, request, config));
}

// Correct: loads once at module level
const configPromise = fs.readFile("./config.json", "utf-8").then(JSON.parse);
const templatePromise = fs.readFile("./template.html", "utf-8");

export async function loader({ request }: LoaderFunctionArgs) {
  const [config, template] = await Promise.all([
    configPromise,
    templatePromise,
  ]);
  return json(render(template, request, config));
}
```

**When to use this pattern:**

- Loading fonts for OG image generation
- Loading static logos, icons, or watermarks
- Reading configuration files that don't change at runtime
- Loading email templates or other static templates
- Any static asset that's the same across all requests

**When NOT to use this pattern:**

- Assets that vary per request or user
- Files that may change during runtime (use caching with TTL instead)
- Large files that would consume too much memory if kept loaded
- Sensitive data that shouldn't persist in memory
