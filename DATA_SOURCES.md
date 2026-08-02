# Data sources and attribution

## Synthetic repository data

All committed profile and notice fixtures are fictional. Synthetic notice identifiers begin with
`SYN-`, and synthetic source links use reserved domains ending in `.example`. They are not
procurement records and must not be presented as such.

## Optional TED Search API

The explicit `fetch-ted` command can request public notice metadata from the fixed TED Search API
endpoint:

- API endpoint: `https://api.ted.europa.eu/v3/notices/search`
- official documentation: `https://docs.ted.europa.eu/api/latest/search.html`

The adapter is read-only, bounded, and deliberately separate from the offline qualification path.
API availability, schemas, fields, rate limits, records, and provider terms can change independently
of this code.

Before using fetched data, review the provider's current documentation, legal notice, attribution
requirements, and any restrictions relevant to your jurisdiction and intended use. Retain the
official notice link and verify important facts against the procurement documents.

## Rights boundary

The Apache License 2.0 applies to TenderVerdict code, original repository documentation, and the
original synthetic fixtures. It does not relicense procurement notices, attachments, provider
interfaces, names, logos, or trademarks.
TED is referenced descriptively as the name of an external source; this project is independent from
the European Union and TED service.
