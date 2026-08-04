import Foundation

public enum PortfolioContractError: Error, Equatable, LocalizedError {
  case invalidWorkspaceEnvelope
  case invalidProfileReport
  case inconsistentProfileCount
  case inconsistentNoticeSet
  case duplicateProfileName
  case invalidProvenance

  public var errorDescription: String? {
    switch self {
    case .invalidWorkspaceEnvelope:
      return "The file is not a supported TenderVerdict portfolio report."
    case .invalidProfileReport:
      return "A nested profile report does not match the schema-3 contract."
    case .inconsistentProfileCount:
      return "The portfolio profile count is inconsistent."
    case .inconsistentNoticeSet:
      return "Portfolio profiles were not evaluated against one shared notice set."
    case .duplicateProfileName:
      return "Portfolio profile names must be unique."
    case .invalidProvenance:
      return "Portfolio provenance digests are invalid or inconsistent."
    }
  }
}

public struct PortfolioWorkspaceReport: Decodable, Equatable, Sendable {
  public let schemaVersion: Int
  public let kind: String
  public let asOf: String
  public let summary: PortfolioWorkspaceSummary
  public let profileReports: [ProfileReport]

  enum CodingKeys: String, CodingKey {
    case schemaVersion = "schema_version"
    case kind
    case asOf = "as_of"
    case summary
    case profileReports = "profile_reports"
  }

  public init(from decoder: Decoder) throws {
    let values = try decoder.container(keyedBy: CodingKeys.self)
    schemaVersion = try values.decode(Int.self, forKey: .schemaVersion)
    kind = try values.decode(String.self, forKey: .kind)
    asOf = try values.decode(String.self, forKey: .asOf)
    summary = try values.decode(PortfolioWorkspaceSummary.self, forKey: .summary)
    profileReports = try values.decode([ProfileReport].self, forKey: .profileReports)

    guard schemaVersion == 1,
      kind == "portfolio_workspace_report",
      !asOf.isEmpty,
      (1...5).contains(profileReports.count),
      summary.noticeCount >= 0
    else {
      throw PortfolioContractError.invalidWorkspaceEnvelope
    }
    guard summary.profileCount == profileReports.count else {
      throw PortfolioContractError.inconsistentProfileCount
    }

    var normalizedNames = Set<String>()
    var profileDigests = Set<String>()
    var noticeDigest: String?
    var noticeSignatures: [NoticeSignature]?
    for report in profileReports {
      guard report.schemaVersion == 3,
        report.profile.schemaVersion == 1,
        report.asOf == asOf,
        report.summary.total == summary.noticeCount,
        report.summary.isInternallyConsistent,
        report.results.count == report.summary.total,
        report.resultsMatchSummary,
        report.hasUniqueResults
      else {
        throw PortfolioContractError.invalidProfileReport
      }

      let normalizedName = report.profile.name
        .trimmingCharacters(in: .whitespacesAndNewlines)
        .lowercased()
      guard !normalizedName.isEmpty, normalizedNames.insert(normalizedName).inserted else {
        throw PortfolioContractError.duplicateProfileName
      }

      guard Self.isSHA256(report.provenance.profileSHA256),
        Self.isSHA256(report.provenance.noticesSHA256),
        profileDigests.insert(report.provenance.profileSHA256).inserted
      else {
        throw PortfolioContractError.invalidProvenance
      }
      if let noticeDigest, noticeDigest != report.provenance.noticesSHA256 {
        throw PortfolioContractError.inconsistentNoticeSet
      }
      noticeDigest = report.provenance.noticesSHA256

      let reportSignatures = report.results.map(\.noticeSignature)
      if let noticeSignatures, noticeSignatures != reportSignatures {
        throw PortfolioContractError.inconsistentNoticeSet
      }
      noticeSignatures = reportSignatures
    }
  }

  public static func decode(_ data: Data) throws -> Self {
    try JSONDecoder().decode(Self.self, from: data)
  }

  public func visibleProfileReports(premiumUnlocked: Bool) -> [ProfileReport] {
    premiumUnlocked ? profileReports : Array(profileReports.prefix(1))
  }

  private static func isSHA256(_ value: String) -> Bool {
    value.utf8.count == 64
      && value.utf8.allSatisfy { byte in
        (48...57).contains(byte) || (97...102).contains(byte)
      }
  }
}

public struct PortfolioWorkspaceSummary: Decodable, Equatable, Sendable {
  public let profileCount: Int
  public let noticeCount: Int

