import Foundation
import TenderVerdictNextGenCore

enum CheckFailure: Error, LocalizedError {
  case failed(String)

  var errorDescription: String? {
    switch self {
    case .failed(let message):
      return message
    }
  }
}

@main
enum TenderVerdictNextGenChecks {
  static func main() throws {
    try checkPortfolioContractPreservesFreeAndPremiumSurfaces()
    try checkPortfolioContractPreservesResultDetails()
    try checkPortfolioContractAcceptsEmptyNoticeSet()
    try checkPortfolioContractRejectsInconsistentProfileCount()
    try checkPortfolioContractRejectsDifferentNoticeDigests()
    try checkPortfolioContractRejectsDifferentNoticeOrder()
    try checkPortfolioContractRejectsInvalidNestedTotals()
    try checkPortfolioContractRejectsResultSummaryMismatch()
    try checkWorkspaceDocumentIsStrictBoundedAndDeterministic()
    try checkNoticeImportPreviewContract()
    try checkReviewQueryAndStableResultLookup()
    try checkLargeReviewQueryPreservesStableIdentities()
    try checkPremiumAccessibilityOutcomes()
    try checkTestStoreConfigurationFailsClosed()
    try checkProcessAdapterPreservesDeterministicBytes()
    print("NEXT_GEN_CHECKS_OK checks=15")
  }

  private static func checkPortfolioContractPreservesFreeAndPremiumSurfaces() throws {
    let report = try PortfolioWorkspaceReport.decode(makeReportData(profileCount: 3))

    try require(report.schemaVersion == 1, "workspace schema was not preserved")
    try require(report.summary.profileCount == 3, "profile count was not preserved")
    try require(report.summary.noticeCount == 3, "notice count was not preserved")
    try require(
      report.visibleProfileReports(premiumUnlocked: false).map(\.profile.name),
      equals: ["Profile 1"],
      "free projection exposed more than one profile"
    )
    try require(
      report.visibleProfileReports(premiumUnlocked: true).map(\.profile.name),
      equals: ["Profile 1", "Profile 2", "Profile 3"],
      "premium projection did not preserve profile order"
    )
  }

  private static func checkPortfolioContractRejectsInconsistentProfileCount() throws {
    let data = try makeReportData(profileCount: 2, declaredProfileCount: 3)
    try requireContractError(.inconsistentProfileCount, data: data)
  }

  private static func checkPortfolioContractPreservesResultDetails() throws {
    let report = try PortfolioWorkspaceReport.decode(makeReportData(profileCount: 1))
    let result = try requireFirst(report.profileReports[0].results, "result details were omitted")

    try require(result.publicationNumber == "SYN-OPEN-001", "publication number changed")
    try require(result.title == "Application maintenance services", "title changed")
    try require(result.verdict == .openDocuments, "verdict changed")
    try require(result.reasons.count == 2, "reasons changed")
    try require(result.unknowns.isEmpty, "unknowns changed")
    try require(
      result.humanNextStep == "Open and review the official procurement documents.",
      "human next step changed"
    )
  }

  private static func checkPortfolioContractAcceptsEmptyNoticeSet() throws {
    let report = try PortfolioWorkspaceReport.decode(
      makeReportData(profileCount: 2, noticeCount: 0)
    )
    try require(report.summary.noticeCount == 0, "empty notice count changed")
    try require(
      report.profileReports.allSatisfy { profile in
        profile.results.isEmpty && profile.summary.total == 0
      },
      "empty notice results were not preserved"
    )
  }

  private static func checkPortfolioContractRejectsDifferentNoticeDigests() throws {
    let data = try makeReportData(
      profileCount: 2,
      secondNoticeDigest: String(repeating: "b", count: 64)
    )
    try requireContractError(.inconsistentNoticeSet, data: data)
  }

  private static func checkPortfolioContractRejectsDifferentNoticeOrder() throws {
    let data = try makeReportData(profileCount: 2, reverseSecondResults: true)
    try requireContractError(.inconsistentNoticeSet, data: data)
  }

  private static func checkPortfolioContractRejectsInvalidNestedTotals() throws {
    let data = try makeReportData(profileCount: 1, invalidNestedTotal: true)
    try requireContractError(.invalidProfileReport, data: data)
  }

