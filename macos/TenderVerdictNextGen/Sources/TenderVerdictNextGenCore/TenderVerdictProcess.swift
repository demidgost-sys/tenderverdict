import Foundation

public enum TenderVerdictProcessError: Error, LocalizedError {
  case invalidWorktree
  case missingSyntheticFixture(String)
  case commandFailed(Int32, String)
  case oversizedOutput

  public var errorDescription: String? {
    switch self {
    case .invalidWorktree:
      return "TenderVerdict source root was not found. Set TENDERVERDICT_WORKTREE."
    case .missingSyntheticFixture(let name):
      return "The bundled synthetic fixture is missing: \(name)."
    case .commandFailed(let status, let detail):
      let suffix = detail.isEmpty ? "" : " \(detail)"
      return "TenderVerdict portfolio exited with status \(status).\(suffix)"
    case .oversizedOutput:
      return "TenderVerdict returned an unexpectedly large synthetic report."
    }
  }
}

public struct TenderVerdictProcess: Sendable {
  public static let worktreeEnvironmentName = "TENDERVERDICT_WORKTREE"
  public static let syntheticAsOf = "2026-08-02"
  private static let maximumSyntheticReportBytes = 1_048_576

  public let worktree: URL

  public init(
    environment: [String: String] = ProcessInfo.processInfo.environment,
    currentDirectory: URL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
  ) throws {
    let configuredPath = environment[Self.worktreeEnvironmentName]?
      .trimmingCharacters(in: .whitespacesAndNewlines)
    let candidate =
      configuredPath.flatMap { path in path.isEmpty ? nil : URL(fileURLWithPath: path) }
      ?? currentDirectory
    let normalized = candidate.standardizedFileURL
    guard
      FileManager.default.fileExists(
        atPath: normalized.appendingPathComponent("pyproject.toml").path
      ),
      FileManager.default.fileExists(
        atPath: normalized.appendingPathComponent("src/tenderverdict").path
      )
    else {
      throw TenderVerdictProcessError.invalidWorktree
    }
    worktree = normalized
  }

  public func loadSyntheticPortfolio() async throws -> PortfolioWorkspaceReport {
    try await Task.detached(priority: .userInitiated) {
      try loadSyntheticPortfolioSynchronously()
    }.value
  }

  public func loadSyntheticPortfolioSynchronously() throws -> PortfolioWorkspaceReport {
    let workspace = worktree.appendingPathComponent(
      "examples/synthetic/portfolio-workspace.json"
    )
    let notices = worktree.appendingPathComponent("examples/synthetic/notices.json")
    try requireFixture(workspace)
    try requireFixture(notices)

    let process = Process()
    let standardOutput = Pipe()
    let standardError = Pipe()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    process.arguments = [
      "python3",
      "-m",
      "tenderverdict",
      "portfolio",
      "--workspace",
      workspace.path,
      "--notices",
      notices.path,
      "--as-of",
      Self.syntheticAsOf,
    ]
    process.currentDirectoryURL = worktree
    process.environment = childEnvironment()
    process.standardOutput = standardOutput
    process.standardError = standardError

    try process.run()
    process.waitUntilExit()
    let output = standardOutput.fileHandleForReading.readDataToEndOfFile()
    let errorOutput = standardError.fileHandleForReading.readDataToEndOfFile()
    guard process.terminationStatus == 0 else {
      let detail = String(decoding: errorOutput.prefix(2_000), as: UTF8.self)
        .trimmingCharacters(in: .whitespacesAndNewlines)
      throw TenderVerdictProcessError.commandFailed(process.terminationStatus, detail)
    }
    guard output.count <= Self.maximumSyntheticReportBytes else {
      throw TenderVerdictProcessError.oversizedOutput
    }
    return try PortfolioWorkspaceReport.decode(output)
  }

  private func requireFixture(_ url: URL) throws {
    guard FileManager.default.fileExists(atPath: url.path) else {
      throw TenderVerdictProcessError.missingSyntheticFixture(url.lastPathComponent)
    }
  }

  private func childEnvironment() -> [String: String] {
    let parent = ProcessInfo.processInfo.environment
    var environment = [
      "PATH": parent["PATH"] ?? "/usr/bin:/bin",
      "PYTHONDONTWRITEBYTECODE": "1",
      "PYTHONPATH": worktree.appendingPathComponent("src").path,
    ]
    for name in ["LANG", "LC_ALL"] {
      if let value = parent[name] {
        environment[name] = value
      }
    }
    return environment
  }
}
