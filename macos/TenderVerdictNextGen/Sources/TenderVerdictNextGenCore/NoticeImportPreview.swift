import Foundation

public enum NoticeImportPreviewError: Error, Equatable, LocalizedError {
  case oversized
  case invalidEnvelope
  case invalidCanonicalFields
  case invalidPreviewRecord
  case invalidMissingFieldCounts

  public var errorDescription: String? {
    switch self {
    case .oversized:
      return "TenderVerdict returned an unexpectedly large notice import preview."
    case .invalidEnvelope:
      return "TenderVerdict returned an invalid notice import preview."
    case .invalidCanonicalFields:
      return "The notice import preview does not use the canonical field contract."
    case .invalidPreviewRecord:
      return "A notice import preview row is invalid."
    case .invalidMissingFieldCounts:
      return "The notice import preview has inconsistent missing-field counts."
    }
  }
}

public struct NoticeImportPreview: Decodable, Equatable, Sendable {
  public static let maximumBytes = 4 * 1_024 * 1_024
  public static let expectedCanonicalFields = [
    "publication_number",
    "lot_id",
    "notice_type",
    "title",
    "buyer",
    "cpv_codes",
    "countries",
    "deadline",
    "deadline_at",
    "publication_date",
    "source_url",
    "metadata_warnings",
  ]
  public static let maximumNoticeCount = 1_000
  public static let maximumPreviewCount = 20

  public let schemaVersion: Int
  public let kind: String
  public let sourceKind: String
  public let noticeCount: Int
  public let canonicalFields: [String]
  public let preview: [NoticeImportRecord]
  public let missingFieldCounts: NoticeMissingFieldCounts

  public init(from decoder: Decoder) throws {
    let values = try strictContainer(
      from: decoder,
      allowedKeys: [
        "schema_version", "kind", "source_kind", "notice_count", "canonical_fields", "preview",
        "missing_field_counts",
      ],
      label: "notice import preview"
    )
    schemaVersion = try values.decode(Int.self, forKey: JSONKey("schema_version"))
    kind = try values.decode(String.self, forKey: JSONKey("kind"))
    sourceKind = try values.decode(String.self, forKey: JSONKey("source_kind"))
    noticeCount = try values.decode(Int.self, forKey: JSONKey("notice_count"))
    canonicalFields = try values.decode([String].self, forKey: JSONKey("canonical_fields"))
    preview = try values.decode([NoticeImportRecord].self, forKey: JSONKey("preview"))
    missingFieldCounts = try values.decode(
      NoticeMissingFieldCounts.self,
      forKey: JSONKey("missing_field_counts")
    )

    guard schemaVersion == 1,
      kind == "notice_import_preview",
      ["local_csv", "local_json", "ted_search_api"].contains(sourceKind),
      (0...Self.maximumNoticeCount).contains(noticeCount),
      preview.count <= min(Self.maximumPreviewCount, noticeCount),
      Set(preview.map(\.id)).count == preview.count
    else {
      throw NoticeImportPreviewError.invalidEnvelope
    }
    guard canonicalFields == Self.expectedCanonicalFields else {
      throw NoticeImportPreviewError.invalidCanonicalFields
    }
    guard missingFieldCounts.allValues.allSatisfy({ (0...noticeCount).contains($0) }) else {
      throw NoticeImportPreviewError.invalidMissingFieldCounts
    }
  }

  public static func decode(_ data: Data) throws -> Self {
    guard data.count <= maximumBytes else {
      throw NoticeImportPreviewError.oversized
    }
    return try JSONDecoder().decode(Self.self, from: data)
  }
}

public struct NoticeImportRecord: Decodable, Equatable, Identifiable, Sendable {
  public let publicationNumber: String
  public let lotID: String?
  public let noticeType: String?
  public let title: String?
  public let buyer: String?
  public let cpvCodes: [String]
  public let countries: [String]
  public let deadline: String?
  public let deadlineAt: String?
  public let publicationDate: String?
  public let sourceURL: String?
  public let metadataWarnings: [String]

  public var id: NoticeIdentity {
    normalizedNoticeIdentity(publicationNumber: publicationNumber, lotID: lotID)
  }

