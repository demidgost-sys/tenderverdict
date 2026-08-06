import Darwin
import Foundation

public enum TenderVerdictProcessError: Error, LocalizedError {
  case invalidRuntime
  case missingSyntheticFixture(String)
  case commandFailed(Int32, String)
  case timedOut
  case oversizedOutput
  case invalidPreviewLimit

  public var errorDescription: String? {
    switch self {
    case .invalidRuntime:
      return
        "TenderVerdict runtime was not found. Build the app bundle or set TENDERVERDICT_WORKTREE."
    case .missingSyntheticFixture(let name):
      return "The bundled synthetic fixture is missing: \(name)."
    case .commandFailed(let status, let detail):
      let suffix = detail.isEmpty ? "" : " \(detail)"
      return "TenderVerdict core command exited with status \(status).\(suffix)"
    case .timedOut:
      return "TenderVerdict core command did not finish within 30 seconds."
    case .oversizedOutput:
      return "TenderVerdict returned an unexpectedly large response."
    case .invalidPreviewLimit:
      return "The notice preview limit must be between 1 and 20."
    }
  }
}

/// Keeps the native review-point affordance aligned with Python's strict date contract.
public enum ReviewPointInputValidator {
  public static let guidance =
    "Enter a review point as YYYY-MM-DD or RFC 3339, for example "
    + "2026-08-02 or 2026-08-02T12:30:00Z."

  public static func validationMessage(for rawValue: String) -> String? {
    let value = rawValue.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !value.isEmpty else {
      return guidance
    }
    if hasDateShape(value), isValidCalendarDate(value) {
      return nil
    }
    if hasRFC3339Shape(value), isValidRFC3339(value) {
      return nil
    }
    return guidance
  }

  public static func todayString(
    referenceDate: Date = Date(),
    timeZone: TimeZone = .current
  ) -> String {
    var calendar = Calendar(identifier: .gregorian)
    calendar.timeZone = timeZone
    let components = calendar.dateComponents([.year, .month, .day], from: referenceDate)
    return String(
      format: "%04d-%02d-%02d",
      components.year ?? 0,
      components.month ?? 0,
      components.day ?? 0
    )
  }

  private static func hasDateShape(_ value: String) -> Bool {
    let bytes = Array(value.utf8)
    guard bytes.count == 10, bytes[4] == 45, bytes[7] == 45 else { return false }
    return bytes.enumerated().allSatisfy { index, byte in
      index == 4 || index == 7 || (48...57).contains(byte)
    }
  }

  private static func isValidCalendarDate(_ value: String) -> Bool {
    let parts = value.split(separator: "-", omittingEmptySubsequences: false)
    guard parts.count == 3,
      let year = Int(parts[0]),
      let month = Int(parts[1]),
      let day = Int(parts[2])
    else {
      return false
    }
    var calendar = Calendar(identifier: .gregorian)
    calendar.timeZone = TimeZone(secondsFromGMT: 0)!
    guard let date = calendar.date(from: DateComponents(year: year, month: month, day: day))
    else {
      return false
    }
    let checked = calendar.dateComponents([.year, .month, .day], from: date)
    return checked.year == year && checked.month == month && checked.day == day
  }

  private static func hasRFC3339Shape(_ value: String) -> Bool {
    let bytes = Array(value.utf8)
    guard bytes.count == 20 || bytes.count == 25 else { return false }
    let fixedSeparators: [Int: UInt8] = [4: 45, 7: 45, 10: 84, 13: 58, 16: 58]
    for (index, expected) in fixedSeparators where bytes[index] != expected {
      return false
    }
    let digitPositions = [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18]
    guard digitPositions.allSatisfy({ (48...57).contains(bytes[$0]) }) else {
      return false
    }
    if bytes.count == 20 {
      return bytes[19] == 90
    }
    guard bytes[19] == 43 || bytes[19] == 45, bytes[22] == 58 else { return false }
    return [20, 21, 23, 24].allSatisfy { (48...57).contains(bytes[$0]) }
  }

