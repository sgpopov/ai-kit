---
title: Separate Application Bootstrap from Reusable Libraries
impact: CRITICAL
impactDescription: Prevents implicit side effects and unstable module composition in monorepos
tags: architecture, monorepo, modules, configuration
---

## Separate Application Bootstrap from Reusable Libraries

Keep application concerns in service apps and keep reusable packages focused on providing modules, services, and explicit registration APIs. Shared libraries should not assume ownership of environment loading, global app configuration, or process-level bootstrap behavior.

**When to apply:**

- Building Nest packages intended to be reused by multiple services
- Splitting a monolith into service apps and internal libraries

**What to avoid:**

- Calling application bootstrap APIs from shared packages
- Making library import order determine environment validation or runtime behavior

**Incorrect (library owns application concerns):**

```typescript
@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
  ],
  providers: [PaymentsService],
  exports: [PaymentsService],
})
export class PaymentsModule {}
```

**Correct (app owns bootstrap, library stays reusable):**

```typescript
@Module({
  providers: [PaymentsService],
  exports: [PaymentsService],
})
export class PaymentsModule {}

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    PaymentsModule,
  ],
})
export class AppModule {}
```

**Review checklist:**

- Does the reusable library stay free of app bootstrap side effects?
- Could multiple apps import the package without hidden ownership conflicts?

**Scope boundaries:**

- Applies strongly in Nx or monorepo workspaces with shared Nest libraries
- Single-application packages can be less strict, but the boundary is still useful if reuse is likely

Reference: [NestJS Modules](https://docs.nestjs.com/modules)
