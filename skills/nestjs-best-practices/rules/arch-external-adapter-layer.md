---
title: Isolate Third-Party SDKs Behind Adapter Services
impact: HIGH
impactDescription: Reduces coupling to upstream APIs and makes failures easier to contain and test
tags: architecture, integrations, adapters, testing
---

## Isolate Third-Party SDKs Behind Adapter Services

Wrap third-party SDKs and remote API clients behind focused Nest services or adapters. The rest of the application should depend on an internal contract, not directly on the external package's response shape, retry model, or error format.

**When to apply:**

- Integrating SOAP clients, CMS SDKs, payment providers, search backends, or HTTP APIs
- Sharing an integration package across multiple services

**What to avoid:**

- Letting controllers or business services call third-party SDKs directly
- Spreading vendor-specific response parsing and error handling across the app

**Incorrect (business service knows vendor details):**

```typescript
@Injectable()
export class BookingService {
  async confirmBooking(reference: string) {
    const response = await this.soapClient.ConfirmBookingAsync({ reference });

    if (response[0].ConfirmBookingResult.Status !== "OK") {
      throw new Error(response[0].ConfirmBookingResult.Message);
    }
  }
}
```

**Correct (vendor logic isolated in an adapter):**

```typescript
@Injectable()
export class EliteParksAdapter {
  async confirmBooking(reference: string): Promise<BookingConfirmationResult> {
    const response = await this.client.ConfirmBookingAsync({ reference });
    const result = response[0].ConfirmBookingResult;

    if (result.Status !== "OK") {
      throw new EliteParksError(result.Message);
    }

    return {
      confirmationId: result.ConfirmationId,
      status: "confirmed",
    };
  }
}

@Injectable()
export class BookingService {
  constructor(private readonly eliteParks: EliteParksAdapter) {}

  confirmBooking(reference: string) {
    return this.eliteParks.confirmBooking(reference);
  }
}
```

**Review checklist:**

- Is upstream-specific parsing contained in a narrow adapter layer?
- Can the application be tested against an internal contract rather than the vendor SDK directly?

**Scope boundaries:**

- Applies strongly to shared integrations and high-churn upstream APIs
- Thin wrappers are acceptable for trivial utilities, but the boundary should harden as business importance grows

Reference: [NestJS Providers](https://docs.nestjs.com/providers)
