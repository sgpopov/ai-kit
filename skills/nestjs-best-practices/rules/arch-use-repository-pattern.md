---
title: Use Repository Pattern for Content Access
impact: HIGH
impactDescription: Decouples business logic from ContentStack and content-query details
tags: architecture, repository, contentstack, cms
---

## Use Repository Pattern for Content Access

Create focused repository or gateway services to encapsulate ContentStack queries, entry mapping, and content-fetching conventions. This keeps application services focused on business logic, makes testing easier with mocked content providers, and prevents ContentStack SDK details from leaking across the codebase.

**When to apply:**

- Reading pages, park content, navigation, forms, or shared content from ContentStack
- Reusing the same entry query, include depth, locale, or mapping rules in multiple services

**What to avoid:**

- Calling the ContentStack SDK directly from controllers or high-level business services
- Mixing entry fetch logic, include rules, and response mapping with business workflows

**Incorrect (ContentStack queries embedded in services):**

```typescript
// ContentStack SDK details leak into the service
@Injectable()
export class ParksService {
  constructor(private readonly contentstackClient: Stack) {}

  async getParkBySlug(slug: string): Promise<ParkPageDto> {
    const response = await this.contentstackClient.ContentType("park").Query().where("url", `/${slug}`).includeReference(["region", "offers", "facilities"]).toJSON().find();

    const entry = response[0][0];

    if (!entry) {
      throw new NotFoundException("Park not found");
    }

    return {
      slug: entry.url,
      title: entry.title,
      regionName: entry.region?.title,
      offers: entry.offers ?? [],
    };
  }
}
```

**Correct (repository encapsulates ContentStack access):**

```typescript
@Injectable()
export class ParksContentRepository {
  constructor(private readonly contentstackClient: Stack) {}

  async findParkEntryBySlug(slug: string): Promise<ParkEntry | null> {
    const response = await this.contentstackClient.ContentType("park").Query().where("url", `/${slug}`).includeReference(["region", "offers", "facilities"]).toJSON().find();

    return response[0][0] ?? null;
  }

  async findParkSummariesByRegion(regionSlug: string): Promise<ParkSummaryEntry[]> {
    const response = await this.contentstackClient.ContentType("park").Query().where("region.slug", regionSlug).includeReference(["region"]).only(["title", "url", "region"]).toJSON().find();

    return response[0] as ParkSummaryEntry[];
  }
}

@Injectable()
export class ParksService {
  constructor(private readonly parksContent: ParksContentRepository) {}

  async getParkBySlug(slug: string): Promise<ParkPageDto> {
    const entry = await this.parksContent.findParkEntryBySlug(slug);

    if (!entry) {
      throw new NotFoundException("Park not found");
    }

    return {
      slug: entry.url,
      title: entry.title,
      regionName: entry.region?.title,
      offers: entry.offers ?? [],
    };
  }
}
```

**Review checklist:**

- Are ContentStack queries and reference/include rules isolated from higher-level business services?
- Can the service layer be tested against a repository contract instead of the raw ContentStack SDK?

**Scope boundaries:**

- Applies to CMS-backed reads and content composition logic, even if the abstraction is named `repository`, `gateway`, or `content service`
- If the abstraction becomes mostly vendor-protocol translation rather than content retrieval, the external adapter rule may be a better fit

Reference: [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
