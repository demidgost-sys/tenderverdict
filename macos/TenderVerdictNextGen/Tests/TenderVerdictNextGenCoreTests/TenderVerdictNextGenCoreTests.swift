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
    try checkTestStoreConfigurationFailsClosed()
    try checkProcessAdapterPreservesDeterministicBytes()
    print("NEXT_GEN_CHECKS_OK checks=10")
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
      "deadline": "2026-08-05",
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
