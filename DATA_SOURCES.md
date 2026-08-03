# Data sources and attribution

## Synthetic repository data

All committed profile and notice examples are fictional. Matching CSV and JSON fixtures contain
the same normalized rows. Synthetic notice identifiers begin with `SYN-`, and synthetic source
links use reserved domains ending in `.example`. They are not procurement records and must not be
presented as such.

## Bundled EU vocabulary snapshots

TenderVerdict validates CPV and country values offline against two bounded code snapshots queried
from the Publications Office Cellar SPARQL endpoint:

- endpoint: `https://publications.europa.eu/webapi/rdf/sparql`;
- CPV concept namespace: `http://data.europa.eu/cpv/cpv/`;
- country authority namespace:
  `http://publications.europa.eu/resource/authority/country/`;
- retrieval date for this source candidate: `2026-08-04`.

The exact queries, record counts, and SHA-256 digests are committed in
[`src/tenderverdict/data/VOCABULARY_SOURCES.json`](src/tenderverdict/data/VOCABULARY_SOURCES.json).
The generated lists contain 9,454 eight-digit CPV codes and 303 three-letter country authority
codes whose concept status was `CURRENT` at retrieval time. The networked maintainer tool
[`tools/update_vocabularies.py`](tools/update_vocabularies.py) validates every response before it
writes and replaces each generated file atomically. It fails if the response shape, encoding,
ordering, size, or minimum counts are unexpected. Product validation reads only the committed
snapshots and performs no vocabulary network request.

A code's presence proves only membership in that snapshot. It does not prove that the code is
current at a later date, correct for a notice, sufficient for supplier eligibility, or equivalent
to legal scope. Snapshot changes require review, regenerated metadata, tests, and a new commit.

## Optional TED Search API and eForms XML

The explicit `fetch-ted` command can request public notice metadata from fixed official endpoints:

- Search API: `https://api.ted.europa.eu/v3/notices/search`;
- official API documentation: `https://docs.ted.europa.eu/api/latest/search.html`;
- official field reference: `https://docs.ted.europa.eu/ODS/latest/reuse/field-list.html`;
- eForms identifier and lot model:
  `https://docs.ted.europa.eu/eforms/latest/schema/identifiers.html`.

The adapter is read-only, bounded, and deliberately separate from the offline demo and
qualification paths. API availability, schemas, fields, rate limits, records, and provider terms
can change independently of this code.

Search results are notice-level. For exactly one returned lot identifier, TenderVerdict uses the
single-lot fields directly. For multiple identifiers, it retrieves the notice's official eForms
XML from the fixed `https://ted.europa.eu/en/notice/{publication-number}/xml` route. It rejects
document types/entities, non-XML responses, oversized documents, malformed XML, invalid or
duplicate identifiers, and any Search/XML lot mismatch. Only then does it create one row per lot
with lot-scoped CPV, country, and submission deadline evidence. A bounded fetch can use at most 100
lot XML documents and produce at most 1,000 normalized rows.

The snapshot records the exact Search query, fixed endpoint, UTC retrieval time, and
`xml_expanded_lots_v1` policy. A network or validation failure never publishes a partial wrapper;
a successful query with zero notices publishes a valid empty snapshot. `retrieved_at` records when
TenderVerdict completed its request. It does not prove that the provider record was complete,
unchanged, or current at that time.

Before using fetched data, review the provider's current documentation, legal notice, attribution
requirements, and any restrictions relevant to your jurisdiction and intended use. Retain the
official notice link and verify important facts against the procurement documents.

## Rights boundary

The Apache License 2.0 applies to TenderVerdict code, original repository documentation, and the
original synthetic fixtures. It does not relicense CPV/country vocabulary data, procurement
notices, attachments, provider interfaces, names, logos, or trademarks. TED and EU Vocabularies
are referenced descriptively as external sources; this project is independent from the European
Union and TED service.