  public init(from decoder: Decoder) throws {
    let values = try strictContainer(
      from: decoder,
      allowedKeys: [
        "publication_number", "lot_id", "notice_type", "title", "buyer", "cpv_codes",
        "countries", "deadline", "deadline_at", "publication_date", "source_url",
        "metadata_warnings",
      ],
      label: "notice import preview row"
    )
    publicationNumber = try values.decode(String.self, forKey: JSONKey("publication_number"))
    lotID = try values.decodeIfPresent(String.self, forKey: JSONKey("lot_id"))
    noticeType = try values.decodeIfPresent(String.self, forKey: JSONKey("notice_type"))
    title = try values.decodeIfPresent(String.self, forKey: JSONKey("title"))
    buyer = try values.decodeIfPresent(String.self, forKey: JSONKey("buyer"))
    cpvCodes = try values.decode([String].self, forKey: JSONKey("cpv_codes"))
    countries = try values.decode([String].self, forKey: JSONKey("countries"))
    deadline = try values.decodeIfPresent(String.self, forKey: JSONKey("deadline"))
    deadlineAt = try values.decodeIfPresent(String.self, forKey: JSONKey("deadline_at"))
    publicationDate = try values.decodeIfPresent(String.self, forKey: JSONKey("publication_date"))
    sourceURL = try values.decodeIfPresent(String.self, forKey: JSONKey("source_url"))
    metadataWarnings = try values.decode(
      [String].self,
      forKey: JSONKey("metadata_warnings")
    )

    guard Self.isNormalizedRequired(publicationNumber, maximumCharacters: 200),
      Self.isNormalizedOptional(lotID, maximumCharacters: 24),
      Self.isNormalizedOptional(noticeType, maximumCharacters: 100),
      Self.isNormalizedOptional(title, maximumCharacters: 2_000),
      Self.isNormalizedOptional(buyer, maximumCharacters: 500),
      Self.isNormalizedOptional(sourceURL, maximumCharacters: 2_048),
      cpvCodes.count <= 100,
      countries.count <= 100,
      Set(cpvCodes).count == cpvCodes.count,
      Set(countries).count == countries.count,
      cpvCodes.allSatisfy(Self.isNormalizedCPV),
      countries.allSatisfy(Self.isNormalizedCountry),
      deadline == nil || deadlineAt == nil,
      Self.isNormalizedOptional(deadline, maximumCharacters: 10),
      Self.isNormalizedOptional(deadlineAt, maximumCharacters: 25),
      Self.isNormalizedOptional(publicationDate, maximumCharacters: 10),
      metadataWarnings.count <= 10,
      Set(metadataWarnings).count == metadataWarnings.count,
      metadataWarnings.allSatisfy({ Self.isNormalizedRequired($0, maximumCharacters: 500) })
    else {
      throw NoticeImportPreviewError.invalidPreviewRecord
    }
  }

  private static func isNormalizedRequired(_ value: String, maximumCharacters: Int) -> Bool {
    !value.isEmpty
      && value == value.trimmingCharacters(in: .whitespacesAndNewlines)
      && value.count <= maximumCharacters
  }

  private static func isNormalizedOptional(_ value: String?, maximumCharacters: Int) -> Bool {
    guard let value else {
      return true
    }
    return isNormalizedRequired(value, maximumCharacters: maximumCharacters)
  }

  private static func isNormalizedCPV(_ value: String) -> Bool {
    value.utf8.count == 8 && value.utf8.allSatisfy { (48...57).contains($0) }
  }

  private static func isNormalizedCountry(_ value: String) -> Bool {
    value.utf8.count == 3 && value.utf8.allSatisfy { (65...90).contains($0) }
  }
}

public struct NoticeMissingFieldCounts: Decodable, Equatable, Sendable {
  public let noticeType: Int
  public let title: Int
  public let buyer: Int
  public let cpvCodes: Int
  public let countries: Int
  public let deadline: Int
  public let sourceURL: Int

  var allValues: [Int] {
    [noticeType, title, buyer, cpvCodes, countries, deadline, sourceURL]
  }

  public init(from decoder: Decoder) throws {
    let values = try strictContainer(
      from: decoder,
      allowedKeys: [
        "notice_type", "title", "buyer", "cpv_codes", "countries", "deadline", "source_url",
      ],
      label: "notice import missing-field counts"
    )
    noticeType = try values.decode(Int.self, forKey: JSONKey("notice_type"))
    title = try values.decode(Int.self, forKey: JSONKey("title"))
    buyer = try values.decode(Int.self, forKey: JSONKey("buyer"))
    cpvCodes = try values.decode(Int.self, forKey: JSONKey("cpv_codes"))
    countries = try values.decode(Int.self, forKey: JSONKey("countries"))
    deadline = try values.decode(Int.self, forKey: JSONKey("deadline"))
    sourceURL = try values.decode(Int.self, forKey: JSONKey("source_url"))
  }
}

public struct NoticeIdentity: Hashable, Sendable {
  private let publicationNumber: String
  private let lotID: String

  public init(publicationNumber: String, lotID: String?) {
    self.publicationNumber = normalizedNoticeIdentityComponent(publicationNumber)
    self.lotID = normalizedNoticeIdentityComponent(lotID ?? "")
  }
}

func normalizedNoticeIdentity(publicationNumber: String, lotID: String?) -> NoticeIdentity {
  NoticeIdentity(publicationNumber: publicationNumber, lotID: lotID)
}

private func normalizedNoticeIdentityComponent(_ value: String) -> String {
  value.folding(
    options: [.caseInsensitive],
    locale: Locale(identifier: "en_US_POSIX")
  )
}