  private static func checkPortfolioContractRejectsResultSummaryMismatch() throws {
    let data = try makeReportData(profileCount: 2, mismatchSecondSummary: true)
    try requireContractError(.invalidProfileReport, data: data)
  }

  private static func checkWorkspaceDocumentIsStrictBoundedAndDeterministic() throws {
    let profile = try SupplierProfile(
      name: "Example Austria Services",
      cpvCodes: ["72260000", "72261000"],
      countries: ["AUT", "DEU"],
      minimumDaysToDeadline: 14
    )
    let document = try PortfolioWorkspaceDocument(profiles: [profile])
    let first = try document.normalizedJSONData()
    let second = try document.normalizedJSONData()

    try require(first == second, "workspace encoding was not deterministic")
    try require(first.last == 0x0a, "workspace encoding did not end with a newline")
    try require(
      try PortfolioWorkspaceDocument.decode(first) == document,
      "workspace encoding did not round trip"
    )

    let profilePayload: [String: Any] = [
      "schema_version": 1,
      "name": "Example Austria Services",
      "cpv_codes": ["72260000"],
      "countries": ["AUT"],
      "minimum_days_to_deadline": 14,
    ]
    let unknown = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [profilePayload],
        "unexpected": true,
      ]
    )
    try requireThrows("workspace unknown fields were accepted") {
      _ = try PortfolioWorkspaceDocument.decode(unknown)
    }

    let empty = try JSONSerialization.data(
      withJSONObject: ["schema_version": 1, "profiles": []]
    )
    try requireThrows("an empty workspace was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(empty)
    }

    let tooManyProfiles = (1...6).map { index in
      profilePayload.merging(["name": "Profile \(index)"]) { _, replacement in replacement }
    }
    let oversizedEnvelope = try JSONSerialization.data(
      withJSONObject: ["schema_version": 1, "profiles": tooManyProfiles]
    )
    try requireThrows("a six-profile workspace was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(oversizedEnvelope)
    }

    let duplicate = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [
          profilePayload,
          profilePayload.merging(["name": "example austria services"]) { _, replacement in
            replacement
          },
        ],
      ]
    )
    try requireThrows("duplicate workspace profile names were accepted") {
      _ = try PortfolioWorkspaceDocument.decode(duplicate)
    }

    let unnormalizedProfile = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [
          profilePayload.merging(["countries": ["aut"]]) { _, replacement in replacement }
        ],
      ]
    )
    try requireThrows("unnormalized workspace countries were accepted") {
      _ = try PortfolioWorkspaceDocument.decode(unnormalizedProfile)
    }

    let invalidMinimum = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [
          profilePayload.merging(["minimum_days_to_deadline": 3_651]) { _, replacement in
            replacement
          }
        ],
      ]
    )
    try requireThrows("an out-of-range minimum deadline was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(invalidMinimum)
    }

    try requireThrows("oversized workspace data was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(
        Data(repeating: 0x20, count: PortfolioWorkspaceDocument.maximumBytes + 1)
      )
    }
  }

  private static func checkNoticeImportPreviewContract() throws {
    let preview = try NoticeImportPreview.decode(makeNoticePreviewData())

    try require(preview.schemaVersion == 1, "notice preview schema changed")
    try require(preview.kind == "notice_import_preview", "notice preview kind changed")
    try require(preview.sourceKind == "local_json", "notice preview source changed")
    try require(preview.noticeCount == 2, "notice preview count changed")
    try require(preview.preview.count == 1, "notice preview limit changed")
    try require(
      preview.canonicalFields == NoticeImportPreview.expectedCanonicalFields,
      "notice preview canonical fields changed"
    )
    let row = try requireFirst(preview.preview, "notice preview row was omitted")
    try require(row.lotID == "LOT-0001", "notice preview lot changed")
    try require(row.deadlineAt == "2026-09-15T12:00:00+02:00", "exact deadline changed")
    try require(row.metadataWarnings == ["Public warning"], "metadata warnings changed")
    try require(preview.missingFieldCounts.buyer == 1, "missing buyer count changed")
    try require(preview.missingFieldCounts.deadline == 1, "missing deadline count changed")

    try requireThrows("non-canonical notice fields were accepted") {
      _ = try NoticeImportPreview.decode(
        makeNoticePreviewData(canonicalFields: ["publication_number"])
      )
    }
    try requireThrows("a preview row with two deadlines was accepted") {
      _ = try NoticeImportPreview.decode(makeNoticePreviewData(includeBothDeadlines: true))
    }
    try requireThrows("an impossible missing-field count was accepted") {
      _ = try NoticeImportPreview.decode(makeNoticePreviewData(missingBuyerCount: 3))
    }
    try requireThrows("an oversized notice preview was accepted") {
      _ = try NoticeImportPreview.decode(
        Data(repeating: 0x20, count: NoticeImportPreview.maximumBytes + 1)
      )
    }
  }

  private static func checkReviewQueryAndStableResultLookup() throws {
    let report = try PortfolioWorkspaceReport.decode(makeReportData(profileCount: 3))
    let primary = report.profileReports[0]

    let searched = ReviewQuery(
      searchText: "software support",
      buyerText: "Example Regional Authority",
      deadlinePresence: .supplied
    ).apply(to: primary.results)
    try require(searched.count == 1, "review search did not narrow to one notice")
    try require(searched[0].publicationNumber == "SYN-WATCH-001", "review search found wrong row")
    try require(
      ReviewQuery(buyerText: "Example Regional").apply(to: primary.results).isEmpty,
      "buyer picker filter used a prefix match instead of exact normalized equality"
    )

    let separatorIdentity = NoticeIdentity(
      publicationNumber: "A\u{1f}LOT-0001",
      lotID: nil
    )
    let structuredIdentity = NoticeIdentity(publicationNumber: "A", lotID: "LOT-0001")
    try require(
      separatorIdentity != structuredIdentity,
      "notice identity was vulnerable to delimiter collisions"
    )
    try require(
      NoticeIdentity(publicationNumber: "ABC", lotID: nil)
        != NoticeIdentity(publicationNumber: "ＡＢＣ", lotID: nil),
      "notice identity collapsed Python-distinct width variants"
    )
    try require(
      NoticeIdentity(publicationNumber: "ABC", lotID: "LOT")
        == NoticeIdentity(publicationNumber: "abc", lotID: "lot"),
      "notice identity stopped mirroring Python case-insensitive duplicate handling"
    )

    let missingDeadline = ReviewQuery(deadlinePresence: .missing).apply(to: primary.results)
    try require(missingDeadline.count == 1, "missing-deadline filter changed")
    try require(
      missingDeadline[0].publicationNumber == "SYN-REJECT-001",
      "missing-deadline filter found wrong row"
    )

    let secondProfile = report.profileReports[1]
    let resolved = report.result(profileID: secondProfile.id, resultID: missingDeadline[0].id)
    try require(resolved?.publicationNumber == "SYN-REJECT-001", "stable lookup used row offset")
    try require(
      report.profileReport(id: secondProfile.id) == secondProfile, "profile lookup failed")
    try require(
      report.result(profileID: "missing", resultID: missingDeadline[0].id) == nil,
      "unknown profile lookup did not fail closed"
    )
  }

  private static func checkLargeReviewQueryPreservesStableIdentities() throws {
    let report = try PortfolioWorkspaceReport.decode(
      makeLargeReportData(profileCount: 3, noticeCount: 125)
    )
    let primary = report.profileReports[0]
    let missing = ReviewQuery(deadlinePresence: .missing).apply(to: primary.results)
    try require(missing.count == 13, "large missing-deadline filter changed")

    let searched = ReviewQuery(
      searchText: "0124 synthetic service",
      buyerText: "Example Buyer 05",
      deadlinePresence: .supplied
    ).apply(to: primary.results)
    try require(searched.count == 1, "large review search did not find the final row")
    try require(
      searched[0].publicationNumber == "SYN-LARGE-0124",
      "large review search found wrong row"
    )

    let secondProfile = report.profileReports[1]
    let resolved = report.result(profileID: secondProfile.id, resultID: searched[0].id)
    try require(
      resolved?.publicationNumber == "SYN-LARGE-0124",
      "large stable lookup confused filtered index with source index"
    )
  }

  private static func checkTestStoreConfigurationFailsClosed() throws {
    try require(
      RevenueCatTestStoreConfiguration.status(in: [:]) == .missing,
      "missing Test Store key did not fail closed"
    )
    try require(
      RevenueCatTestStoreConfiguration.status(
        in: [RevenueCatTestStoreConfiguration.environmentName: ""]
      ) == .rejected,
      "empty Test Store key was accepted"
    )
    try require(
      RevenueCatTestStoreConfiguration.status(
        in: [RevenueCatTestStoreConfiguration.environmentName: "appl_public_fixture"]
      ) == .rejected,
      "non-Test Store key was accepted"
    )
    try require(
      RevenueCatTestStoreConfiguration.status(
        in: [RevenueCatTestStoreConfiguration.environmentName: "test_public_fixture"]
      ) == .accepted,
      "synthetic Test Store-shaped key was rejected"
    )
  }

  private static func checkPremiumAccessibilityOutcomes() throws {
    let offeringMarker = "TEST-OFFERING"
    let cases: [(PremiumAccessState, PremiumAccessRecoveryAction, PremiumAccessFocusTarget)] = [
      (.configurationMissing, .connectTestStore, .testStoreAPIKey),
      (.configurationRejected, .connectTestStore, .testStoreAPIKey),
      (.locked(price: nil), .restore, .restore),
      (.locked(price: offeringMarker), .purchase, .purchase),
      (.unlocked, .restore, .restore),
      (.cancelled(price: nil), .restore, .restore),
      (.cancelled(price: offeringMarker), .purchase, .purchase),
      (.failed, .retry, .retry),
    ]
    try require(
      PremiumAccessState.loading.terminalAccessibilityOutcome == nil,
      "loading state emitted a terminal accessibility outcome"
    )
    for (state, primaryAction, focusTarget) in cases {
      guard let outcome = state.terminalAccessibilityOutcome else {
        throw CheckFailure.failed("terminal RevenueCat state omitted accessibility outcome")
      }
      try require(!outcome.announcement.isEmpty, "accessibility announcement was empty")
      try require(
        outcome.primaryRecoveryAction == primaryAction,
        "accessibility primary recovery action changed"
      )
      try require(outcome.focusTarget == focusTarget, "accessibility recovery focus changed")
      try require(
        !outcome.announcement.contains("test_")
          && !outcome.announcement.contains("appl_")
          && !outcome.announcement.contains(offeringMarker),
        "accessibility announcement exposed configuration or package data"
      )
    }
  }

  private static func checkProcessAdapterPreservesDeterministicBytes() throws {
    let runner = try TenderVerdictProcess()
    guard let worktree = runner.worktree else {
      throw CheckFailure.failed("source adapter worktree was not discovered")
    }
    let workspace = worktree.appendingPathComponent(
      "examples/synthetic/portfolio-workspace.json"
    )
    let notices = worktree.appendingPathComponent("examples/synthetic/notices.json")
    let first = try runner.runPortfolioSynchronously(
      workspace: workspace,
      notices: notices,
      asOf: TenderVerdictProcess.syntheticAsOf
    )
    let second = try runner.runPortfolioSynchronously(
      workspace: workspace,
      notices: notices,
      asOf: TenderVerdictProcess.syntheticAsOf
    )

    try require(first.report == second.report, "selected-input reports were not deterministic")
    try require(first.jsonData == second.jsonData, "selected-input JSON bytes changed between runs")
    try require(
      first.report.summary.profileCount == 3,
      "selected workspace did not preserve profile count"
    )

    let normalizedFirst = try runner.normalizeWorkspaceSynchronously(workspace)
    let normalizedSecond = try runner.normalizeWorkspaceSynchronously(workspace)
    try require(
      normalizedFirst == normalizedSecond,
      "workspace normalization changed between source-adapter runs"
    )
    try require(
      normalizedFirst.document.profiles.map(\.name)
        == ["Example Austria Services", "Example Germany Support", "Example DACH Operations"],
      "workspace normalization changed profile order"
    )

    let preview = try runner.inspectNoticesSynchronously(notices, limit: 2)
    try require(preview.noticeCount == 3, "notice inspection changed the source count")
    try require(preview.preview.count == 2, "notice inspection ignored its bounded limit")
    try require(
      preview.preview[0].publicationNumber == "SYN-OPEN-001",
      "notice inspection changed input order"
    )
    try requireThrows("an invalid native preview limit was accepted") {
      _ = try runner.inspectNoticesSynchronously(notices, limit: 21)
    }
  }

  private static func require(_ condition: Bool, _ message: String) throws {
    guard condition else {
      throw CheckFailure.failed(message)
    }
  }

  private static func require<T: Equatable>(
    _ actual: T,
    equals expected: T,
    _ message: String
  ) throws {
    try require(actual == expected, message)
  }

  private static func requireThrows(
    _ message: String,
    operation: () throws -> Void
  ) throws {
    do {
      try operation()
    } catch {
      return
    }
    throw CheckFailure.failed(message)
  }

  private static func requireContractError(
    _ expected: PortfolioContractError,
    data: Data
  ) throws {
    do {
      _ = try PortfolioWorkspaceReport.decode(data)
    } catch let error as PortfolioContractError {
      try require(error == expected, "unexpected contract error: \(error)")
      return
    }
    throw CheckFailure.failed("invalid portfolio report was accepted")
  }

  private static func requireFirst<T>(_ values: [T], _ message: String) throws -> T {
    guard let value = values.first else {
      throw CheckFailure.failed(message)
    }
    return value
  }
}

