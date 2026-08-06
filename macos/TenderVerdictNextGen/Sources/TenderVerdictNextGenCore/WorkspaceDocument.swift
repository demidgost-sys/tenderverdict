import Foundation

public enum WorkspaceDocumentError: Error, Equatable, LocalizedError {
  case oversized
  case invalidEnvelope
  case invalidProfile
  case duplicateProfileName

  public var errorDescription: String? {
    switch self {
    case .oversized:
      return "Choose a workspace file no larger than 256 KiB."
    case .invalidEnvelope:
      return "The file is not a supported TenderVerdict workspace document."
    case .invalidProfile:
      return "A workspace profile does not match the schema-1 contract."
    case .duplicateProfileName:
      return "Workspace profile names must be unique."
    }
  }
}

public struct PortfolioWorkspaceDocument: Codable, Equatable, Sendable {
  public static let maximumBytes = 256 * 1_024
  public static let maximumProfiles = 5

  public let schemaVersion: Int
  public let profiles: [SupplierProfile]

  public init(profiles: [SupplierProfile]) throws {
    try Self.validate(schemaVersion: 1, profiles: profiles)
    schemaVersion = 1
    self.profiles = profiles
  }

  public init(from decoder: Decoder) throws {
    let values = try strictContainer(
      from: decoder,
      allowedKeys: ["schema_version", "profiles"],
      label: "workspace"
    )
    let schemaVersion = try values.decode(Int.self, forKey: JSONKey("schema_version"))
    let profiles = try values.decode([SupplierProfile].self, forKey: JSONKey("profiles"))
    try Self.validate(schemaVersion: schemaVersion, profiles: profiles)
    self.schemaVersion = schemaVersion
    self.profiles = profiles
  }

  public func encode(to encoder: Encoder) throws {
    var values = encoder.container(keyedBy: JSONKey.self)
    try values.encode(schemaVersion, forKey: JSONKey("schema_version"))
    try values.encode(profiles, forKey: JSONKey("profiles"))
  }

  public static func decode(_ data: Data) throws -> Self {
    guard data.count <= maximumBytes else {
      throw WorkspaceDocumentError.oversized
    }
    return try JSONDecoder().decode(Self.self, from: data)
  }

  public func normalizedJSONData() throws -> Data {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    var data = try encoder.encode(self)
    data.append(0x0a)
    guard data.count <= Self.maximumBytes else {
      throw WorkspaceDocumentError.oversized
    }
    return data
  }

  private static func validate(schemaVersion: Int, profiles: [SupplierProfile]) throws {
    guard schemaVersion == 1, (1...maximumProfiles).contains(profiles.count) else {
      throw WorkspaceDocumentError.invalidEnvelope
    }
    var normalizedNames = Set<String>()
    for profile in profiles {
      let normalizedName = normalizedIdentityText(profile.name)
      guard !normalizedName.isEmpty, normalizedNames.insert(normalizedName).inserted else {
        throw WorkspaceDocumentError.duplicateProfileName
      }
    }
  }
}

public struct WorkspaceNormalization: Equatable, Sendable {
  public let document: PortfolioWorkspaceDocument
  public let jsonData: Data

  public init(document: PortfolioWorkspaceDocument, jsonData: Data) {
    self.document = document
    self.jsonData = jsonData
  }
}

struct JSONKey: CodingKey, Hashable {
  let stringValue: String
  let intValue: Int?

  init(_ stringValue: String) {
    self.stringValue = stringValue
    intValue = nil
  }

  init?(stringValue: String) {
    self.init(stringValue)
  }

  init?(intValue: Int) {
    stringValue = String(intValue)
    self.intValue = intValue
  }
}

func strictContainer(
  from decoder: Decoder,
  allowedKeys: Set<String>,
  label: String
) throws -> KeyedDecodingContainer<JSONKey> {
  let values = try decoder.container(keyedBy: JSONKey.self)
  if let unknown = values.allKeys.map(\.stringValue).filter({ !allowedKeys.contains($0) }).sorted()
    .first
  {
    throw DecodingError.dataCorrupted(
      .init(
        codingPath: decoder.codingPath, debugDescription: "\(label) has unknown field: \(unknown)")
    )
  }
  return values
}

func normalizedSearchText(_ value: String) -> String {
  normalizedIdentityText(value).folding(
    options: [.diacriticInsensitive],
    locale: Locale(identifier: "en_US_POSIX")
  )
}

func normalizedIdentityText(_ value: String) -> String {
  value.trimmingCharacters(in: .whitespacesAndNewlines).folding(
    options: [.caseInsensitive, .widthInsensitive],
    locale: Locale(identifier: "en_US_POSIX")
  )
}