  private static func isValidRFC3339(_ value: String) -> Bool {
    let bytes = Array(value.utf8)
    guard isValidCalendarDate(String(value.prefix(10))),
      let hour = twoDigitInt(bytes, at: 11),
      let minute = twoDigitInt(bytes, at: 14),
      let second = twoDigitInt(bytes, at: 17),
      (0..<24).contains(hour),
      (0..<60).contains(minute),
      (0..<60).contains(second)
    else {
      return false
    }
    guard bytes.count == 25 else { return true }
    guard let offsetHour = twoDigitInt(bytes, at: 20),
      let offsetMinute = twoDigitInt(bytes, at: 23)
    else {
      return false
    }
    return (0..<24).contains(offsetHour) && (0..<60).contains(offsetMinute)
  }

  private static func twoDigitInt(_ bytes: [UInt8], at index: Int) -> Int? {
    guard bytes.indices.contains(index + 1),
      (48...57).contains(bytes[index]),
      (48...57).contains(bytes[index + 1])
    else {
      return nil
    }
    return Int(bytes[index] - 48) * 10 + Int(bytes[index + 1] - 48)
  }
}

public struct PortfolioExecution: Sendable {
  public let report: PortfolioWorkspaceReport
  public let jsonData: Data

  public init(report: PortfolioWorkspaceReport, jsonData: Data) {
    self.report = report
    self.jsonData = jsonData
  }
}

public struct TenderVerdictProcess: Sendable {
  public static let worktreeEnvironmentName = "TENDERVERDICT_WORKTREE"
  public static let syntheticAsOf = "2026-08-02"

  private static let maximumReportBytes = 64 * 1_024 * 1_024
  private static let maximumPreviewBytes = 4 * 1_024 * 1_024
  private static let maximumErrorBytes = 64 * 1_024
  private static let timeout: TimeInterval = 30

  private let embeddedExecutable: URL?
  private let bundledExamples: URL?
  public let worktree: URL?