private func makeNoticePreviewData(
  canonicalFields: [String] = NoticeImportPreview.expectedCanonicalFields,
  includeBothDeadlines: Bool = false,
  missingBuyerCount: Int = 1
) throws -> Data {
  let row: [String: Any] = [
    "publication_number": "SYN-FULL-001",
    "lot_id": "LOT-0001",
    "notice_type": "competition",
    "title": "Full notice",
    "buyer": "Example Buyer",
    "cpv_codes": ["72260000"],
    "countries": ["AUT"],
    "deadline": includeBothDeadlines ? "2026-09-15" : NSNull(),
    "deadline_at": "2026-09-15T12:00:00+02:00",
    "publication_date": "2026-08-01",
    "source_url": "https://procurement.example/full",
    "metadata_warnings": ["Public warning"],
  ]
  let payload: [String: Any] = [
    "schema_version": 1,
    "kind": "notice_import_preview",
    "source_kind": "local_json",
    "notice_count": 2,
    "canonical_fields": canonicalFields,
    "preview": [row],
    "missing_field_counts": [
      "notice_type": 1,
      "title": 0,
      "buyer": missingBuyerCount,
      "cpv_codes": 1,
      "countries": 1,
      "deadline": 1,
      "source_url": 1,
    ],
  ]
  return try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
}

