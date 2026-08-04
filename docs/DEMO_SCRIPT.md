# Two-minute Shipaton demo script

Target duration: **1:55**. Record the packaged macOS app, not `swift run`. Keep the cursor deliberate
and the window large enough to read.

| Time | Screen action | Narration point |
|---|---|---|
| 0:00–0:12 | Show title and synthetic result | Suppliers often need to review the same tender feed for several legal entities or service profiles. |
| 0:12–0:27 | Point to Local analysis, Schema verified, and the Free card | TenderVerdict applies explainable, deterministic metadata rules locally; the first profile remains free. |
| 0:27–0:45 | Choose the three-profile workspace and notices, confirm `as_of`, run | One bounded notice set is parsed once and evaluated independently for each named profile. |
| 0:45–0:58 | Show Free metrics and export | The existing schema-3 report and deterministic JSON export are preserved; there is no ranking or black-box score. |
| 0:58–1:15 | Show locked Premium section and connect the Test Store key off-camera/pasted | The native Portfolio Workspace is gated by RevenueCat entitlement `supplier_profiles_plus`; the key is not stored. |
| 1:15–1:30 | Run the official Test Store purchase | RevenueCat owns the offering, purchase result, and `CustomerInfo` entitlement state. State exactly that this is Test Store with no real charge. |
| 1:30–1:44 | Show all profile cards after success | Active entitlement reveals the complete portfolio without changing any qualification result. |
| 1:44–1:53 | Restore or relaunch and show access returning | Restore/relaunch proves the UI is driven by RevenueCat access state rather than a local demo toggle. |
| 1:53–1:55 | End card/window | Open-source macOS app, public repository, Apache-2.0. |

## Recording rules

- Do not show the API key, account email, browser cookies, dashboard secrets, or unrelated files.
- Use only committed synthetic notices and profiles.
- Show the RevenueCat purchase sheet and the resulting unlocked app state in one continuous cut.
- If restore cannot fit under two minutes, show it in a short accelerated segment, but do not hide a
  failure or splice a fake state.
- Avoid calling the verdicts legal decisions, recommendations, or AI predictions.
- Publish to public YouTube or Vimeo only after the final cut is checked at normal speed with sound.
