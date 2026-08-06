import Foundation

enum WorkspaceContinuityError: Error {
  case unavailableDefaults
  case roundTripFailed
}

/// Opt-in continuity for the two local input selections.
///
/// Only security-scoped bookmarks are persisted. Tender data, generated reports,
/// review dates, and RevenueCat configuration remain session-only.
struct WorkspaceContinuity {
  struct RestoredSelections {
    let workspace: URL?
    let notices: URL?
    let refreshedStaleBookmark: Bool
  }

  private enum Key {
    static let enabled = "nextGen.rememberInputSelections"
    static let workspace = "nextGen.workspaceBookmark"
    static let notices = "nextGen.noticesBookmark"
  }

  private let defaults: UserDefaults

  init(defaults: UserDefaults = .standard) {
    self.defaults = defaults
  }

  var isEnabled: Bool {
    defaults.bool(forKey: Key.enabled)
  }

  func restore() -> RestoredSelections {
    guard isEnabled else {
      return RestoredSelections(
        workspace: nil,
        notices: nil,
        refreshedStaleBookmark: false
      )
    }

    let workspace = resolveBookmark(forKey: Key.workspace)
    let notices = resolveBookmark(forKey: Key.notices)
    return RestoredSelections(
      workspace: workspace.url,
      notices: notices.url,
      refreshedStaleBookmark: workspace.wasStale || notices.wasStale
    )
  }

  func setEnabled(_ enabled: Bool, workspace: URL?, notices: URL?) throws {
    defaults.set(enabled, forKey: Key.enabled)
    guard enabled else {
      defaults.removeObject(forKey: Key.workspace)
      defaults.removeObject(forKey: Key.notices)
      return
    }
    try update(workspace: workspace, notices: notices)
  }

  func update(workspace: URL?, notices: URL?) throws {
    guard isEnabled else { return }
    if let workspace {
      try saveBookmark(for: workspace, key: Key.workspace)
    }
    if let notices {
      try saveBookmark(for: notices, key: Key.notices)
    }
  }

  private func saveBookmark(for url: URL, key: String) throws {
    let data = try url.bookmarkData(
      options: [.withSecurityScope],
      includingResourceValuesForKeys: nil,
      relativeTo: nil
    )
    defaults.set(data, forKey: key)
  }

  private func resolveBookmark(forKey key: String) -> (url: URL?, wasStale: Bool) {
    guard let data = defaults.data(forKey: key) else {
      return (nil, false)
    }
    var isStale = false
    do {
      let url = try URL(
        resolvingBookmarkData: data,
        options: [.withSecurityScope],
        relativeTo: nil,
        bookmarkDataIsStale: &isStale
      )
      if isStale {
        try saveBookmark(for: url, key: key)
      }
      return (url, isStale)
    } catch {
      defaults.removeObject(forKey: key)
      return (nil, false)
    }
  }

  static func verifyIsolatedRoundTrip() throws {
    let suiteName = "TenderVerdictNextGenSmoke.\(UUID().uuidString)"
    guard let defaults = UserDefaults(suiteName: suiteName) else {
      throw WorkspaceContinuityError.unavailableDefaults
    }
    defaults.removePersistentDomain(forName: suiteName)
    let directory = FileManager.default.temporaryDirectory
      .appendingPathComponent("TenderVerdictContinuity-\(UUID().uuidString)", isDirectory: true)
    try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: false)
    defer {
      defaults.removePersistentDomain(forName: suiteName)
      try? FileManager.default.removeItem(at: directory)
    }

    let workspace = directory.appendingPathComponent("workspace.json")
    let notices = directory.appendingPathComponent("notices.json")
    try Data("{}\n".utf8).write(to: workspace, options: [.atomic])
    try Data("[]\n".utf8).write(to: notices, options: [.atomic])

    let continuity = WorkspaceContinuity(defaults: defaults)
    try continuity.setEnabled(true, workspace: workspace, notices: notices)
    let restored = continuity.restore()
    guard continuity.isEnabled,
      restored.workspace?.standardizedFileURL == workspace.standardizedFileURL,
      restored.notices?.standardizedFileURL == notices.standardizedFileURL,
      defaults.data(forKey: Key.workspace) != nil,
      defaults.data(forKey: Key.notices) != nil
    else {
      throw WorkspaceContinuityError.roundTripFailed
    }

    try continuity.setEnabled(false, workspace: nil, notices: nil)
    let forgotten = continuity.restore()
    guard !continuity.isEnabled,
      forgotten.workspace == nil,
      forgotten.notices == nil,
      defaults.data(forKey: Key.workspace) == nil,
      defaults.data(forKey: Key.notices) == nil
    else {
      throw WorkspaceContinuityError.roundTripFailed
    }
  }
}