private func makeLargeReportData(profileCount: Int, noticeCount: Int) throws -> Data {
  let sharedNoticeDigest = String(repeating: "a", count: 64)
  let verdicts = ["open_documents", "watch", "reject"]
  let reports: [[String: Any]] = (1...profileCount).map { profileIndex in
    var counts = ["open_documents": 0, "watch": 0, "reject": 0]
    let results: [[String: Any]] = (0..<noticeCount).map { noticeIndex in
      let verdict = verdicts[(noticeIndex + profileIndex - 1) % verdicts.count]
      counts[verdict, default: 0] += 1
      let hasDeadline = noticeIndex % 10 != 0
      return [
        "publication_number": String(format: "SYN-LARGE-%04d", noticeIndex),
        "lot_id": NSNull(),
        "title": "Synthetic service \(noticeIndex)",
        "buyer": String(format: "Example Buyer %02d", noticeIndex % 7),
        "deadline": hasDeadline ? "2026-09-15" : NSNull(),
        "deadline_at": NSNull(),
        "publication_date": "2026-08-01",
        "source_url": "https://procurement.example/large/\(noticeIndex)",
        "verdict": verdict,
        "reasons": ["Synthetic deterministic reason."],
        "unknowns": [],
        "human_next_step": "Review the supplied metadata.",
      ]
    }
    return [
      "schema_version": 3,
      "provenance": [
        "profile_sha256": String(repeating: String(profileIndex), count: 64),
        "notices_sha256": sharedNoticeDigest,
      ],
      "profile": [
        "schema_version": 1,
        "name": "Large Profile \(profileIndex)",
        "cpv_codes": ["72260000"],
        "countries": ["AUT"],
        "minimum_days_to_deadline": 14,
      ],
      "as_of": "2026-08-02",
      "summary": [
        "total": noticeCount,
        "open_documents": counts["open_documents", default: 0],
        "watch": counts["watch", default: 0],
        "reject": counts["reject", default: 0],
      ],
      "results": results,
    ]
  }
  let payload: [String: Any] = [
    "schema_version": 1,
    "kind": "portfolio_workspace_report",
    "as_of": "2026-08-02",
    "summary": [
      "profile_count": profileCount,
      "notice_count": noticeCount,
    ],
    "profile_reports": reports,
  ]
  return try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
}

