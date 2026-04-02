---
title: Dynamic Imports for Heavy Components
impact: CRITICAL
impactDescription: directly affects TTI and LCP
tags: bundle, dynamic-import, code-splitting, lazy-loading
---

## Dynamic Imports for Heavy Components

Use React's `lazy` + `Suspense` to lazy-load large components not needed on initial render. Remix v2 has no framework-specific dynamic import wrapper — use the React primitives directly.

**Incorrect (Monaco bundles with main chunk ~300KB):**
```tsx
import { MonacoEditor } from './monaco-editor'

function CodePanel({ code }: { code: string }) {
  return <MonacoEditor value={code} />
}
```

**Correct (Monaco loads on demand):**
```tsx
import { lazy, Suspense } from 'react'

const MonacoEditor = lazy(() =>
  import('./monaco-editor').then(m => ({ default: m.MonacoEditor }))
)

function CodePanel({ code }: { code: string }) {
  return (
    <Suspense fallback={<div>Loading editor…</div>}>
      <MonacoEditor value={code} />
    </Suspense>
  )
}
```

**SSR note:** If the component must not run on the server (e.g. it accesses `window`), guard the import inside a `clientLoader` or render it only inside a route that uses `export const handle = { ssr: false }`, or gate it with a `useEffect`/`useState` mount check:
```tsx
import { lazy, Suspense, useEffect, useState } from 'react'

const MonacoEditor = lazy(() =>
  import('./monaco-editor').then(m => ({ default: m.MonacoEditor }))
)

function CodePanel({ code }: { code: string }) {
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  if (!mounted) return null

  return (
    <Suspense fallback={<div>Loading editor…</div>}>
      <MonacoEditor value={code} />
    </Suspense>
  )
}
```