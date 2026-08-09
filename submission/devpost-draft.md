# TenderVerdict Next Gen — Devpost draft

> Draft only. Do not publish or submit until the final package, media, eligibility, and logged-out
> URL checks in `docs/HACKATHON_RUNBOOK.md` pass.

## Tagline

One tender feed. A clear next step for every supplier profile.

## The idea in one sentence

TenderVerdict compares public-tender notices across up to five supplier profiles and explains what
to open, verify, or skip before a small supplier team spends hours in the documents.

## Inspiration

A tender is not simply relevant or irrelevant to an entire company. The same notice can fit one
legal entity, country, service line, or deadline policy and fail another. Small supplier teams often
repeat that screening by hand, lose the reasoning, and discover missing metadata too late.

TenderVerdict started with a narrow promise: turn structured notice metadata into an explainable
review queue, never a black-box bid decision. Next Gen brings that promise from one supplier
profile to a portfolio while keeping the complete first-profile workflow free.

## What it does

TenderVerdict loads one normalized notice feed and one to five supplier profiles. Its deterministic
rules check CPV fit, geography, deadline lead time, notice type, and missing fields. Every notice
receives a product-native verdict—`open_documents`, `watch`, or `reject`—plus reasons, unknowns,
source metadata, and a concrete human next step.

The workflow is simple:

1. Build or load supplier profiles and inspect the normalized notice input before analysis.
2. Review one complete supplier profile for free, including every reason, safe source link, filter,
   review brief, and deterministic JSON export.
3. Unlock **Portfolio** with RevenueCat to compare up to five independent profiles, see where their
   outcomes differ, and open the exact evidence behind any comparison cell.

RevenueCat changes presentation access only. It never changes a verdict, creates a score, ranks
suppliers, reads full tender documents, or decides whether to bid.

| Free | Portfolio |
|---|---|
| One complete supplier review | Up to five complete supplier reviews |
| Reasons, unknowns, source links, filters, brief, and JSON | Cross-profile comparison, reasoning drill-down, full brief, and portfolio JSON |

## How we built it

- A Python 3.11+ core owns strict schemas, deterministic qualification, provenance, and atomic
  export.
- A native SwiftUI macOS app handles Profile Builder, input preview, local review, comparison, and
  export without reimplementing the qualification rules.
- The official RevenueCat Apple SDK controls the `supplier_profiles_plus` entitlement through
  offering, Test Store purchase, refresh, foreground recovery, and restore paths.
- Test Store configuration is Debug-only and process-local. No usable key is committed, bundled,
  or remembered; Release refuses Test Store configuration before any SDK call.
- The self-contained evaluation app embeds the bounded Python runtime, synthetic fixtures, license
  notices, native checks, smoke tests, an ad-hoc signature, archive, and checksum.

## Challenges

**Monetization without weakening trust.** One engine produces the same report before and after
unlock; RevenueCat only decides how much of that validated report the native app may present.

**Useful free access.** Free is not a disabled demo. It keeps one complete review, while Portfolio
earns its place by removing repeated cross-profile screening.

**Correct comparison.** Search and filters cannot change the identity of a notice. Comparison cells
therefore resolve by stable profile and result IDs, not by a filtered array position.

## Accomplishments

- One notice feed is evaluated consistently for one to five ordered supplier profiles.
- Profile Builder and import preview make strict local contracts usable without manual JSON edits.
- Free keeps complete reasoning and export; Portfolio adds comparison and full portfolio export.
- Invalid input preserves the last valid report and never replaces an existing export with partial
  output.
- A packaged Debug build completed RevenueCat Test Store cancel, simulated failure, retry, success,
  immediate restore, foreground refresh, relaunch, and accelerated-expiry recovery. This was a Test
  Store evaluation; no real payment occurred.
- Current Judge Access evidence completed refresh, Restore, foreground return, and full relaunch
  without a purchase and without publishing a key, reviewer code, or customer identifier.

## Proof for judging

| Question | Evidence |
|---|---|
| Is the problem specific? | The same three synthetic notices produce visibly different outcomes for three legal-entity and service profiles. |
| Is it a working product? | Profile Builder, import preview, canonical analysis, filters, reasoning drill-down, comparison, briefs, and atomic JSON form one macOS workflow. |
| Is RevenueCat substantive? | `CustomerInfo`, refresh, restore, Test Store purchase state, and Judge Access control the multi-profile Portfolio surface. |
| Does monetization fit? | One complete profile stays useful and free; Portfolio saves repeated review across up to five profiles. |
| Is the boundary honest? | Qualification stays local and deterministic; the evaluation uses synthetic data, Test Store, no stored usable key, and no real charge. |

## Eligibility evidence

- [Shipaton Manager: Test Store-only purchase is acceptable](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient)
- [Shipaton: macOS is eligible with no platform-only disadvantage](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission)

## What we learned

Entitlement-backed UI is clearest when billing state and domain logic stay separate. A useful free
workflow makes the Portfolio value easier to understand, and visible reasoning matters more than a
new score. The strongest product sentence is also the product loop: one feed, different supplier
outcomes, and evidence a person can defend.

## What is next

The app is an ad-hoc-signed competition evaluation build, not a notarized consumer release. The
owner accepted the repaired captioned v2 after a normal-speed watch/listen, its link-accessible URL
is saved in Devpost, and the pushed candidate passes exact-head CI. Every truthful Additional info
value is saved, including store release = false, but final Submit is server-rejected by the
contradictory required-field validation. A public follow-up and direct private manager escalation
are pending.

## Links

- Competition source: `https://github.com/demidgost-sys/tenderverdict/tree/hackathon/revenuecat-next-gen-2026`
- Demo video: `https://www.youtube.com/watch?v=HFBtMsN7Nlk`
- Pushed candidate revision at the finalization attempt: `f7744d1322f90e49dc55b1938218dd4b74669a07`
- Demo master SHA-256: `5862094c00c8dcb5e2e793d46d1ced44a003458dfcb1d957484135da13c6d047`