private func makeReportData(
  profileCount: Int,
  declaredProfileCount: Int? = nil,
  secondNoticeDigest: String? = nil,
  invalidNestedTotal: Bool = false,
  reverseSecondResults: Bool = false,
  mismatchSecondSummary: Bool = false,
  noticeCount: Int = 3
) throws -> Data {
  let sharedNoticeDigest = String(repeating: "a", count: 64)
  let reports: [[String: Any]] = (1...profileCount).map { index in
    let noticeDigest = index == 2 ? secondNoticeDigest ?? sharedNoticeDigest : sharedNoticeDigest
    var results = noticeCount == 0 ? [] : makeResults()
    if index == 2 && reverseSecondResults {
      results.reverse()
    }
    if index == 2 && mismatchSecondSummary {
      results[0]["verdict"] = "reject"
    }
    let summary: [String: Any]
    if invalidNestedTotal {
      summary = ["total": 3, "open_documents": 1, "watch": 1, "reject": 2]
    } else if noticeCount == 0 {
      summary = ["total": 0, "open_documents": 0, "watch": 0, "reject": 0]
    } else {
      summary = ["total": 3, "open_documents": 1, "watch": 1, "reject": 1]
    }
    return [
      "schema_version": 3,
      "provenance": [
        "profile_sha256": String(repeating: String(index), count: 64),
        "notices_sha256": noticeDigest,
      ],
      "profile": [
        "schema_version": 1,
        "name": "Profile \(index)",
        "cpv_codes": ["72260000"],
        "countries": ["AUT"],
        "minimum_days_to_deadline": 14,
      ],
      "as_of": "2026-08-02",
      "summary": summary,
      "results": results,
    ]
  }
  let payload: [String: Any] = [
    "schema_version": 1,
    "kind": "portfolio_workspace_report",
    "as_of": "2026-08-02",
    "summary": [
      "profile_count": declaredProfileCount ?? profileCount,
      "notice_count": noticeCount,
    ],
    "profile_reports": reports,
  ]
  return try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
}