  public init(
    environment: [String: String] = ProcessInfo.processInfo.environment,
    currentDirectory: URL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath),
    bundle: Bundle = .main
  ) throws {
    let configuredPath = environment[Self.worktreeEnvironmentName]?
      .trimmingCharacters(in: .whitespacesAndNewlines)
    let configuredWorktree = configuredPath.flatMap { path in
      path.isEmpty ? nil : URL(fileURLWithPath: path)
    }
    let worktreeCandidate = configuredWorktree ?? currentDirectory
    let normalizedWorktree = worktreeCandidate.standardizedFileURL
    if Self.isWorktree(normalizedWorktree) {
      worktree = normalizedWorktree
    } else {
      worktree = nil
    }

    if let resourceURL = bundle.resourceURL {
      let executable =
        resourceURL
        .appendingPathComponent("TenderVerdictCore", isDirectory: true)
        .appendingPathComponent("TenderVerdictCore", isDirectory: false)
      embeddedExecutable =
        FileManager.default.isExecutableFile(atPath: executable.path)
        ? executable
        : nil

      let examples = resourceURL.appendingPathComponent("Examples", isDirectory: true)
      bundledExamples =
        FileManager.default.fileExists(atPath: examples.path)
        ? examples
        : nil
    } else {
      embeddedExecutable = nil
      bundledExamples = nil
    }

    guard embeddedExecutable != nil || worktree != nil else {
      throw TenderVerdictProcessError.invalidRuntime
    }
  }

  public func loadSyntheticPortfolio() async throws -> PortfolioExecution {
    try await Task.detached(priority: .userInitiated) {
      try loadSyntheticPortfolioSynchronously()
    }.value
  }

  public func loadSyntheticPortfolioSynchronously() throws -> PortfolioExecution {
    let examples =
      bundledExamples
      ?? worktree?.appendingPathComponent("examples/synthetic", isDirectory: true)
    guard let examples else {
      throw TenderVerdictProcessError.missingSyntheticFixture("portfolio-workspace.json")
    }
    let workspace = examples.appendingPathComponent("portfolio-workspace.json")
    let notices = examples.appendingPathComponent("notices.json")
    try requireFixture(workspace)
    try requireFixture(notices)
    return try runPortfolioSynchronously(
      workspace: workspace,
      notices: notices,
      asOf: Self.syntheticAsOf
    )
  }

  public func runPortfolio(
    workspace: URL,
    notices: URL,
    asOf: String
  ) async throws -> PortfolioExecution {
    try await Task.detached(priority: .userInitiated) {
      try runPortfolioSynchronously(workspace: workspace, notices: notices, asOf: asOf)
    }.value
  }

  public func runPortfolioSynchronously(
    workspace: URL,
    notices: URL,
    asOf: String
  ) throws -> PortfolioExecution {
    let output = try execute(
      arguments: [
        "portfolio",
        "--workspace",
        workspace.standardizedFileURL.path,
        "--notices",
        notices.standardizedFileURL.path,
        "--as-of",
        asOf,
      ],
      maximumOutputBytes: Self.maximumReportBytes
    )
    return PortfolioExecution(
      report: try PortfolioWorkspaceReport.decode(output),
      jsonData: output
    )
  }

  public func normalizeWorkspace(_ workspace: URL) async throws -> WorkspaceNormalization {
    try await Task.detached(priority: .userInitiated) {
      try normalizeWorkspaceSynchronously(workspace)
    }.value
  }

  public func normalizeWorkspaceSynchronously(_ workspace: URL) throws -> WorkspaceNormalization {
    let output = try execute(
      arguments: [
        "normalize-workspace",
        "--workspace",
        workspace.standardizedFileURL.path,
      ],
      maximumOutputBytes: PortfolioWorkspaceDocument.maximumBytes
    )
    return WorkspaceNormalization(
      document: try PortfolioWorkspaceDocument.decode(output),
      jsonData: output
    )
  }

  public func inspectNotices(_ notices: URL, limit: Int = 5) async throws
    -> NoticeImportPreview
  {
    try await Task.detached(priority: .userInitiated) {
      try inspectNoticesSynchronously(notices, limit: limit)
    }.value
  }

  public func inspectNoticesSynchronously(_ notices: URL, limit: Int = 5) throws
    -> NoticeImportPreview
  {
    guard (1...NoticeImportPreview.maximumPreviewCount).contains(limit) else {
      throw TenderVerdictProcessError.invalidPreviewLimit
    }
    let output = try execute(
      arguments: [
        "inspect-notices",
        "--notices",
        notices.standardizedFileURL.path,
        "--limit",
        String(limit),
      ],
      maximumOutputBytes: Self.maximumPreviewBytes
    )
    return try NoticeImportPreview.decode(output)
  }

  private func execute(arguments: [String], maximumOutputBytes: Int) throws -> Data {
    let fileManager = FileManager.default
    let temporaryDirectory = fileManager.temporaryDirectory
      .appendingPathComponent("TenderVerdictNextGen-\(UUID().uuidString)", isDirectory: true)
    try fileManager.createDirectory(
      at: temporaryDirectory,
      withIntermediateDirectories: false
    )
    defer { try? fileManager.removeItem(at: temporaryDirectory) }

    let standardOutputURL = temporaryDirectory.appendingPathComponent("stdout.json")
    let standardErrorURL = temporaryDirectory.appendingPathComponent("stderr.txt")
    guard fileManager.createFile(atPath: standardOutputURL.path, contents: nil),
      fileManager.createFile(atPath: standardErrorURL.path, contents: nil)
    else {
      throw CocoaError(.fileWriteUnknown)
    }

    let standardOutput = try FileHandle(forWritingTo: standardOutputURL)
    let standardError = try FileHandle(forWritingTo: standardErrorURL)
    defer {
      try? standardOutput.close()
      try? standardError.close()
    }

    let process = Process()
    if let embeddedExecutable {
      process.executableURL = embeddedExecutable
      process.arguments = arguments
      process.currentDirectoryURL = embeddedExecutable.deletingLastPathComponent()
    } else if let worktree {
      let launcher = worktree.appendingPathComponent("tools/next_gen_core_launcher.py")
      process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
      process.arguments = ["python3", launcher.path] + arguments
      process.currentDirectoryURL = worktree
    } else {
      throw TenderVerdictProcessError.invalidRuntime
    }
    process.environment = childEnvironment()
    process.standardOutput = standardOutput
    process.standardError = standardError

    try process.run()
    let deadline = Date().addingTimeInterval(Self.timeout)
    while process.isRunning && Date() < deadline {
      let outputBytes = try fileSize(at: standardOutputURL)
      let errorBytes = try fileSize(at: standardErrorURL)
      if outputBytes > maximumOutputBytes || errorBytes > Self.maximumErrorBytes {
        terminate(process)
        throw TenderVerdictProcessError.oversizedOutput
      }
      Thread.sleep(forTimeInterval: 0.02)
    }
    if process.isRunning {
      terminate(process)
      throw TenderVerdictProcessError.timedOut
    }

    try standardOutput.synchronize()
    try standardError.synchronize()
    let finalOutputBytes = try fileSize(at: standardOutputURL)
    let finalErrorBytes = try fileSize(at: standardErrorURL)
    guard finalOutputBytes <= maximumOutputBytes,
      finalErrorBytes <= Self.maximumErrorBytes
    else {
      throw TenderVerdictProcessError.oversizedOutput
    }
    guard process.terminationStatus == 0 else {
      let errorData = try Data(contentsOf: standardErrorURL)
      let detail = String(decoding: errorData.prefix(4_000), as: UTF8.self)
        .trimmingCharacters(in: .whitespacesAndNewlines)
      throw TenderVerdictProcessError.commandFailed(process.terminationStatus, detail)
    }
    return try Data(contentsOf: standardOutputURL, options: [.mappedIfSafe])
  }

  private func terminate(_ process: Process) {
    process.terminate()
    let gracefulDeadline = Date().addingTimeInterval(1)
    while process.isRunning && Date() < gracefulDeadline {
      Thread.sleep(forTimeInterval: 0.02)
    }
    if process.isRunning {
      Darwin.kill(process.processIdentifier, SIGKILL)
      process.waitUntilExit()
    }
  }

  private func requireFixture(_ url: URL) throws {
    guard FileManager.default.fileExists(atPath: url.path) else {
      throw TenderVerdictProcessError.missingSyntheticFixture(url.lastPathComponent)
    }
  }

  private func fileSize(at url: URL) throws -> Int {
    let attributes = try FileManager.default.attributesOfItem(atPath: url.path)
    return (attributes[.size] as? NSNumber)?.intValue ?? 0
  }

  private func childEnvironment() -> [String: String] {
    let parent = ProcessInfo.processInfo.environment
    var environment = [
      "PATH": parent["PATH"] ?? "/usr/bin:/bin",
      "PYTHONDONTWRITEBYTECODE": "1",
    ]
    if let worktree, embeddedExecutable == nil {
      environment["PYTHONPATH"] = worktree.appendingPathComponent("src").path
    }
    for name in ["LANG", "LC_ALL"] {
      if let value = parent[name] {
        environment[name] = value
      }
    }
    return environment
  }

  private static func isWorktree(_ url: URL) -> Bool {
    FileManager.default.fileExists(atPath: url.appendingPathComponent("pyproject.toml").path)
      && FileManager.default.fileExists(
        atPath: url.appendingPathComponent("src/tenderverdict").path
      )
      && FileManager.default.fileExists(
        atPath: url.appendingPathComponent("tools/next_gen_core_launcher.py").path
      )
  }
}
