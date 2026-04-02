---
title: Standardize Shared Bootstrap Conventions
impact: HIGH
impactDescription: Reduces drift across services and keeps runtime behavior predictable
tags: architecture, bootstrap, monorepo, platform
---

## Standardize Shared Bootstrap Conventions

In multi-service Nest workspaces, keep core bootstrap behavior consistent across applications. Global pipes, versioning, security middleware, shutdown hooks, and logging conventions should come from a shared bootstrap path unless a service has a documented reason to diverge.

**When to apply:**

- Running multiple HTTP services or worker processes in the same codebase
- Adding or changing global Nest runtime behavior

**What to avoid:**

- Re-implementing bootstrap logic differently in each service
- Letting workers and schedulers drift away from the platform conventions without intent

**Incorrect (each service owns slightly different bootstrap logic):**

```typescript
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(new ValidationPipe());
  await app.listen(3000);
}
```

**Correct (shared bootstrap helper):**

```typescript
async function bootstrap() {
  const app = await setupApplication(AppModule, "holiday-content");
  await app.listen(3000);
}
```

**Review checklist:**

- Is global runtime behavior defined in one shared bootstrap path?
- If a service diverges, is the divergence explicit and documented?

**Scope boundaries:**

- Applies most strongly in service monorepos
- Single-service applications can keep bootstrap local, but shared helpers still become valuable once multiple entry points exist

Reference: [NestJS Standalone Applications](https://docs.nestjs.com/standalone-applications)
