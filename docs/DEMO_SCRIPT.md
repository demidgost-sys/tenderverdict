# Shipaton demo script

Target duration: **1:48**. This is a ready-to-record script for the final packaged Debug build; it
does not require recording during implementation. Keep the app window readable and use committed
synthetic data only.

| Time | Screen action | Narration |
|---|---|---|
| 0:00–0:08 | Show the TenderVerdict hero and Portfolio Signal with three profiles, three notices, and two changed outcomes. | One tender feed. A clear next step for every supplier profile. TenderVerdict shows what to open, verify, or skip, with reasons a human can defend. |
| 0:08–0:22 | Open **Build profiles…**; show names, CPVs, countries, lead time, ordering, and **Validate & Save As…**; close without changing the prepared fixture. | The native Profile Builder creates one to five named profiles and validates every value through the canonical bundled rules—no hand-edited JSON required. |
| 0:22–0:36 | Choose the committed workspace and notices. Pause on the import preview and its metadata-gap badges, leave bookmark continuity visibly optional, then run. | Before analysis, the import preview shows the file type, total notices, sample records, and missing metadata. Remembering only the two file bookmarks is explicit opt-in; no report, review date, or key is stored. |
| 0:36–0:52 | In the always-free first report, show the one Open / one Watch / one Reject summary, search or choose buyer/deadline/verdict filters, expand **Why this verdict**, and point to Export JSON. | The first complete analysis and deterministic export stay free. The UI separates verdict drivers, confirmation items, and passed checks without changing the report. |
| 0:52–1:02 | Show the Free/Portfolio packaging, cross-profile disagreement count, and the current localized Test Store package already loaded. Do not show the key. | Free keeps one complete supplier review. RevenueCat controls one meaningful upgrade: up to five profiles, their comparison, and the full portfolio export. This is the official Test Store path, with no real charge. |
| 1:02–1:24 | Run the real RevenueCat Test Store purchase and keep the purchase sheet plus resulting unlocked state in one continuous segment. | RevenueCat owns the offering, purchase outcome, and `CustomerInfo` entitlement. The qualification results never change when access unlocks. |
| 1:24–1:40 | Filter the shared comparison, select a verdict cell, and show that profile/notice detail with reasons and next step. | Each cell is an independent verdict, never a score or ranking. One click opens the exact evidence for that supplier and notice. |
| 1:40–1:46 | Close the detail and activate **Restore access**; show the unlocked state returning or remaining active. | Restore proves access comes from RevenueCat state, not a hidden demo switch. |
| 1:46–1:48 | End on the unlocked product title or repository end card. | Open source, macOS, Apache 2.0. |

## Capture setup

- Build the exact final revision with `--configuration debug`; Test Store purchases do not run in
  the ordinary Release package.
- Record only after the full verification emits its `NEXT_GEN_CHECKS_OK` completion marker in both
  Debug and Release on that final revision; use [project status](PROJECT_STATUS.md) for the expected
  current total.
- Prepare the selected synthetic files and a valid `test_` key before capture. Connect the offering
  without showing the key, terminal, account email, or RevenueCat dashboard secrets.
- Keep the RevenueCat purchase sheet and resulting entitlement state in one continuous segment.
  Cuts may tighten navigation elsewhere, but must not hide a failure or fabricate state.
- If the Test Store sheet or Restore exceeds the budget, shorten the Profile Builder and filter
  pauses first. Keep the final published video **at or below 1:50** and the official under-two-minute
  limit.
- State **Test Store, no real charge**. Do not call it an App Store payment.
- Avoid calling verdicts legal decisions, recommendations, AI predictions, scores, or rankings.
- Add accurate captions, then check the final public YouTube/Vimeo cut at normal speed with sound
  before entering its URL in Devpost.
