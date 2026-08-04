import Darwin
import Foundation

public enum TenderVerdictProcessError: Error, LocalizedError {
  case invalidRuntime
  case missingSyntheticFixture(String)
  case commandFailed(Int32, String)
  case timedOut
  case oversizedOutput

  public var errorDescription: String? {
    switch self {
    case .invalidRuntime:
      return
        "TenderVerdict runtime was not found. Build the app bundle or set TENDERVERDICT_WORKTREE."
    case .missingSyntheticFixture(let name):
      return "The bundled synthetic fixture is missing: \(name)."
    case .commandFailed(let status, let detail):
      let suffix = detail.isEmpty ? "" : " \(detail)"
      return "TenderVerdict portfolio exited with status \(status).\(suffix)"
    case .timedOut:
      return "TenderVerdict portfolio did not finish within 30 seconds."
    case .oversizedOutput:
      return "TenderVerdict returned an unexpectedly large portfolio report."
    }
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
    let output = try executePortfolio(workspace: workspace, notices: notices, asOf: asOf)
    return PortfolioExecution(
      report: try PortfolioWorkspaceReport.decode(output),
      jsonData: output
    )
  }

  private func executePortfolio(workspace: URL, notices: URL, asOf: String) throws -> Data {
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
    let arguments = [
      "portfolio",
      "--workspace",
      workspace.standardizedFileURL.path,
      "--notices",
      notices.standardizedFileURL.path,
      "--as-of",
      asOf,
    ]
    if let embeddedExecutable {
      process.executableURL = embeddedExecutable
      process.arguments = arguments
      process.currentDirectoryURL = embeddedExecutable.deletingLastPathComponent()
    } else if let worktree {
      process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
      process.arguments = ["python3", "-m", "tenderverdict"] + arguments
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
      if outputBytes > Self.maximumReportBytes || errorBytes > Self.maximumErrorBytes {
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
    guard process.terminationStatus == 0 else {
      let errorData = try Data(contentsOf: standardErrorURL)
      let detail = String(decoding: errorData.prefix(4_000), as: UTF8.self)
        .trimmingCharacters(in: .whitespacesAndNewlines)
      throw TenderVerdictProcessError.commandFailed(process.terminationStatus, detail)
    }
    guard try fileSize(at: standardOutputURL) <= Self.maximumReportBytes else {
      throw TenderVerdictProcessError.oversizedOutput
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
  }
}
