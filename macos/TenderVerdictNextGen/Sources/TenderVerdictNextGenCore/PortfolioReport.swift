import Foundation

/// Mirrors Python's `normalize_display_text`: preserve evidence while making control and
/// bidirectional-formatting characters visible before rendering untrusted report text.
public func normalizedDisplayText(_ value: String) -> String {
  var rendered = ""
  rendered.reserveCapacity(value.utf8.count)

  for scalar in value.unicodeScalars {
    let codepoint = scalar.value
    if codepoint == 0x09 || codepoint == 0x0a || codepoint == 0x0d {
      rendered.append(" ")
    } else if codepoint < 0x20 || (0x7f...0x9f).contains(codepoint)
      || scalar.properties.generalCategory == .format
    {
      rendered +=
        codepoint <= 0xffff
        ? String(format: "\\u%04x", codepoint)
        : String(format: "\\U%08x", codepoint)
    } else {
      rendered.unicodeScalars.append(scalar)
    }
  }

  return rendered.split(whereSeparator: \.isWhitespace).joined(separator: " ")
}

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

      let normalizedName = normalizedIdentityText(report.profile.name)
      guard !normalizedName.isEmpty, normalizedNames.insert(normalizedName).inserted else {
        throw PortfolioContractError.duplicateProfileName
      }

      guard Self.isSHA256(report.provenance.profileSHA256),
        Self.isSHA256(report.provenance.noticesSHA256),
        report.provenance.generator.name == "TenderVerdict",
        !report.provenance.generator.version.isEmpty,
        !report.provenance.sourceKind.isEmpty,
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

public struct ProfileReport: Codable, Equatable, Identifiable, Sendable {
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
    var identities = Set<NoticeIdentity>()
    return results.allSatisfy { result in
      !result.publicationNumber.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        && !result.humanNextStep.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        && identities.insert(result.id).inserted
    }
  }

  public func deterministicJSONData() throws -> Data {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    let encoded = try encoder.encode(self)
    let json = String(decoding: encoded, as: UTF8.self)
    return Data((asciiSafeJSON(json) + "\n").utf8)
  }
}

public enum QualificationVerdict: String, Codable, Equatable, CaseIterable, Sendable {
  case openDocuments = "open_documents"
  case watch
  case reject
}

public struct QualificationResult: Codable, Equatable, Identifiable, Sendable {
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

