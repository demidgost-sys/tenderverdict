# TenderVerdict qualification report

- **Company:** Example Software GmbH
- **As of:** 2026-08-02
- **Notices:** 3

## Provenance

- **Generator:** TenderVerdict 0.2.0a1
- **Source kind:** synthetic\_demo
- **Profile SHA-256:** `0a50cb80e9d2f9f61f6d7f9e5f24e5abaaf185ea985507c11cf922d0a2403d6a`
- **Notices SHA-256:** `2bc23dc112526168591bc7922b477b2cb1dd73b00d1fc941db89cbd209f59a5d`

## Summary

- **open_documents:** 1
- **watch:** 1
- **reject:** 1

## SYN\-OPEN\-001 — Application maintenance services

- **Verdict:** `open_documents`
- **Buyer:** Example City Procurement Office
- **Deadline:** 2026-09-15
- **Published:** 2026-08-01
- **Source:** https://procurement\.example/notices/SYN\-OPEN\-001

### Reasons

- Notice type is competition\.
- Notice title is supplied\.
- Buyer metadata is supplied\.
- Submission deadline leaves 44 days, meeting the 14\-day minimum\.
- Exact CPV match: 72260000\.
- Country match: AUT\.
- A syntactically valid HTTPS source URL is supplied\.

### Unknowns

- None from the supplied metadata.

**Human next step:** Open and review the official procurement documents; a human decides whether to proceed\.

## SYN\-WATCH\-001 — Software support services

- **Verdict:** `watch`
- **Buyer:** Example Regional Authority
- **Deadline:** 2026-09-20
- **Published:** 2026-07-30
- **Source:** https://procurement\.example/notices/SYN\-WATCH\-001

### Reasons

- Notice type is competition\.
- Notice title is supplied\.
- Buyer metadata is supplied\.
- Submission deadline leaves 49 days, meeting the 14\-day minimum\.
- Four\-digit CPV class match only: profile 72260000, notice 72261000\.
- Country match: DEU\.
- A syntactically valid HTTPS source URL is supplied\.

### Unknowns

- Confirm the exact procurement scope in the documents\.

**Human next step:** Verify the flagged metadata before opening the procurement documents\.

## SYN\-REJECT\-001 — Software implementation services

- **Verdict:** `reject`
- **Buyer:** Example Federal Agency
- **Deadline:** 2026-08-05
- **Published:** 2026-07-15
- **Source:** https://procurement\.example/notices/SYN\-REJECT\-001

### Reasons

- Notice type is competition\.
- Notice title is supplied\.
- Buyer metadata is supplied\.
- Submission deadline leaves 3 days, below the 14\-day minimum\.
- Exact CPV match: 72260000\.
- Country match: AUT\.
- A syntactically valid HTTPS source URL is supplied\.

### Unknowns

- None from the supplied metadata.

**Human next step:** Stop review unless the notice metadata is corrected\.

---

Metadata-only decision support. No legal advice and no autonomous participation decision.
