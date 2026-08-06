# LinkedIn project story

Status: **published by owner on 2026-08-06**. This repository records the owner's report; no
independent external LinkedIn readback was performed during this documentation pass.

I started TenderVerdict with a narrow question:

Can public tender metadata help a small supplier decide which documents are worth opening first?

The first version handled one supplier profile. For RevenueCat Shipaton 2026 Next Gen, I changed
the scope.

The same tender can be worth opening for one supplier, need more checking for another, and be an
immediate reject for a third.

TenderVerdict now evaluates the same notice feed independently for up to five named supplier
profiles. Every notice becomes one clear next step:

- Open documents
- Watch
- Reject

The app keeps the reasons, missing information, source link and next human step visible. It does
not rank suppliers, make a bid decision or pretend that incomplete metadata is certain.

I also wanted the free version to remain useful. One complete supplier review and deterministic
JSON export stay free. RevenueCat unlocks the Portfolio Workspace: multi-profile comparison,
evidence drill-down and the full portfolio export.

The qualification rules do not change after purchase. RevenueCat controls access to the workspace,
not the verdict.

I am a technical student, not a professional software developer. I chose the problem and product
boundaries, reviewed the intermediate versions, tested the application and decided what I was
willing to claim publicly. Codex handled most of the implementation, tests, UI work and release
checks.

The current macOS build uses local files, uploads no tender data and has no telemetry. It passes
125 Python tests and 19 Debug plus 19 Release native checks.

The number alone is not the point. These checks protect narrower promises: deterministic results,
fail-closed errors, identical qualification before and after purchase, and no stored RevenueCat
key.

TenderVerdict is still a competition prototype, not a production procurement tool or legal advice.
But it is now a complete, inspectable workflow rather than a feature mock-up.

One tender feed. A clear next step for every supplier profile.

Source:
https://github.com/demidgost-sys/tenderverdict

#BuildInPublic #PublicProcurement #RevenueCat
