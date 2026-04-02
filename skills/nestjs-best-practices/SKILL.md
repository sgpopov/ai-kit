---
name: nestjs-best-practices
description: NestJS best practices and architecture patterns for production-ready applications and service monorepos. Use this skill when writing, reviewing, or refactoring NestJS modules, shared packages, workers, external integrations, configuration, and operational infrastructure.
---

# NestJS Best Practices

Comprehensive best practices guide for NestJS applications and monorepos. Contains 30+ rules across 8 categories, prioritized by impact to guide code generation, refactoring, review, and architecture decisions.

## When to Apply

Reference these guidelines when:

- Writing new NestJS modules, controllers, or services
- Designing shared NestJS packages in a monorepo
- Defining application bootstrap or worker startup paths
- Integrating third-party APIs, SDKs, queues, or schedulers
- Reviewing code for architecture and security issues
- Refactoring existing NestJS codebases
- Optimizing performance, ContentStack access, or OpenSearch queries

## Rule Categories by Priority

| Priority | Category             | Impact      | Prefix      |
| -------- | -------------------- | ----------- | ----------- |
| 1        | Architecture         | CRITICAL    | `arch-`     |
| 2        | Dependency Injection | CRITICAL    | `di-`       |
| 3        | Error Handling       | HIGH        | `error-`    |
| 4        | Security             | HIGH        | `security-` |
| 5        | Performance          | HIGH        | `perf-`     |
| 6        | Testing              | MEDIUM-HIGH | `test-`     |
| 7        | API Design           | MEDIUM      | `api-`      |
| 9        | DevOps & Deployment  | LOW-MEDIUM  | `devops-`   |

## Quick Reference

### 1. Architecture (CRITICAL)

- `arch-avoid-circular-deps` - Avoid circular module dependencies
- `arch-app-vs-library-boundaries` - Keep application bootstrap out of reusable libraries
- `arch-dynamic-module-configuration` - Expose explicit registration APIs for configurable packages
- `arch-external-adapter-layer` - Isolate third-party SDKs behind Nest services or adapters
- `arch-feature-modules` - Organize by feature, not technical layer
- `arch-module-sharing` - Proper module exports/imports, avoid duplicate providers
- `arch-shared-bootstrap-consistency` - Standardize global Nest setup across services and workers
- `arch-single-responsibility` - Focused services over "god services"
- `arch-use-repository-pattern` - Abstract database logic for testability

### 2. Dependency Injection (CRITICAL)

- `di-avoid-service-locator` - Avoid service locator anti-pattern
- `di-interface-segregation` - Interface Segregation Principle (ISP)
- `di-liskov-substitution` - Liskov Substitution Principle (LSP)
- `di-prefer-constructor-injection` - Constructor over property injection
- `di-scope-awareness` - Understand singleton/request/transient scopes
- `di-use-interfaces-tokens` - Use injection tokens for interfaces

### 3. Error Handling (HIGH)

- `error-use-exception-filters` - Centralized exception handling
- `error-throw-http-exceptions` - Use NestJS HTTP exceptions
- `error-handle-async-errors` - Handle async errors properly

### 4. Security (HIGH)

- `security-validate-all-input` - Validate with class-validator
- `security-rate-limiting` - Implement rate limiting

### 5. Performance (HIGH)

- `perf-async-hooks` - Proper async lifecycle hooks
- `perf-optimize-contentstack` - Reduce CMS round-trips and expensive content traversals
- `perf-lazy-loading` - Lazy load modules for faster startup

### 6. Testing (MEDIUM-HIGH)

- `test-use-testing-module` - Use NestJS testing utilities
- `test-mock-external-services` - Mock external dependencies

### 7. API Design (MEDIUM)

- `api-use-dto-serialization` - DTO and response serialization
- `api-use-interceptors` - Cross-cutting concerns
- `api-versioning` - API versioning strategies
- `api-use-pipes` - Input transformation with pipes

### 8. DevOps & Deployment (LOW-MEDIUM)

- `devops-correlation-id-logging` - Propagate request context through logs and async work
- `devops-worker-bootstrap-conventions` - Keep schedulers, workers, and HTTP services operationally aligned
- `devops-use-config-module` - Environment configuration
- `devops-use-logging` - Structured logging
- `devops-graceful-shutdown` - Zero-downtime deployments

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/arch-avoid-circular-deps.md
rules/security-validate-all-input.md
rules/_sections.md
```

Each rule file contains:

- Brief explanation of why it matters
- When to apply the rule and what scope it covers
- Incorrect code example with explanation
- Correct code example with explanation
- Review checklist for code review or planning
- Additional context and references
