# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Architecture (arch)

**Impact:** CRITICAL
**Description:** Proper module organization and dependency management are the foundation of maintainable NestJS applications. This section also covers monorepo ownership boundaries, shared bootstrap design, and external integration layering.

## 2. Dependency Injection (di)

**Impact:** CRITICAL
**Description:** NestJS's IoC container is powerful but can be misused. Understanding scopes, injection tokens, registration APIs, and proper composition patterns is essential for testable code.

## 3. Error Handling (error)

**Impact:** HIGH
**Description:** Consistent error handling improves debugging, user experience, and API reliability. Centralized exception filters and deliberate translation of external failures ensure uniform error responses.

## 4. Security (security)

**Impact:** HIGH
**Description:** Security vulnerabilities can be catastrophic. Input validation, authentication, authorization, rate limiting, secret handling, and safe output are non-negotiable.

## 5. Performance (perf)

**Impact:** HIGH
**Description:** Optimizing request handling, caching, database access, and expensive upstream integrations directly impacts application responsiveness and scalability.

## 6. Testing (test)

**Impact:** MEDIUM-HIGH
**Description:** Well-tested applications are more reliable. NestJS testing utilities should cover both isolated unit behavior and runtime module/bootstrap integration.

## 7. API Design (api)

**Impact:** MEDIUM
**Description:** RESTful conventions, versioning, DTOs, consistent response formats, and explicit contracts improve API usability and maintainability.

## 8. DevOps & Deployment (devops)

**Impact:** LOW-MEDIUM
**Description:** Configuration management, structured logging, correlation IDs, graceful shutdown, and worker conventions ensure production readiness and operability.
