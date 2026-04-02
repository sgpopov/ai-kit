---
title: Use Explicit Registration APIs for Configurable Modules
impact: CRITICAL
impactDescription: Prevents hidden configuration side effects and improves testability
tags: architecture, dynamic-modules, configuration, dependency-injection
---

## Use Explicit Registration APIs for Configurable Modules

When a reusable Nest module needs configuration, expose an explicit `forRoot`, `forRootAsync`, or similar registration API. This makes configuration ownership visible and prevents module imports from silently reading environment state.

**When to apply:**

- Creating reusable modules that need API keys, endpoints, feature flags, or client settings
- Sharing the same integration package across multiple services

**What to avoid:**

- Reading `process.env` or calling `ConfigModule.forRoot()` directly inside a shared package module
- Hiding configuration in module-level side effects

**Incorrect (hidden configuration):**

```typescript
@Module({
  imports: [ConfigModule.forRoot()],
  providers: [SearchService],
  exports: [SearchService],
})
export class SearchModule {}
```

**Correct (explicit registration API):**

```typescript
@Module({})
export class SearchModule {
  static forRootAsync(): DynamicModule {
    return {
      module: SearchModule,
      imports: [ConfigModule],
      providers: [
        {
          provide: SEARCH_OPTIONS,
          inject: [ConfigService],
          useFactory: (config: ConfigService) => ({
            node: config.getOrThrow<string>("search.node"),
            requestTimeout: config.getOrThrow<number>("search.requestTimeout"),
          }),
        },
        SearchService,
      ],
      exports: [SearchService],
    };
  }
}
```

**Review checklist:**

- Is module configuration explicit at import time?
- Can tests provide configuration without relying on ambient environment state?

**Scope boundaries:**

- Applies primarily to reusable or configurable internal packages
- Simple local feature modules without external configuration may not need a dynamic module API

Reference: [NestJS Dynamic Modules](https://docs.nestjs.com/fundamentals/dynamic-modules)
