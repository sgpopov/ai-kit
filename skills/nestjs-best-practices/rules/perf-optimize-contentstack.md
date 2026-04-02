---
title: Optimize Contentstack Queries
impact: HIGH
impactDescription: CMS calls are often one of the largest sources of API latency
tags: performance, contentstack, cms, queries, optimization
---

## Optimize Contentstack Queries

Fetch only the fields and references the endpoint actually needs, paginate large content types, and avoid loading broad reference trees by default. In this codebase, slow CMS-backed endpoints usually come from over-fetching Contentstack entries rather than from expensive in-process logic.

**Incorrect (over-fetching entries and loading references too broadly):**

```typescript
@Injectable()
export class ParksService {
  constructor(private readonly contentstackService: ContentstackService) {}

  async getParkSummaries() {
    const parks = await this.contentstackService.getAllEntries<ParkEntry>("park_page", ["brand", "brand.brand_logo", "holiday_page_content.park_info_section.gallery", "holiday_page_content.park_info_section.facilities", "location.address.county"]);

    // Pulls full park documents and a wide reference graph
    return parks.map((park) => ({
      title: park.title,
      slug: park.url,
      county: park.location?.address?.county?.title,
    }));
  }

  async getAllOffers() {
    // Fetches the entire content type in one call with no pagination
    return this.contentstackService.getAllEntries<OfferEntry>("content_offers");
  }
}
```

**Correct (select only needed fields, include narrow references, and paginate):**

```typescript
@Injectable()
export class ParksService {
  constructor(private readonly contentstackService: ContentstackService) {}

  async getParkSummaries() {
    const [parks] = await this.contentstackService.query("park_page").selectBaseFields(["title", "url", "park_code", "location"]).loadReferences(["location.address.county"]).pagination(0, 50).includeTotalCount().find<[ParkEntry[], number]>();

    return parks.map((park) => ({
      title: park.title,
      slug: park.url,
      county: park.location?.address?.county?.title,
    }));
  }

  async getParkMenu(entryId: string) {
    return this.contentstackService.getSingleEntry<ParkEntry>("park_page", entryId, ["park_menu_pdf"]);
  }
}

export class ParksStep extends BaseSitemapStep implements StepsContract {
  async getAllParkUrls(): Promise<ParkEntry[]> {
    return this.fetchEntriesRecursively<ParkEntry>({
      type: "park_page",
      selectFields: ["url", "updated_at"],
      includeReferences: [],
      size: 100,
    });
  }
}
```

Prefer these patterns when calling Contentstack:

- Use `selectBaseFields(...)` or `only(...)` whenever the endpoint does not need the full entry payload.
- Keep `includeReference(...)` scoped to the exact path the response needs, for example `park_menu_pdf` or `location.address.county`, rather than loading a broad reference tree.
- Use `getSingleEntry(...)` or `findOne()` for single-entry reads instead of fetching a whole collection and filtering in memory.
- Paginate large content types with `skip(...)`, `limit(...)`, and `includeCount()` or the shared recursive fetch helper when all entries are required.
- Apply filters in the Contentstack query itself with `where(...)`, `containedIn(...)`, `referenceIn(...)`, and conditional query-builder steps instead of downloading extra entries and trimming them in application code.

Reference: [packages/contentstack/src/query-builder.ts](/Users/svilen/code/parkholidays/parkholidays-services/packages/contentstack/src/query-builder.ts)