private func makeResults() -> [[String: Any]] {
  [
    [
      "publication_number": "SYN-OPEN-001",
      "lot_id": NSNull(),
      "title": "Application maintenance services",
      "buyer": "Example City Procurement Office",
      "deadline": "2026-09-15",
      "deadline_at": NSNull(),
      "publication_date": "2026-08-01",
      "source_url": "https://procurement.example/notices/SYN-OPEN-001",
      "verdict": "open_documents",
      "reasons": ["Exact CPV match.", "Country match."],
      "unknowns": [],
      "human_next_step": "Open and review the official procurement documents.",
    ],
    [
      "publication_number": "SYN-WATCH-001",
      "lot_id": NSNull(),
      "title": "Software support services",
      "buyer": "Example Regional Authority",
      "deadline": "2026-09-20",
      "deadline_at": NSNull(),
      "publication_date": "2026-07-30",
      "source_url": "https://procurement.example/notices/SYN-WATCH-001",
      "verdict": "watch",
      "reasons": ["Broader CPV class match."],
      "unknowns": ["Confirm the exact procurement scope."],
      "human_next_step": "Verify the flagged metadata.",
    ],
    [
      "publication_number": "SYN-REJECT-001",
      "lot_id": NSNull(),
      "title": "Software implementation services",
      "buyer": "Example Federal Agency",
      "deadline": NSNull(),
      "deadline_at": NSNull(),
      "publication_date": "2026-07-15",
      "source_url": "https://procurement.example/notices/SYN-REJECT-001",
      "verdict": "reject",
      "reasons": ["Deadline is below the configured minimum."],
      "unknowns": [],
      "human_next_step": "Stop review unless the metadata is corrected.",
    ],
  ]
}