  public var id: NoticeIdentity {
    normalizedNoticeIdentity(publicationNumber: publicationNumber, lotID: lotID)
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

  public func encode(to encoder: Encoder) throws {
    var values = encoder.container(keyedBy: CodingKeys.self)
    try values.encode(publicationNumber, forKey: .publicationNumber)
    try values.encode(lotID, forKey: .lotID)
    try values.encode(title, forKey: .title)
    try values.encode(buyer, forKey: .buyer)
    try values.encode(deadline, forKey: .deadline)
    try values.encode(deadlineAt, forKey: .deadlineAt)
    try values.encode(publicationDate, forKey: .publicationDate)
    try values.encode(sourceURL, forKey: .sourceURL)
    try values.encode(verdict, forKey: .verdict)
    try values.encode(reasons, forKey: .reasons)
    try values.encode(unknowns, forKey: .unknowns)
    try values.encode(humanNextStep, forKey: .humanNextStep)
  }

  public var safeSourceURL: URL? {
    guard let sourceURL,
      !sourceURL.unicodeScalars.contains(where: { scalar in
        CharacterSet.whitespacesAndNewlines.contains(scalar)
          || CharacterSet.controlCharacters.contains(scalar)
          || scalar.properties.generalCategory == .format
      }),
      let components = URLComponents(string: sourceURL),
      components.scheme?.lowercased() == "https",
      let host = components.host,
      !host.isEmpty,
      components.user == nil,
      components.password == nil,
      components.fragment == nil,
      let url = components.url
    else {
      return nil
    }
    return url
  }

  public var displayTitle: String {
    let value = normalizedDisplayText(title ?? "")
    return value.isEmpty ? "Untitled notice" : value
  }

  public var displayBuyer: String {
    let value = normalizedDisplayText(buyer ?? "")
    return value.isEmpty ? "Buyer not supplied" : value
  }

  public var displayDeadline: String {
    normalizedDisplayText(deadlineAt ?? deadline ?? "Deadline not supplied")
  }

  public var displayReference: String {
    let publication = normalizedDisplayText(publicationNumber)
    guard let lotID, !lotID.isEmpty else {
      return publication
    }
    return "\(publication) / \(normalizedDisplayText(lotID))"
  }

  public var displayHumanNextStep: String {
    normalizedDisplayText(humanNextStep)
  }

  public var displayReasons: [String] {
    reasons.map(normalizedDisplayText)
  }

  public var displayUnknowns: [String] {
    unknowns.map(normalizedDisplayText)
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
}

private struct NoticeSignature: Equatable {
  let identity: NoticeIdentity
  let title: String?
  let buyer: String?
  let deadline: String?
  let deadlineAt: String?
  let publicationDate: String?
  let sourceURL: String?
}

public struct ReportProvenance: Codable, Equatable, Sendable {
  public let generator: ReportGenerator
  public let sourceKind: String
  public let profileSHA256: String
  public let noticesSHA256: String
  public let tedQuery: String?
  public let retrievedAt: String?
  public let lotPolicy: String?

  enum CodingKeys: String, CodingKey {
    case generator
    case sourceKind = "source_kind"
    case profileSHA256 = "profile_sha256"
    case noticesSHA256 = "notices_sha256"
    case tedQuery = "ted_query"
    case retrievedAt = "retrieved_at"
    case lotPolicy = "lot_policy"
  }
}

public struct ReportGenerator: Codable, Equatable, Sendable {
  public let name: String
  public let version: String
}

public struct SupplierProfile: Codable, Equatable, Sendable {
  public static let maximumNameCharacters = 200
  public static let maximumCodes = 100
  public static let maximumCountries = 100
  public static let maximumMinimumDaysToDeadline = 3_650

  public let schemaVersion: Int
  public let name: String
  public let cpvCodes: [String]
  public let countries: [String]
  public let minimumDaysToDeadline: Int

  public var displayName: String { normalizedDisplayText(name) }

  public init(
    name: String,
    cpvCodes: [String],
    countries: [String],
    minimumDaysToDeadline: Int
  ) throws {
    try Self.validate(
      schemaVersion: 1,
      name: name,
      cpvCodes: cpvCodes,
      countries: countries,
      minimumDaysToDeadline: minimumDaysToDeadline
    )
    schemaVersion = 1
    self.name = name
    self.cpvCodes = cpvCodes
    self.countries = countries
    self.minimumDaysToDeadline = minimumDaysToDeadline
  }

  public init(from decoder: Decoder) throws {
    let values = try strictContainer(
      from: decoder,
      allowedKeys: [
        "schema_version", "name", "cpv_codes", "countries", "minimum_days_to_deadline",
      ],
      label: "profile"
    )
    let schemaVersion = try values.decode(Int.self, forKey: JSONKey("schema_version"))
    let name = try values.decode(String.self, forKey: JSONKey("name"))
    let cpvCodes = try values.decode([String].self, forKey: JSONKey("cpv_codes"))
    let countries = try values.decode([String].self, forKey: JSONKey("countries"))
    let minimumDaysToDeadline = try values.decode(
      Int.self,
      forKey: JSONKey("minimum_days_to_deadline")
    )
    try Self.validate(
      schemaVersion: schemaVersion,
      name: name,
      cpvCodes: cpvCodes,
      countries: countries,
      minimumDaysToDeadline: minimumDaysToDeadline
    )
    self.schemaVersion = schemaVersion
    self.name = name
    self.cpvCodes = cpvCodes
    self.countries = countries
    self.minimumDaysToDeadline = minimumDaysToDeadline
  }

  public func encode(to encoder: Encoder) throws {
    var values = encoder.container(keyedBy: JSONKey.self)
    try values.encode(schemaVersion, forKey: JSONKey("schema_version"))
    try values.encode(name, forKey: JSONKey("name"))
    try values.encode(cpvCodes, forKey: JSONKey("cpv_codes"))
    try values.encode(countries, forKey: JSONKey("countries"))
    try values.encode(minimumDaysToDeadline, forKey: JSONKey("minimum_days_to_deadline"))
  }

  private static func validate(
    schemaVersion: Int,
    name: String,
    cpvCodes: [String],
    countries: [String],
    minimumDaysToDeadline: Int
  ) throws {
    let trimmedName = name.trimmingCharacters(in: .whitespacesAndNewlines)
    guard schemaVersion == 1,
      name == trimmedName,
      !name.isEmpty,
      name.count <= maximumNameCharacters,
      (1...maximumCodes).contains(cpvCodes.count),
      (1...maximumCountries).contains(countries.count),
      (0...maximumMinimumDaysToDeadline).contains(minimumDaysToDeadline),
      Set(cpvCodes).count == cpvCodes.count,
      Set(countries).count == countries.count,
      cpvCodes.allSatisfy(Self.isNormalizedCPV),
      countries.allSatisfy(Self.isNormalizedCountry)
    else {
      throw WorkspaceDocumentError.invalidProfile
    }
  }

  private static func isNormalizedCPV(_ value: String) -> Bool {
    value.utf8.count == 8 && value.utf8.allSatisfy { (48...57).contains($0) }
  }

  private static func isNormalizedCountry(_ value: String) -> Bool {
    value.utf8.count == 3 && value.utf8.allSatisfy { (65...90).contains($0) }
  }
}

public struct ProfileReportSummary: Codable, Equatable, Sendable {
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

private func asciiSafeJSON(_ value: String) -> String {
  var result = ""
  result.reserveCapacity(value.utf8.count)
  for scalar in value.unicodeScalars {
    switch scalar.value {
    case 0...0x7e:
      result.unicodeScalars.append(scalar)
    case 0x7f...0xffff:
      result += String(format: "\\u%04x", scalar.value)
    default:
      let offset = scalar.value - 0x10000
      let high = 0xd800 + (offset >> 10)
      let low = 0xdc00 + (offset & 0x3ff)
      result += String(format: "\\u%04x\\u%04x", high, low)
    }
  }
  return result
}
