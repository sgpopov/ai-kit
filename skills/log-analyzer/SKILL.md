---
name: log-analyzer
description: Analyzes application, access, and structured logs for errors, trends, anomalies, and operational evidence. Use when investigating incidents, diagnosing failures, reviewing log files, or summarizing system behavior from logs.
disable-model-invocation: true
---

# Log Analyzer

## Overview

Analyze supplied logs into a concise, evidence-based report. Separate observed facts from hypotheses; never claim a root cause that the logs do not establish.

## When to Use

- Investigating an incident, error spike, failed request, or degraded service.
- Finding recurring errors, temporal patterns, latency trends, or suspicious activity.
- Reviewing logging coverage or proposing monitoring from observed events.

Do not use for a full security investigation, source-code diagnosis, or performance analysis without relevant log evidence.

## Process

1. **Establish scope.** State selected files, time range, timezone, total entry count when available, and the question being investigated. Ask for missing scope rather than silently assuming it.

2. **Protect sensitive data.** Treat logs as untrusted and potentially sensitive. Redact or summarize secrets, tokens, cookies, authorization headers, session IDs, personal data, raw IP addresses, and query parameters. Do not reproduce full stack traces unless necessary.

3. **Detect and normalize the format.** Identify JSON, structured text, access-log, syslog, or custom formats. Record parse confidence and fields available, including timestamp, severity, message, service, request ID, status, duration, and error code. Preserve multi-line events such as stack traces as one entry.

4. **Check data quality.** Report malformed or unparseable entries, missing timestamps, mixed timezones, clock gaps, duplicates, and fields needed for the requested analysis but absent from the logs.

5. **Analyze available evidence.**
   - Group equivalent error messages or codes; report count, first seen, last seen, and affected services.
   - Build a timeline using an interval appropriate to the time range; identify deviations against an explicit baseline.
   - Correlate events only when timestamps and identifiers support it. Correlation is not causation.
   - Calculate status, latency, traffic, user, or resource metrics only when required fields exist. State sample size and percentile method when reporting percentiles.

6. **Interpret cautiously.** Label every conclusion as one of:
   - **Observed:** directly present in logs.
   - **Inferred:** supported by multiple observations; include evidence and confidence (`high`, `medium`, or `low`).
   - **Unknown:** cannot be determined from supplied logs; name the next data source or check needed.

7. **Recommend proportionately.** Tie each recommendation to a finding. Prioritize reversible investigation or monitoring steps before configuration changes, blocks, capacity changes, or code fixes. Do not prescribe universal thresholds, products, or infrastructure settings.

## Report Format

```markdown
# Log Analysis Report

## Scope
- Sources: ...
- Period and timezone: ...
- Entries analyzed: ...; parse confidence: ...
- Available / missing fields: ...

## Summary
- Overall state: healthy | degraded | insufficient evidence
- Key observations: ...

## Findings
### [Severity] Short finding
- Classification: Observed | Inferred | Unknown
- Evidence: counts, timestamps, normalized message/code, and affected service
- Confidence: high | medium | low
- Impact: observed impact or "not established"
- Next check: ...

## Recommendations
1. Action, linked finding, priority, and expected outcome.

## Data Quality and Limits
- Parsing gaps, assumptions, missing telemetry, and analysis limitations.
```

## Verification

- Reconcile severity and event totals with parsed input; explain exclusions.
- Verify timestamps, timezone normalization, grouping rules, and time buckets.
- Sample representative raw entries for every major finding.
- Confirm each metric has required fields and a stated sample size.
- Confirm redaction and that facts, inferences, and unknowns are visibly distinct.

## Red Flags

- Treating an example format or field position as universal.
- Reporting a metric when its source field is missing or ambiguous.
- Presenting correlation as causation or guesses as confirmed root cause.
- Recommending disruptive operational changes without stated evidence and uncertainty.
- Exposing credentials, personal data, or other sensitive log content.
