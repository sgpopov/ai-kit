---
title: Use defer or async on Script Tags
impact: HIGH
impactDescription: eliminates render-blocking
tags: rendering, script, defer, async, performance
---

## Use defer or async on Script Tags

Script tags without `defer` or `async` block HTML parsing while the script
downloads and executes. This delays First Contentful Paint and Time to
Interactive.

- **`defer`**: Downloads in parallel, executes after HTML parsing completes,
  maintains execution order
- **`async`**: Downloads in parallel, executes immediately when ready, no
  guaranteed order

Use `defer` for scripts that depend on DOM or other scripts. Use `async` for
independent scripts like analytics.

**Incorrect (blocks rendering):**

```tsx
// app/root.tsx
export default function App() {
  return (
    <html>
      <head>
        <script src="https://example.com/analytics.js" />
        <script src="/scripts/utils.js" />
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
```

**Correct (non-blocking):**

```tsx
// app/root.tsx
export default function App() {
  return (
    <html>
      <head>
        {/* Independent script - use async */}
        <script src="https://example.com/analytics.js" async />
        {/* DOM-dependent script - use defer */}
        <script src="/scripts/utils.js" defer />
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
```

**For scripts that must run only after hydration**, inject them via `useEffect`
to guarantee client-only execution:

```tsx
// app/root.tsx
import { useEffect } from "react";

export default function App() {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://example.com/analytics.js";
    script.async = true;
    document.head.appendChild(script);
  }, []);

  return (
    <html>
      <head>
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
```

**Note:** Remix has no equivalent to Next.js's `next/script` with a `strategy`
prop. The raw `async`/`defer` HTML attributes are the correct Remix-idiomatic
approach for external scripts. For post-hydration loading, use the `useEffect`
pattern above.

**Reference:**
[MDN - Script element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#defer)
