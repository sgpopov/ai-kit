---
title: Prevent Waterfall Chains in Loaders and Actions
impact: CRITICAL
impactDescription: 2-10× improvement
tags: loaders, actions, waterfalls, parallelization
---

## Prevent Waterfall Chains in Loaders and Actions

In Remix `loader` and `action` functions, start independent operations
immediately rather than awaiting them sequentially.

**Incorrect (config waits for auth, data waits for both):**

```typescript
import { json } from "@remix-run/node";
import type { LoaderFunctionArgs } from "@remix-run/node";

export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request);
  const config = await fetchConfig();
  const data = await fetchData(session.user.id);

  return json({ data, config });
}
```

**Correct (auth and config start immediately):**

```typescript
import { json } from "@remix-run/node";
import type { LoaderFunctionArgs } from "@remix-run/node";

export async function loader({ request }: LoaderFunctionArgs) {
  const sessionPromise = getSession(request);
  const configPromise = fetchConfig();
  const session = await sessionPromise;
  const [config, data] = await Promise.all([
    configPromise,
    fetchData(session.user.id),
  ]);

  return json({ data, config });
}
```

For operations with more complex dependency chains, use `better-all` to
automatically maximize parallelism (see Dependency-Based Parallelization).
