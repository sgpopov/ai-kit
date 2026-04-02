---
title: Propagate Correlation IDs Through Logs and Async Work
impact: MEDIUM
impactDescription: Improves incident debugging and cross-service traceability
tags: devops, logging, observability, tracing
---

## Propagate Correlation IDs Through Logs and Async Work

Attach a request or job correlation ID to logs and preserve it across async boundaries. In multi-service systems, structured logs without correlation context are expensive to use during incident response.

**When to apply:**

- HTTP services handling user requests
- Background jobs, schedulers, and async workflows that trigger downstream work

**What to avoid:**

- Emitting logs with no trace or request context
- Generating new unrelated identifiers at every layer when a parent correlation ID already exists

**Incorrect (logs cannot be tied together):**

```typescript
this.logger.log("Started booking consolidation");
this.logger.error("Failed to update booking");
```

**Correct (logs carry shared context):**

```typescript
this.logger.log("Started booking consolidation", {
  correlationId,
  bookingReference,
});

this.logger.error("Failed to update booking", {
  correlationId,
  bookingReference,
  errorCode,
});
```

**Review checklist:**

- Can related logs across layers be tied together by a stable correlation identifier?
- Is the identifier propagated into async jobs or downstream calls where practical?

**Scope boundaries:**

- Applies to operational logs, not necessarily every debug statement during local development
- Full distributed tracing can supersede this, but correlation IDs are still useful when tracing is partial

Reference: [NestJS Logger](https://docs.nestjs.com/techniques/logger)
