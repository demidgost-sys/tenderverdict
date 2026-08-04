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
    try checkPortfolioContractRejectsInconsistentProfileCount()
    try checkPortfolioContractRejectsDifferentNoticeDigests()
    try checkPortfolioContractRejectsInvalidNestedTotals()
    try checkTestStoreConfigurationFailsClosed()
    try checkProcessAdapterPreservesDeterministicBytes()
    print("NEXT_GEN_CHECKS_OK checks=6")
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

  private static func checkPortfolioContractRejectsDifferentNoticeDigests() throws {
    let data = try makeReportData(
      profileCount: 2,
      secondNoticeDigest: String(repeating: "b", count: 64)
    )
    try requireContractError(.inconsistentNoticeSet, data: data)
  }

  private static func checkPortfolioContractRejectsInvalidNestedTotals() throws {
    let data = try makeReportData(profileCount: 1, invalidNestedTotal: true)
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
}

private func makeReportData(
  profileCount: Int,
  declaredProfileCount: Int? = nil,
  secondNoticeDigest: String? = nil,
  invalidNestedTotal: Bool = false
) throws -> Data {
  let sharedNoticeDigest = String(repeating: "a", count: 64)
  let reports: [[String: Any]] = (1...profileCount).map { index in
    let noticeDigest = index == 2 ? secondNoticeDigest ?? sharedNoticeDigest : sharedNoticeDigest
    let summary: [String: Any] =
      invalidNestedTotal
      ? ["total": 3, "open_documents": 1, "watch": 1, "reject": 2]
      : ["total": 3, "open_documents": 1, "watch": 1, "reject": 1]
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
    ]
  }
  let payload: [String: Any] = [
    "schema_version": 1,
    "kind": "portfolio_workspace_report",
    "as_of": "2026-08-02",
    "summary": [
      "profile_count": declaredProfileCount ?? profileCount,
      "notice_count": 3,
    ],
    "profile_reports": reports,
  ]
  return try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
}
