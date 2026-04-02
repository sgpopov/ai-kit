---
title: Keep Worker and Scheduler Bootstrap Consistent
impact: MEDIUM
impactDescription: Improves operability and reduces drift between HTTP and background runtimes
tags: devops, workers, scheduler, bootstrap
---

## Keep Worker and Scheduler Bootstrap Consistent

Treat schedulers, background workers, and standalone Nest application contexts as first-class runtime entry points. They should follow the same expectations for logging, configuration validation, shutdown behavior, and instrumentation as HTTP services.

**When to apply:**

- Creating `createApplicationContext()` entry points
- Running cron jobs, queue workers, or one-off background processes in Nest

**What to avoid:**

- Using ad hoc startup scripts with different logging, config, or shutdown behavior from the rest of the platform
- Treating workers as exempt from validation or observability conventions

**Incorrect (worker bootstrap is special-cased and informal):**

```typescript
async function bootstrap() {
  console.log("Scheduler starting");
  await NestFactory.createApplicationContext(SchedulerModule);
}
```

**Correct (worker bootstrap follows platform conventions):**

```typescript
async function bootstrap() {
  const app = await NestFactory.createApplicationContext(SchedulerModule, {
    bufferLogs: true,
  });

  app.enableShutdownHooks();

  const logger = app.get(Logger);
  logger.log("Scheduler started");
}
```

**Review checklist:**

- Do worker entry points validate config, initialize logging, and enable orderly shutdown?
- Are worker runtime conventions aligned with the rest of the Nest platform?

**Scope boundaries:**

- Applies to long-running workers and schedulers more than short-lived local scripts
- Simple build scripts may stay outside Nest, but operational workloads should not

Reference: [NestJS Standalone Applications](https://docs.nestjs.com/standalone-applications)
