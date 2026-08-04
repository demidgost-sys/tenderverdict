# Shipaton 2026 competition scorecard

- Rechecked: 2026-08-05
- Scope: Next Gen Award, macOS submission path
- Decision rule: verified evidence is separated from inference and open owner gates

This scorecard converts the public judging criteria and recurring winner patterns into product
decisions. It does not predict a result, claim private judge preferences, or replace the controlling
[evidence record](SHIPATON_EVIDENCE.md).

The measurable progress ledger is maintained separately in
[PROJECT_STATUS.md](PROJECT_STATUS.md): 19 of 22 local implementation milestones are complete and
7 of 12 final-submission gates are ready. This scorecard explains quality and strategic fit; the
ledger prevents those judgments from being confused with verified completion.

## Public judges and judging contract

The public Devpost page currently lists Charlie Chapman and David Barnard as judges. The Official
Rules allow the panel to change, so TenderVerdict should be optimized for the published criteria,
not for speculative personal taste.

The Next Gen criteria are paraphrased below from the
[Official Rules](https://revenuecat-shipaton-2026.devpost.com/rules):

| Criterion | What the product must make obvious | Current evidence | State |
|---|---|---|---|
| Problem and experience | A clear, useful, interesting, original answer to a real problem | One notice feed is evaluated differently for several supplier profiles; verdicts remain explainable and human-owned | `STRONG_CONCEPT` |
| Working application | Meaningful progress toward a functioning app, with core behavior visible in the repository and demo | Offline Python core, self-contained macOS app, real local files, deterministic export, and native review UI run locally | `VERIFIED_LOCALLY` |
| RevenueCat and monetization | RevenueCat should control a thoughtful subscription, purchase, ads, or monetization experience | `supplier_profiles_plus` gates the multi-profile comparison while the complete single-profile workflow stays free; Test Store purchase, refresh, relaunch, and restore were exercised | `VERIFIED_TEST_STORE`, eligibility interpretation still `UNKNOWN` |
| Product and technical care | Intentional product decisions, build quality, and a well-presented result | One qualification engine, strict contracts, offline privacy, provenance, failure recovery, accessibility evidence, packaging, and public documentation | `STRONG_WITH_OPEN_QA` |

The remaining weakness is not missing feature volume. It is external proof that the narrow workflow
is genuinely useful, plus the unresolved organizer interpretation of Test Store-only integration.

## What recent winners demonstrate

The following is an inference from RevenueCat's official
[2025 winners](https://www.revenuecat.com/blog/company/shipaton-2025-winners) and
[2024 winners](https://www.revenuecat.com/blog/company/2024-ship-a-ton-winners/) announcements, not
an additional judging rule:

1. A narrow, immediately understandable core loop beats a broad feature inventory.
2. Native polish matters when it supports the task: fast onboarding, clear interaction, haptics or
   animation where appropriate, privacy, offline behavior, and accessibility.
3. Monetization is strongest when Premium expands a real repeated job rather than removing a
   basic safety or trust feature.
4. Personal or observed problem evidence, user feedback, and signs of real use strengthen the
   story more than speculative market claims.
5. Technical ambition helps when the user can feel the result and the repository makes the work
   inspectable.

RevenueCat's own [Shipaton product guidance](https://www.revenuecat.com/blog/engineering/how-to-win-shipaton-part-1-coming-up-with-an-idea)
similarly recommends a minimum lovable product around a real problem and early feedback. Its
[pitch guidance](https://www.revenuecat.com/blog/engineering/how-to-win-shipaton-part-4-pitching-your-app)
puts proof of the working experience ahead of an exhaustive feature tour.

## Product decisions from the scorecard

### Implemented in the current pass

1. The Free surface now contains a real review queue, not only aggregate totals. Each notice shows
   title, buyer, deadline, verdict, and the human next step.
2. Verdict filters and progressive disclosure keep reasons and unknowns available without turning
   the first screen into a wall of text.
3. Valid supplied HTTPS sources open through an explicit safe link in both the native app and the
   self-contained HTML report.
4. Premium now contains a notice-by-profile comparison matrix. It shows independent verdicts and
   explicitly avoids score, ranking, or an automatic recommendation.
5. The Swift decoder validates complete result arrays, result counts, verdict totals, unique notice
   identities, and the shared ordered notice set before anything is presented.
6. A visible offering refresh action improves recovery without weakening the entitlement boundary.

### Next product work before calling the app release-ready

| Priority | Improvement | Current state | Why it matters | Acceptance evidence |
|---|---|---|---|---|
| P1 | Complete accessibility pass | `PARTIAL` | Converts native semantics into verified usability | VoiceOver async announcements, Increase Contrast, Reduce Transparency, and large-text checks |
| P1 | Real-user workflow pass | `OPEN` | Tests whether verdict wording and comparison actually reduce review work | Three opt-in sessions and two documented workflow changes using public, synthetic, or de-identified data |
| P1 | Native profile builder and editor | `EVIDENCE_GATED` | Removes hand-authored JSON only if users confirm it is the main obstacle | Create, rename, reorder, validate, and save 1–5 local profiles without leaving the app |
| P1 | Local workspace continuity | `OPEN` | Makes repeated supplier review feel like a product, not a one-off demo | Explicitly saved recent workspace; no silent upload or hidden telemetry; clear reset action |
| P2 | Notice search and buyer/deadline filters | `FIXTURE_GATED` | Helps only after realistic files exceed the three-row demo | Tested with a bounded 100+ notice fixture; keyboard and screen-reader usable |
| P2 | Profile-focused drill-down | `PARTIAL` | Lets a user move from comparison to evidence without losing context | Selecting a matrix cell opens the matching notice reasoning for that profile |
| P2 | Saved local export presets | `OPEN` | Reduces repeated export friction without creating accounts | User-controlled destination and format choice; atomic writes and recovery tests remain intact |

Do not add cross-profile ranking, bid automation, confidential-document ingestion, hosted accounts,
analytics, or production billing merely to look larger. None fixes the current proof gap, and each
would widen the trust and delivery surface.

## Release and submission gates

The project is not ready for an external release or final Devpost submission until all of these are
true:

- the complete Python, Swift, package, public-tree, and security checks pass on the final candidate;
- the final self-contained app passes launch, local-file run, result review, source link, export,
  failure retention, and entitlement recovery checks;
- the student and academic-email requirement is confirmed in the entrant account;
- the Test Store-only interpretation is answered by the organizer or disclosed as an unresolved
  submission risk;
- exact private Devpost fields are inspected after the owner signs in and joins the hackathon;
- public repository and final submission URLs are intentionally checked while logged out.

The unauthenticated Devpost project page currently stops at registration, so this repository does
not pretend that private form fields have been verified. Publicly documented description, source,
video, icon, screenshot, platform, and eligibility requirements are already tracked in the
[runbook](HACKATHON_RUNBOOK.md).

The same gate set already passed on clean pushed implementation baseline `33dbe87`; it must be
repeated on any later final candidate rather than treated as permanently inherited evidence.

## Owner inputs — later, not required for this implementation pass

When the local product and QA pass is complete, the owner will need to provide or confirm:

1. the organizer's written answer about Test Store-only acceptance, if one arrives;
2. the qualifying academic email and current student-status confirmation inside Devpost;
3. access to the joined Devpost project so its exact private fields can be audited;
4. three opt-in workflow testers or permission to use already identified volunteers;
5. final approval of the exact commit and public claims before any release or submission action.
