# Data sources and attribution

## Synthetic repository data

All committed profile and notice fixtures are fictional. The matching CSV and JSON examples contain
the same normalized records. Synthetic notice identifiers begin with `SYN-`, and synthetic source
links use reserved domains ending in `.example`. They are not procurement records and must not be
presented as such.

## Optional TED Search API

The explicit `fetch-ted` command can request public notice metadata from the fixed TED Search API
endpoint:

- API endpoint: `https://api.ted.europa.eu/v3/notices/search`
- official documentation: `https://docs.ted.europa.eu/api/latest/search.html`

The adapter is read-only, bounded, and deliberately separate from the offline qualification path.
API availability, schemas, fields, rate limits, records, and provider terms can change independently
of this code.

The Search API returns notice-level rows. The Publications Office has documented that matching
values back to their correct lot can be difficult in its
[TED reusers workshop Q&A](https://op.europa.eu/en/web/ted-reusers-workshops/questions-and-answers-2025).
The current adapter therefore uses lot-specific
CPV, country, and deadline values only when exactly one lot identifier is returned. It withholds
those fields for zero- or multi-lot rows, records a warning, and lets qualification return `watch`
unless an independent hard stop applies. This is a conservative boundary, not full lot-aware
normalization.

Every successful fetch writes one wrapper containing the exact query, fixed endpoint, UTC retrieval
time, `single_lot_only` policy, and the complete normalized notice array. A failed response never
publishes that wrapper; a successful query with zero rows publishes a valid empty snapshot.

Before using fetched data, review the provider's current documentation, legal notice, attribution
requirements, and any restrictions relevant to your jurisdiction and intended use. Retain the
official notice link and verify important facts against the procurement documents.

## Rights boundary

The Apache License 2.0 applies to TenderVerdict code, original repository documentation, and the
original synthetic fixtures. It does not relicense procurement notices, attachments, provider
interfaces, names, logos, or trademarks.
TED is referenced descriptively as the name of an external source; this project is independent from
the European Union and TED service.