  enum CodingKeys: String, CodingKey {
    case profileCount = "profile_count"
    case noticeCount = "notice_count"
  }
}

public struct ProfileReport: Decodable, Equatable, Identifiable, Sendable {
  public let schemaVersion: Int
  public let provenance: ReportProvenance
  public let profile: SupplierProfile
  public let asOf: String
  public let summary: ProfileReportSummary
  public let results: [QualificationResult]

  public var id: String { provenance.profileSHA256 }

  enum CodingKeys: String, CodingKey {
    case schemaVersion = "schema_version"
    case provenance
    case profile
    case asOf = "as_of"
    case summary
    case results
  }

  var resultsMatchSummary: Bool {
    let counts = results.reduce(into: (open: 0, watch: 0, reject: 0)) { partial, result in
      switch result.verdict {
      case .openDocuments:
        partial.open += 1
      case .watch:
        partial.watch += 1
      case .reject:
        partial.reject += 1
      }
    }
    return counts.open == summary.openDocuments
      && counts.watch == summary.watch
      && counts.reject == summary.reject
  }

  var hasUniqueResults: Bool {
    var identities = Set<String>()
    return results.allSatisfy { result in
      !result.publicationNumber.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        && !result.humanNextStep.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        && identities.insert(result.id).inserted
    }
  }
}

public enum QualificationVerdict: String, Decodable, Equatable, CaseIterable, Sendable {
  case openDocuments = "open_documents"
  case watch
  case reject
}

public struct QualificationResult: Decodable, Equatable, Identifiable, Sendable {
  public let publicationNumber: String
  public let lotID: String?
  public let title: String?
  public let buyer: String?
  public let deadline: String?
  public let deadlineAt: String?
  public let publicationDate: String?
  public let sourceURL: String?
  public let verdict: QualificationVerdict
  public let reasons: [String]
  public let unknowns: [String]
  public let humanNextStep: String

  public var id: String {
    Self.normalizedIdentity(publicationNumber: publicationNumber, lotID: lotID)
  }

  enum CodingKeys: String, CodingKey {
    case publicationNumber = "publication_number"
    case lotID = "lot_id"
    case title
    case buyer
    case deadline
    case deadlineAt = "deadline_at"
    case publicationDate = "publication_date"
    case sourceURL = "source_url"
    case verdict
    case reasons
    case unknowns
    case humanNextStep = "human_next_step"
  }

  fileprivate var noticeSignature: NoticeSignature {
    NoticeSignature(
      identity: id,
      title: title,
      buyer: buyer,
      deadline: deadline,
      deadlineAt: deadlineAt,
      publicationDate: publicationDate,
      sourceURL: sourceURL
    )
  }

  private static func normalizedIdentity(publicationNumber: String, lotID: String?) -> String {
    let publication = publicationNumber
      .trimmingCharacters(in: .whitespacesAndNewlines)
      .lowercased()
    let lot = lotID?
      .trimmingCharacters(in: .whitespacesAndNewlines)
      .lowercased() ?? ""
    return "\(publication)\u{1f}\(lot)"
  }
}

private struct NoticeSignature: Equatable {
  let identity: String
  let title: String?
  let buyer: String?
  let deadline: String?
  let deadlineAt: String?
  let publicationDate: String?
  let sourceURL: String?
}

public struct ReportProvenance: Decodable, Equatable, Sendable {
  public let profileSHA256: String
  public let noticesSHA256: String

  enum CodingKeys: String, CodingKey {
    case profileSHA256 = "profile_sha256"
    case noticesSHA256 = "notices_sha256"
  }
}

public struct SupplierProfile: Decodable, Equatable, Sendable {
  public let schemaVersion: Int
  public let name: String

  enum CodingKeys: String, CodingKey {
    case schemaVersion = "schema_version"
    case name
  }
}

public struct ProfileReportSummary: Decodable, Equatable, Sendable {
  public let total: Int
  public let openDocuments: Int
  public let watch: Int
  public let reject: Int

  enum CodingKeys: String, CodingKey {
    case total
    case openDocuments = "open_documents"
    case watch
    case reject
  }

  var isInternallyConsistent: Bool {
    guard total >= 0,
      openDocuments >= 0,
      watch >= 0,
      reject >= 0,
      openDocuments <= total,
      watch <= total - openDocuments
    else {
      return false
    }
    return reject == total - openDocuments - watch
  }
}
