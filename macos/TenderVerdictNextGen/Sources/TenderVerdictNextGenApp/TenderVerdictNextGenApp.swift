import AppKit
import Darwin
import SwiftUI
import TenderVerdictNextGenCore
import UniformTypeIdentifiers

@main
struct TenderVerdictNextGenApp: App {
  @StateObject private var model: AppModel

  init() {
    if let flag = CommandLine.arguments.firstIndex(of: "--render-review-brief"),
      CommandLine.arguments.indices.contains(flag + 1)
    {
      Self.renderReviewBrief(
        at: CommandLine.arguments[flag + 1],
        premiumUnlocked: CommandLine.arguments.contains("--premium")
      )
    }
    if let flag = CommandLine.arguments.firstIndex(of: "--render-submission-screenshot"),
      CommandLine.arguments.indices.contains(flag + 1)
    {
      let colorScheme: ColorScheme = CommandLine.arguments.contains("--dark") ? .dark : .light
      Self.renderSubmissionScreenshot(
        at: CommandLine.arguments[flag + 1],
        colorScheme: colorScheme
      )
    }
    if CommandLine.arguments.contains("--smoke-test") {
      Self.runSmokeTest()
    }
    _model = StateObject(wrappedValue: AppModel())
  }

  var body: some Scene {
    WindowGroup("TenderVerdict Next Gen") {
      ContentView(model: model)
        .frame(minWidth: 900, minHeight: 720)
    }
    .defaultSize(width: 1_020, height: 900)
  }

  private static func runSmokeTest() -> Never {
    do {
      let runner = try TenderVerdictProcess()
      let execution = try runner.loadSyntheticPortfolioSynchronously()
      let report = execution.report
      let freeCount = report.visibleProfileReports(premiumUnlocked: false).count
      let premiumCount = report.visibleProfileReports(premiumUnlocked: true).count
      try WorkspaceContinuity.verifyIsolatedRoundTrip()
      print(
        "NEXT_GEN_SMOKE_OK schema=\(report.schemaVersion) "
          + "profiles=\(report.summary.profileCount) "
          + "notices=\(report.summary.noticeCount) "
          + "free_visible=\(freeCount) premium_visible=\(premiumCount) "
          + "continuity=bookmark_only "
          + "entitlement=\(RevenueCatAccessController.entitlementIdentifier)"
      )
      Darwin.exit(EXIT_SUCCESS)
    } catch {
      let message = (error as? LocalizedError)?.errorDescription ?? "unknown error"
      FileHandle.standardError.write(Data("NEXT_GEN_SMOKE_FAIL: \(message)\n".utf8))
      Darwin.exit(EXIT_FAILURE)
    }
  }

  private static func renderReviewBrief(
    at path: String,
    premiumUnlocked: Bool
  ) -> Never {
    do {
      let execution = try TenderVerdictProcess().loadSyntheticPortfolioSynchronously()
      let brief = try execution.report.shareableReviewBriefHTMLData(
        premiumUnlocked: premiumUnlocked
      )
      let output = URL(fileURLWithPath: path).standardizedFileURL
      try FileManager.default.createDirectory(
        at: output.deletingLastPathComponent(),
        withIntermediateDirectories: true
      )
      try brief.write(to: output, options: [.atomic])
      let scope = premiumUnlocked ? "portfolio" : "first_profile"
      print(
        "NEXT_GEN_BRIEF_OK scope=\(scope) bytes=\(brief.count) output=\(output.path)"
      )
      Darwin.exit(EXIT_SUCCESS)
    } catch {
      let message = (error as? LocalizedError)?.errorDescription ?? String(describing: error)
      FileHandle.standardError.write(Data("NEXT_GEN_BRIEF_FAIL: \(message)\n".utf8))
      Darwin.exit(EXIT_FAILURE)
    }
  }

  @MainActor
  private static func renderSubmissionScreenshot(
    at path: String,
    colorScheme: ColorScheme
  ) -> Never {
    do {
      let execution = try TenderVerdictProcess().loadSyntheticPortfolioSynchronously()
      let model = AppModel(previewExecution: execution)
      let logicalWidth: CGFloat = 800
      let logicalHeight: CGFloat = 2_556 * logicalWidth / 1_179
      let view = ContentView(model: model, startsAutomatically: false, scrollable: false)
        .frame(width: logicalWidth, height: logicalHeight, alignment: .top)
        .background(Color(nsColor: .windowBackgroundColor))
        .environment(\.colorScheme, colorScheme)
      let bounds = NSRect(x: 0, y: 0, width: logicalWidth, height: logicalHeight)
      let hostingView = NSHostingView(rootView: view)
      hostingView.frame = bounds
      let window = NSWindow(
        contentRect: bounds,
        styleMask: [.borderless],
        backing: .buffered,
        defer: false
      )
      window.contentView = hostingView
      window.backgroundColor = .windowBackgroundColor
      window.appearance = NSAppearance(
        named: colorScheme == .dark ? .darkAqua : .aqua
      )
      window.orderBack(nil)
      hostingView.layoutSubtreeIfNeeded()
      hostingView.displayIfNeeded()
      guard
        let bitmap = NSBitmapImageRep(
          bitmapDataPlanes: nil,
          pixelsWide: 1_179,
          pixelsHigh: 2_556,
          bitsPerSample: 8,
          samplesPerPixel: 4,
          hasAlpha: true,
          isPlanar: false,
          colorSpaceName: .deviceRGB,
          bytesPerRow: 1_179 * 4,
          bitsPerPixel: 32
        )
      else {
        throw CocoaError(.fileWriteUnknown)
      }
      bitmap.size = NSSize(width: logicalWidth, height: logicalHeight)
      hostingView.cacheDisplay(in: bounds, to: bitmap)
      window.orderOut(nil)
      guard
        let png = bitmap.representation(using: .png, properties: [.compressionFactor: 0.85])
      else {
        throw CocoaError(.fileWriteUnknown)
      }
      let output = URL(fileURLWithPath: path).standardizedFileURL
      try FileManager.default.createDirectory(
        at: output.deletingLastPathComponent(),
        withIntermediateDirectories: true
      )
      try png.write(to: output, options: [.atomic])
      let appearance = colorScheme == .dark ? "dark" : "light"
      print(
        "NEXT_GEN_SCREENSHOT_OK width=1179 height=2556 "
          + "appearance=\(appearance) "
          + "output=\(output.path)"
      )
      Darwin.exit(EXIT_SUCCESS)
    } catch {
      let message = (error as? LocalizedError)?.errorDescription ?? String(describing: error)
      FileHandle.standardError.write(Data("NEXT_GEN_SCREENSHOT_FAIL: \(message)\n".utf8))
      Darwin.exit(EXIT_FAILURE)
    }
  }
}

@MainActor
final class AppModel: ObservableObject {
  @Published private(set) var report: PortfolioWorkspaceReport?
  @Published private(set) var loadError: String?
  @Published private(set) var inputError: String?
  @Published private(set) var isLoading = false
  @Published private(set) var isPreparingInput = false
  @Published private(set) var workspaceURL: URL?
  @Published private(set) var noticesURL: URL?
  @Published private(set) var workspaceDocument: PortfolioWorkspaceDocument?
  @Published private(set) var noticePreview: NoticeImportPreview?
  @Published private(set) var rememberSelections = false
  @Published private(set) var sourceDescription = "Synthetic example"
  @Published private(set) var reportIsPrevious = false
  @Published private(set) var statusMessage: String?
  @Published var isProfileBuilderPresented = false
  @Published var asOf = TenderVerdictProcess.syntheticAsOf {
    didSet {
      guard !isApplyingReport, oldValue != asOf else { return }
      markReportAsPrevious()
      if inputError == ReviewPointInputValidator.guidance {
        inputError = nil
      }
    }
  }

  let revenueCat: RevenueCatAccessController

  private let runner: TenderVerdictProcess?
  private let continuity: WorkspaceContinuity
  private var reportData: Data?
  private var started = false
  private var isApplyingReport = false

  init() {
    continuity = WorkspaceContinuity()
    rememberSelections = continuity.isEnabled
    revenueCat = RevenueCatAccessController()
    do {
      runner = try TenderVerdictProcess()
    } catch {
      runner = nil
      loadError = Self.message(
        for: error,
        fallback: "TenderVerdict runtime is unavailable."
      )
    }
  }

  init(previewExecution: PortfolioExecution) {
    continuity = WorkspaceContinuity()
    revenueCat = RevenueCatAccessController(environment: [:])
    runner = nil
    report = previewExecution.report
    reportData = previewExecution.jsonData
    sourceDescription = "Synthetic example"
    statusMessage =
      "Analyzed \(previewExecution.report.summary.noticeCount) notices for "
      + "\(previewExecution.report.summary.profileCount) profiles."
  }

  var canRunSelected: Bool {
    workspaceURL != nil && noticesURL != nil && workspaceDocument != nil
      && noticePreview != nil && !isLoading && !isPreparingInput
  }

  var canExport: Bool {
    report != nil && reportData != nil && !isLoading
  }

  var workspaceName: String {
    workspaceURL?.lastPathComponent ?? "Choose a workspace v1 JSON file"
  }

  var noticesName: String {
    noticesURL?.lastPathComponent ?? "Choose normalized CSV or JSON notices"
  }

  var reviewPointError: String? {
    ReviewPointInputValidator.validationMessage(for: asOf)
  }

  var exportMenuTitle: String {
    reportIsPrevious ? "Export previous…" : "Export…"
  }

  var syntheticButtonTitle: String {
    sourceDescription == "Synthetic example" && report != nil && !reportIsPrevious
      ? "Reload guided example"
      : "Try guided example"
  }

  func start() {
    guard !started else {
      return
    }
    started = true
    Task { await revenueCat.start() }
    restoreRememberedSelections()
    loadSynthetic()
  }

  func chooseWorkspace() {
    let panel = NSOpenPanel()
    panel.title = "Choose a TenderVerdict workspace"
    panel.prompt = "Choose Workspace"
    panel.allowedContentTypes = [.json]
    panel.allowsMultipleSelection = false
    panel.canChooseDirectories = false
    guard panel.runModal() == .OK, let url = panel.url else {
      return
    }
    prepareWorkspace(url)
  }

  func chooseNotices() {
    let panel = NSOpenPanel()
    panel.title = "Choose normalized tender notices"
    panel.prompt = "Choose Notices"
    panel.allowedContentTypes = [.json, .commaSeparatedText]
    panel.allowsMultipleSelection = false
    panel.canChooseDirectories = false
    guard panel.runModal() == .OK, let url = panel.url else {
      return
    }
    prepareNotices(url)
  }

  func presentProfileBuilder() {
    inputError = nil
    isProfileBuilderPresented = true
  }

  func saveWorkspace(_ document: PortfolioWorkspaceDocument) {
    guard let runner, !isPreparingInput else { return }
    isPreparingInput = true
    inputError = nil
    statusMessage = "Validating the workspace against bundled authority tables…"
    Task {
      let temporaryURL = FileManager.default.temporaryDirectory
        .appendingPathComponent("TenderVerdictWorkspace-\(UUID().uuidString).json")
      defer { try? FileManager.default.removeItem(at: temporaryURL) }
      do {
        try document.normalizedJSONData().write(to: temporaryURL, options: [.atomic])
        let normalization = try await runner.normalizeWorkspace(temporaryURL)
        let panel = NSSavePanel()
        panel.title = "Save TenderVerdict workspace"
        panel.prompt = "Save Workspace"
        panel.allowedContentTypes = [.json]
        panel.canCreateDirectories = true
        panel.nameFieldStringValue = "portfolio-workspace.json"
        guard panel.runModal() == .OK, let url = panel.url else {
          isPreparingInput = false
          statusMessage = "Workspace validation passed; saving was cancelled."
          return
        }
        try normalization.jsonData.write(to: url, options: [.atomic])
        workspaceURL = url
        workspaceDocument = normalization.document
        markReportAsPrevious()
        let continuityReady = rememberCurrentSelectionsIfNeeded()
        isPreparingInput = false
        isProfileBuilderPresented = false
        inputError = nil
        statusMessage =
          "Saved \(normalization.document.profiles.count) validated profiles in "
          + "\(url.lastPathComponent)."
          + (continuityReady ? "" : " File access will not be remembered.")
      } catch {
        failInput(error, fallback: "The workspace could not be validated and saved.")
      }
    }
  }

  func setRememberSelections(_ enabled: Bool) {
    do {
      try continuity.setEnabled(enabled, workspace: workspaceURL, notices: noticesURL)
      rememberSelections = enabled
      inputError = nil
      statusMessage =
        enabled
        ? "This Mac will remember only the two selected file bookmarks."
        : "Remembered file selections were forgotten. Current files remain selected."
    } catch {
      rememberSelections = false
      try? continuity.setEnabled(false, workspace: nil, notices: nil)
      failInput(error, fallback: "The selected files could not be remembered on this Mac.")
    }
  }

  func runSelectedPortfolio() {
    guard let runner, let workspaceURL, let noticesURL, canRunSelected else {
      return
    }
    let reviewPoint = asOf.trimmingCharacters(in: .whitespacesAndNewlines)
    if let reviewPointError {
      inputError = reviewPointError
      statusMessage = nil
      return
    }
    markReportAsPrevious()
    beginLoading()
    Task {
      let workspaceAccess = workspaceURL.startAccessingSecurityScopedResource()
      let noticesAccess = noticesURL.startAccessingSecurityScopedResource()
      defer {
        if workspaceAccess { workspaceURL.stopAccessingSecurityScopedResource() }
        if noticesAccess { noticesURL.stopAccessingSecurityScopedResource() }
      }
      do {
        let execution = try await runner.runPortfolio(
          workspace: workspaceURL,
          notices: noticesURL,
          asOf: reviewPoint
        )
        apply(
          execution,
          source: "\(workspaceURL.lastPathComponent) + \(noticesURL.lastPathComponent)"
        )
      } catch {
        fail(error, fallback: "The selected portfolio could not be analyzed.")
      }
    }
  }

  func loadSynthetic() {
    guard let runner else {
      return
    }
    beginLoading()
    Task {
      do {
        let execution = try await runner.loadSyntheticPortfolio()
        apply(execution, source: "Synthetic example")
      } catch {
        fail(error, fallback: "The synthetic portfolio could not be loaded.")
      }
    }
  }

  func exportReport() {
    guard let report, let reportData, let primary = report.profileReports.first else {
      return
    }
    let premiumUnlocked = revenueCat.state.isUnlocked
    let panel = NSSavePanel()
    panel.title =
      premiumUnlocked
      ? reportIsPrevious
        ? "Export previous deterministic portfolio report"
        : "Export deterministic portfolio report"
      : reportIsPrevious
        ? "Export previous deterministic single-profile report"
        : "Export deterministic single-profile report"
    panel.prompt = "Export JSON"
    panel.allowedContentTypes = [.json]
    panel.canCreateDirectories = true
    panel.nameFieldStringValue =
      premiumUnlocked
      ? "tenderverdict-portfolio-report.json"
      : "tenderverdict-profile-report.json"
    guard panel.runModal() == .OK, let url = panel.url else {
      return
    }
    do {
      let exportData =
        premiumUnlocked
        ? reportData
        : try primary.deterministicJSONData()
      try exportData.write(to: url, options: [.atomic])
      statusMessage =
        reportIsPrevious
        ? "Exported previous report as \(url.lastPathComponent)."
        : "Exported \(url.lastPathComponent)."
      loadError = nil
    } catch {
      loadError = Self.message(for: error, fallback: "The report could not be exported.")
    }
  }

  func exportReviewBrief() {
    guard let report else {
      return
    }
    let premiumUnlocked = revenueCat.state.isUnlocked
    let panel = NSSavePanel()
    panel.title =
      reportIsPrevious
      ? "Export previous human review brief"
      : "Export human review brief"
    panel.prompt = "Export Brief"
    panel.allowedContentTypes = [.html]
    panel.canCreateDirectories = true
    panel.nameFieldStringValue =
      premiumUnlocked
      ? "tenderverdict-portfolio-review-brief.html"
      : "tenderverdict-profile-review-brief.html"
    guard panel.runModal() == .OK, let url = panel.url else {
      return
    }
    do {
      let brief = try report.shareableReviewBriefHTMLData(
        premiumUnlocked: premiumUnlocked
      )
      try brief.write(to: url, options: [.atomic])
      statusMessage =
        reportIsPrevious
        ? "Exported the previous review brief as \(url.lastPathComponent)."
        : "Exported \(url.lastPathComponent)."
      loadError = nil
    } catch {
      loadError = Self.message(
        for: error,
        fallback: "The review brief could not be exported."
      )
    }
  }

  private func beginLoading() {
    isLoading = true
    loadError = nil
    statusMessage = "Running local deterministic analysis…"
  }

  private func prepareWorkspace(_ url: URL) {
    guard let runner, !isPreparingInput else { return }
    isPreparingInput = true
    inputError = nil
    statusMessage = "Validating \(url.lastPathComponent)…"
    Task {
      let access = url.startAccessingSecurityScopedResource()
      defer { if access { url.stopAccessingSecurityScopedResource() } }
      do {
        let normalization = try await runner.normalizeWorkspace(url)
        workspaceURL = url
        workspaceDocument = normalization.document
        markReportAsPrevious()
        let continuityReady = rememberCurrentSelectionsIfNeeded()
        isPreparingInput = false
        inputError = nil
        statusMessage =
          "Workspace ready: \(normalization.document.profiles.count) validated profiles."
          + (continuityReady ? "" : " File access will not be remembered.")
      } catch {
        failInput(error, fallback: "The selected workspace is not valid.")
      }
    }
  }

  private func prepareNotices(_ url: URL) {
    guard let runner, !isPreparingInput else { return }
    isPreparingInput = true
    inputError = nil
    statusMessage = "Inspecting \(url.lastPathComponent)…"
    Task {
      let access = url.startAccessingSecurityScopedResource()
      defer { if access { url.stopAccessingSecurityScopedResource() } }
      do {
        let preview = try await runner.inspectNotices(url)
        noticesURL = url
        noticePreview = preview
        markReportAsPrevious()
        let continuityReady = rememberCurrentSelectionsIfNeeded()
        isPreparingInput = false
        inputError = nil
        statusMessage =
          "Notices ready: \(preview.noticeCount) normalized records."
          + (continuityReady ? "" : " File access will not be remembered.")
      } catch {
        failInput(error, fallback: "The selected notices file is not valid.")
      }
    }
  }

  private func restoreRememberedSelections() {
    guard rememberSelections, runner != nil else { return }
    let restored = continuity.restore()
    guard restored.workspace != nil || restored.notices != nil else { return }
    if let workspace = restored.workspace {
      prepareWorkspace(workspace)
    }
    if let notices = restored.notices {
      Task {
        while isPreparingInput {
          try? await Task.sleep(nanoseconds: 20_000_000)
        }
        prepareNotices(notices)
      }
    }
    if restored.refreshedStaleBookmark {
      statusMessage = "Refreshed remembered file access. No analysis was run automatically."
    }
  }

  private func rememberCurrentSelectionsIfNeeded() -> Bool {
    guard rememberSelections else { return true }
    do {
      try continuity.update(workspace: workspaceURL, notices: noticesURL)
      return true
    } catch {
      rememberSelections = false
      try? continuity.setEnabled(false, workspace: nil, notices: nil)
      return false
    }
  }

  private func failInput(_ error: Error, fallback: String) {
    inputError = Self.message(for: error, fallback: fallback)
    isPreparingInput = false
    statusMessage = nil
  }

  private func apply(_ execution: PortfolioExecution, source: String) {
    isApplyingReport = true
    report = execution.report
    reportData = execution.jsonData
    asOf = execution.report.asOf
    sourceDescription = source
    reportIsPrevious = false
    isApplyingReport = false
    loadError = nil
    isLoading = false
    statusMessage =
      "Analyzed \(execution.report.summary.noticeCount) notices for "
      + "\(execution.report.summary.profileCount) profiles."
  }

  private func fail(_ error: Error, fallback: String) {
    loadError = Self.message(for: error, fallback: fallback)
    isLoading = false
    statusMessage = nil
  }

  private static func message(for error: Error, fallback: String) -> String {
    if let processError = error as? TenderVerdictProcessError,
      case .commandFailed(_, let detail) = processError
    {
      var cleaned = normalizedDisplayText(detail)
      if cleaned.lowercased().hasPrefix("error:") {
        cleaned = String(cleaned.dropFirst(6)).trimmingCharacters(in: .whitespaces)
      }
      return cleaned.isEmpty ? fallback : cleaned
    }
    return (error as? LocalizedError)?.errorDescription ?? fallback
  }

  private func markReportAsPrevious() {
    if report != nil {
      reportIsPrevious = true
    }
  }
}

struct ContentView: View {
  @ObservedObject var model: AppModel
  var startsAutomatically = true
  var scrollable = true
  @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

  var body: some View {
    Group {
      if scrollable {
        ScrollView { content }
      } else {
        content
      }
    }
    .background(Color(nsColor: .windowBackgroundColor))
    .tint(.indigo)
    .task {
      if startsAutomatically {
        model.start()
      }
    }
    .sheet(isPresented: $model.isProfileBuilderPresented) {
      ProfileBuilderView(
        document: model.workspaceDocument,
        externalError: model.inputError,
        isSaving: model.isPreparingInput
      ) { document in
        model.saveWorkspace(document)
      }
    }
  }

  private var content: some View {
    VStack(alignment: .leading, spacing: 28) {
      header
      sourceStatus
      portfolioSignal
      PortfolioInputSection(model: model)
      freeAnalysis
      PremiumWorkspaceSection(report: model.report, controller: model.revenueCat)
      Spacer(minLength: 0)
      footer
    }
    .frame(maxWidth: 920, maxHeight: .infinity, alignment: .topLeading)
    .padding(.horizontal, 36)
    .padding(.vertical, 32)
  }

  private var header: some View {
    HStack(alignment: .top, spacing: 16) {
      ZStack {
        RoundedRectangle(cornerRadius: 14, style: .continuous)
          .fill(Color.indigo)
        Image(systemName: "doc.text.magnifyingglass")
          .font(.title2.weight(.semibold))
          .foregroundStyle(.white.opacity(0.96))
      }
      .frame(width: 50, height: 50)
      .shadow(
        color: reduceTransparency ? .clear : Color.indigo.opacity(0.18),
        radius: reduceTransparency ? 0 : 10,
        y: reduceTransparency ? 0 : 4
      )
      .accessibilityHidden(true)

      VStack(alignment: .leading, spacing: 9) {
        Text("TenderVerdict")
          .font(.subheadline.weight(.semibold))
          .foregroundStyle(.indigo)
        Text("One tender feed. Different supplier decisions.")
          .font(.largeTitle.bold())
          .fixedSize(horizontal: false, vertical: true)
        Text(
          "Turn procurement metadata into an explainable queue of what to open, verify, or skip, "
            + "then compare the same notices across up to five profiles."
        )
        .font(.title3)
        .foregroundStyle(.secondary)
        .fixedSize(horizontal: false, vertical: true)
      }
    }
    .accessibilityElement(children: .combine)
  }

  private var sourceStatus: some View {
    ViewThatFits(in: .horizontal) {
      HStack(spacing: 0) {
        StatusLabel(title: "Runs on this Mac", systemImage: "lock.shield")
        statusDivider
        StatusLabel(title: "Reasons included", systemImage: "checkmark.seal")
        statusDivider
        StatusLabel(title: "RevenueCat Premium", systemImage: "shippingbox")
      }
      VStack(alignment: .leading, spacing: 8) {
        StatusLabel(title: "Runs on this Mac", systemImage: "lock.shield")
        StatusLabel(title: "Reasons included", systemImage: "checkmark.seal")
        StatusLabel(title: "RevenueCat Premium", systemImage: "shippingbox")
      }
    }
    .foregroundStyle(.secondary)
    .padding(.vertical, 11)
    .overlay(alignment: .top) { Divider() }
    .overlay(alignment: .bottom) { Divider() }
  }

  private var statusDivider: some View {
    Rectangle()
      .fill(.quaternary)
      .frame(width: 1, height: 15)
      .padding(.horizontal, 14)
      .accessibilityHidden(true)
  }

  @ViewBuilder
  private var portfolioSignal: some View {
    if let report = model.report {
      PremiumCard(tint: .indigo) {
        VStack(alignment: .leading, spacing: 16) {
          NoticeCardContent(
            title: "One feed. Different supplier decisions.",
            detail:
              portfolioDifferenceSummary(report)
              + " Every result keeps its own reasons and human next step.",
            systemImage: "arrow.triangle.branch",
            tint: .indigo
          )
          ViewThatFits(in: .horizontal) {
            HStack(spacing: 12) {
              PortfolioSignalMetric(
                value: report.summary.noticeCount,
                title: "Shared notices",
                systemImage: "doc.on.doc"
              )
              PortfolioSignalMetric(
                value: report.summary.profileCount,
                title: "Supplier profiles",
                systemImage: "person.2"
              )
              PortfolioSignalMetric(
                value: report.divergentNoticeCount,
                title: "Changed outcomes",
                systemImage: "arrow.triangle.branch"
              )
            }
            VStack(alignment: .leading, spacing: 10) {
              PortfolioSignalMetric(
                value: report.summary.noticeCount,
                title: "Shared notices",
                systemImage: "doc.on.doc"
              )
              PortfolioSignalMetric(
                value: report.summary.profileCount,
                title: "Supplier profiles",
                systemImage: "person.2"
              )
              PortfolioSignalMetric(
                value: report.divergentNoticeCount,
                title: "Changed outcomes",
                systemImage: "arrow.triangle.branch"
              )
            }
          }
        }
      }
    }
  }

  @ViewBuilder
  private var freeAnalysis: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        title: "Your first supplier review",
        detail:
          "Every verdict, reason, source link, review brief, and JSON export stays available for profile one."
      )
      if let report = model.report,
        let primary = report.visibleProfileReports(premiumUnlocked: false).first
      {
        reportContextCard(report: report)
        ProfileCard(report: primary)
        ReviewQueue(report: primary)
      } else if model.isLoading {
        LoadingCard(label: "Running the local analysis…")
      } else {
        NoticeCard(
          title: "No report loaded",
          detail: model.loadError ?? "Choose inputs above or load the synthetic example.",
          systemImage: "doc.badge.plus",
          tint: .orange
        )
      }
    }
  }

  private func reportContextCard(report: PortfolioWorkspaceReport) -> some View {
    let isSynthetic = model.sourceDescription == "Synthetic example"
    return NoticeCard(
      title: model.reportIsPrevious
        ? "Previous report kept for reference"
        : isSynthetic ? "Bundled demo report" : "Current selected-input report",
      detail: model.reportIsPrevious
        ? "This report still reflects \(model.sourceDescription) at \(report.asOf). "
          + "Run the selected inputs before treating it as current."
        : isSynthetic
          ? "Synthetic data at \(report.asOf). Choose both local inputs above to run your own review."
          : "\(model.sourceDescription) · review point \(report.asOf)",
      systemImage: model.reportIsPrevious
        ? "clock.badge.exclamationmark"
        : isSynthetic ? "sparkles" : "checkmark.seal.fill",
      tint: model.reportIsPrevious ? .orange : isSynthetic ? .indigo : .green
    )
  }

  private var footer: some View {
    ViewThatFits(in: .horizontal) {
      HStack(alignment: .firstTextBaseline) { footerContents }
      VStack(alignment: .leading, spacing: 6) { footerContents }
    }
    .font(.caption)
    .foregroundStyle(.tertiary)
    .accessibilityElement(children: .combine)
  }

  @ViewBuilder
  private var footerContents: some View {
    Label("Report source: \(model.sourceDescription)", systemImage: "externaldrive")
      .lineLimit(1)
    Spacer()
    if let report = model.report {
      Text("Report review point \(report.asOf)")
    }
  }
}

struct PortfolioInputSection: View {
  @ObservedObject var model: AppModel

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        title: "Run a local portfolio review",
        detail:
          "Choose profiles and one normalized notice feed. Every profile uses the same review point."
      )
      PremiumCard(tint: .indigo) {
        VStack(alignment: .leading, spacing: 16) {
          inputRow(
            title: "Workspace",
            systemImage: "square.stack.3d.up",
            value: model.workspaceName,
            buttonTitle: "Choose workspace…",
            action: model.chooseWorkspace
          )
          HStack(alignment: .firstTextBaseline, spacing: 10) {
            Text("No workspace yet? Build and validate one without editing JSON.")
              .font(.caption)
              .foregroundStyle(.secondary)
            Spacer()
            Button {
              model.presentProfileBuilder()
            } label: {
              Label("Build profiles…", systemImage: "person.2.badge.gearshape")
            }
            .buttonStyle(.bordered)
            .disabled(model.isPreparingInput || model.isLoading)
          }
          inputRow(
            title: "Notices",
            systemImage: "doc.on.doc",
            value: model.noticesName,
            buttonTitle: "Choose notices…",
            action: model.chooseNotices
          )
          if let preview = model.noticePreview {
            NoticeImportPreviewView(preview: preview)
          }
          VStack(alignment: .leading, spacing: 7) {
            ViewThatFits(in: .horizontal) {
              HStack(alignment: .firstTextBaseline, spacing: 16) { reviewPointControls }
              VStack(alignment: .leading, spacing: 9) { reviewPointControls }
            }
            if let error = model.reviewPointError {
              Label(error, systemImage: "exclamationmark.circle")
                .font(.caption)
                .foregroundStyle(.orange)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityLabel("Review point error: \(error)")
            }
          }
          Divider()
          ViewThatFits(in: .horizontal) {
            HStack(spacing: 10) { actionButtons }
            VStack(alignment: .leading, spacing: 10) { actionButtons }
          }

          Toggle(
            "Remember these two file selections on this Mac",
            isOn: Binding(
              get: { model.rememberSelections },
              set: { value in model.setRememberSelections(value) }
            )
          )
          .toggleStyle(.checkbox)
          .disabled(model.isPreparingInput)
          Text(
            "Opt in to security-scoped bookmarks only. Tender data, reports, review dates, "
              + "and the RevenueCat key are never persisted by this feature."
          )
          .font(.caption)
          .foregroundStyle(.tertiary)
          .fixedSize(horizontal: false, vertical: true)

          if model.isPreparingInput {
            HStack(spacing: 10) {
              ProgressView().controlSize(.small)
              Text("Validating local input…")
            }
            .foregroundStyle(.secondary)
            .accessibilityElement(children: .combine)
          }

          if model.isLoading {
            HStack(spacing: 10) {
              ProgressView().controlSize(.small)
              Text("Running locally…")
            }
            .foregroundStyle(.secondary)
            .accessibilityElement(children: .combine)
          } else if let error = model.inputError ?? model.loadError {
            Label(normalizedDisplayText(error), systemImage: "exclamationmark.triangle.fill")
              .foregroundStyle(.orange)
              .fixedSize(horizontal: false, vertical: true)
              .accessibilityLabel("Analysis error: \(normalizedDisplayText(error))")
          } else if let status = model.statusMessage {
            Label(normalizedDisplayText(status), systemImage: "checkmark.circle.fill")
              .foregroundStyle(.secondary)
              .accessibilityLabel("Analysis status: \(normalizedDisplayText(status))")
          }
        }
      }
    }
  }

  @ViewBuilder
  private var reviewPointControls: some View {
    Label("Evaluate as of", systemImage: "calendar")
      .font(.subheadline.weight(.semibold))
      .frame(width: 128, alignment: .leading)
    TextField(
      "YYYY-MM-DD or RFC 3339",
      text: Binding(
        get: { model.asOf },
        set: { model.asOf = $0 }
      )
    )
    .textFieldStyle(.roundedBorder)
    .accessibilityLabel("Evaluate notices as of this date or RFC 3339 instant")
    .accessibilityHint("Use YYYY-MM-DD or a timestamp with an explicit UTC offset.")
    Button("Use today") {
      model.asOf = ReviewPointInputValidator.todayString()
    }
    .buttonStyle(.bordered)
    .disabled(model.isPreparingInput || model.isLoading)
  }

  @ViewBuilder
  private var actionButtons: some View {
    Button {
      model.runSelectedPortfolio()
    } label: {
      Label("Run portfolio", systemImage: "play.fill")
        .lineLimit(1)
    }
    .buttonStyle(.borderedProminent)
    .controlSize(.large)
    .disabled(!model.canRunSelected)

    Button {
      model.loadSynthetic()
    } label: {
      Label(model.syntheticButtonTitle, systemImage: "sparkles")
        .lineLimit(1)
    }
    .buttonStyle(.bordered)
    .controlSize(.large)
    .disabled(model.isLoading || model.isPreparingInput)

    Spacer()

    Menu {
      Button {
        model.exportReviewBrief()
      } label: {
        Label("Export review brief…", systemImage: "doc.richtext")
      }
      Button {
        model.exportReport()
      } label: {
        Label("Export JSON…", systemImage: "curlybraces")
      }
    } label: {
      Label(model.exportMenuTitle, systemImage: "square.and.arrow.down")
        .lineLimit(1)
    }
    .menuStyle(.button)
    .buttonStyle(.bordered)
    .controlSize(.large)
    .disabled(!model.canExport)
  }

  private func inputRow(
    title: String,
    systemImage: String,
    value: String,
    buttonTitle: String,
    action: @escaping () -> Void
  ) -> some View {
    ViewThatFits(in: .horizontal) {
      HStack(spacing: 16) {
        inputRowContents(
          title: title,
          systemImage: systemImage,
          value: value,
          buttonTitle: buttonTitle,
          action: action
        )
      }
      VStack(alignment: .leading, spacing: 10) {
        inputRowContents(
          title: title,
          systemImage: systemImage,
          value: value,
          buttonTitle: buttonTitle,
          action: action
        )
      }
    }
  }

  @ViewBuilder
  private func inputRowContents(
    title: String,
    systemImage: String,
    value: String,
    buttonTitle: String,
    action: @escaping () -> Void
  ) -> some View {
    Label(title, systemImage: systemImage)
      .font(.subheadline.weight(.semibold))
      .frame(width: 128, alignment: .leading)
    Text(normalizedDisplayText(value))
      .foregroundStyle(.secondary)
      .lineLimit(1)
      .truncationMode(.middle)
      .frame(maxWidth: .infinity, alignment: .leading)
      .accessibilityLabel("\(title): \(normalizedDisplayText(value))")
    Button(buttonTitle, action: action)
      .buttonStyle(.bordered)
      .controlSize(.large)
      .lineLimit(1)
      .disabled(model.isPreparingInput || model.isLoading)
  }
}

struct PremiumWorkspaceSection: View {
  let report: PortfolioWorkspaceReport?
  @ObservedObject var controller: RevenueCatAccessController
  @State private var apiKeyEntry = ""
  @State private var pendingUserAction = false
  @FocusState private var premiumFocus: PremiumAccessFocusTarget?

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        title: "Portfolio Workspace",
        detail:
          "See where the same notice changes outcome across supplier profiles, then inspect why."
      )
      premiumContent
    }
    .onChange(of: controller.state) { state in
      guard let outcome = state.terminalAccessibilityOutcome else { return }
      PremiumAccessibilityAnnouncer.post(outcome)
      if pendingUserAction {
        premiumFocus = outcome.focusTarget
        pendingUserAction = false
      }
    }
  }

  @ViewBuilder
  private var premiumContent: some View {
    switch controller.state {
    case .testStoreUnavailableInRelease:
      testStoreUnavailableCard
    case .configurationMissing:
      configurationCard(
        title: "Connect a RevenueCat Test Store project",
        detail: "Paste a test_ key for this launch. The key is not stored by TenderVerdict."
      )
    case .configurationRejected:
      configurationCard(
        title: "That key was rejected",
        detail:
          "Use a 12–512 byte RevenueCat Test Store key beginning with test_, "
          + "without spaces or control characters."
      )
    case .loading:
      LoadingCard(label: "Checking Premium access…")
    case .locked(let price):
      actionableLockedCard(
        title: "Portfolio Workspace is locked",
        detail: price.map { value in
          "Current Test Store package: \(value). No real charge is made."
        }
          ?? "The expected supplier_profiles_plus / $rc_monthly / "
          + "supplier_profiles_plus_monthly package is unavailable."
      )
    case .cancelled(let price):
      actionableLockedCard(
        title: "Test Store purchase cancelled",
        detail: price.map { value in
          "Access is unchanged. The available test package is \(value)."
        }
          ?? "Access is unchanged. You can retry after an offering is available."
      )
    case .failed:
      failedCard
    case .unlocked:
      unlockedWorkspace
    }
  }

  private var testStoreUnavailableCard: some View {
    PremiumCard(tint: .indigo) {
      VStack(alignment: .leading, spacing: 16) {
        portfolioValueHeader
        accessPlanSummary
        portfolioPreview
        Divider()
        NoticeCardContent(
          title: "Evaluation purchase is unavailable in Release",
          detail:
            "Use the separately packaged Debug evaluation build to test RevenueCat purchase "
            + "and restore. Release never accepts a Test Store key.",
          systemImage: "lock.shield",
          tint: .indigo
        )
        Text("No RevenueCat key can be entered or configured in this Release app.")
          .font(.caption)
          .foregroundStyle(.secondary)
      }
    }
  }

  private func configurationCard(title: String, detail: String) -> some View {
    PremiumCard(tint: .indigo) {
      VStack(alignment: .leading, spacing: 16) {
        portfolioValueHeader
        accessPlanSummary
        portfolioPreview
        Divider()
        NoticeCardContent(
          title: title,
          detail: detail,
          systemImage: "lock.shield",
          tint: .indigo
        )
        ViewThatFits(in: .horizontal) {
          HStack(spacing: 10) { configurationControls }
          VStack(alignment: .leading, spacing: 10) { configurationControls }
        }
        Text("Entitlement: \(RevenueCatAccessController.entitlementIdentifier)")
          .font(.caption.monospaced())
          .foregroundStyle(.tertiary)
      }
    }
  }

  @ViewBuilder
  private var configurationControls: some View {
    SecureField("test_…", text: $apiKeyEntry)
      .textFieldStyle(.roundedBorder)
      .accessibilityLabel("RevenueCat Test Store API key")
      .focused($premiumFocus, equals: .testStoreAPIKey)
    Button {
      let key = apiKeyEntry
      apiKeyEntry = ""
      pendingUserAction = true
      Task { await controller.configure(testStoreAPIKey: key) }
    } label: {
      Label("Connect Test Store", systemImage: "link")
    }
    .buttonStyle(.borderedProminent)
    .disabled(apiKeyEntry.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
  }

  private func actionableLockedCard(title: String, detail: String) -> some View {
    PremiumCard(tint: .indigo) {
      VStack(alignment: .leading, spacing: 16) {
        portfolioValueHeader
        accessPlanSummary
        portfolioPreview
        Divider()
        NoticeCardContent(
          title: title,
          detail: detail,
          systemImage: "lock",
          tint: .indigo
        )
        ViewThatFits(in: .horizontal) {
          HStack(spacing: 10) { lockedActions }
          VStack(alignment: .leading, spacing: 10) { lockedActions }
        }
      }
    }
  }

  @ViewBuilder
  private var lockedActions: some View {
    Button {
      pendingUserAction = true
      Task { await controller.purchaseCurrentPackage() }
    } label: {
      Label("Unlock with Test Store", systemImage: "cart")
    }
    .buttonStyle(.borderedProminent)
    .disabled(!controller.canPurchase)
    .focused($premiumFocus, equals: .purchase)

    Button {
      pendingUserAction = true
      Task { await controller.restore() }
    } label: {
      Label("Restore access", systemImage: "arrow.clockwise")
    }
    .buttonStyle(.bordered)
    .disabled(!controller.canRestore)
    .focused($premiumFocus, equals: .restore)

    Button {
      pendingUserAction = true
      Task { await controller.refresh() }
    } label: {
      Label("Refresh offering", systemImage: "arrow.triangle.2.circlepath")
    }
    .buttonStyle(.bordered)
    .disabled(controller.state.isBusy)
    .focused($premiumFocus, equals: .refreshOffering)
  }

  private var failedCard: some View {
    PremiumCard(tint: .orange) {
      VStack(alignment: .leading, spacing: 14) {
        NoticeCardContent(
          title: "Premium status could not be refreshed",
          detail:
            "Check the expected Test Store offering, package, product, entitlement, and connection, "
            + "then retry. Quit and reopen the Debug app to replace an already configured key.",
          systemImage: "exclamationmark.arrow.triangle.2.circlepath",
          tint: .orange
        )
        ViewThatFits(in: .horizontal) {
          HStack(spacing: 10) { failedActions }
          VStack(alignment: .leading, spacing: 10) { failedActions }
        }
      }
    }
  }

  @ViewBuilder
  private var failedActions: some View {
    Button("Retry") {
      pendingUserAction = true
      Task { await controller.refresh() }
    }
    .buttonStyle(.borderedProminent)
    .focused($premiumFocus, equals: .retry)
    Button("Restore access") {
      pendingUserAction = true
      Task { await controller.restore() }
    }
    .buttonStyle(.bordered)
    .disabled(!controller.canRestore)
    .focused($premiumFocus, equals: .restore)
  }

  @ViewBuilder
  private var unlockedWorkspace: some View {
    if let report {
      VStack(alignment: .leading, spacing: 12) {
        NoticeCard(
          title: "Portfolio comparison ready",
          detail:
            "RevenueCat confirmed access. Every profile, changed outcome, and the full "
            + "portfolio export are now available.",
          systemImage: "checkmark.seal.fill",
          tint: .green
        )
        HStack {
          Spacer()
          Button {
            pendingUserAction = true
            Task { await controller.restore() }
          } label: {
            Label("Restore access", systemImage: "arrow.clockwise")
          }
          .buttonStyle(.bordered)
          .disabled(!controller.canRestore)
          .focused($premiumFocus, equals: .restore)
        }
        PortfolioComparison(report: report)
        Text("Profile totals")
          .font(.headline)
          .padding(.top, 2)
        ForEach(report.visibleProfileReports(premiumUnlocked: true)) { profile in
          ProfileCard(report: profile)
        }
      }
    } else {
      LoadingCard(label: "Load a local portfolio to use Premium access.")
    }
  }

  private var portfolioPreview: some View {
    VStack(alignment: .leading, spacing: 10) {
      if let report {
        Label(
          "\(report.summary.profileCount) supplier profiles · "
            + "\(report.summary.noticeCount) shared notices",
          systemImage: "person.2"
        )
        if report.summary.profileCount > 1, report.summary.noticeCount > 0 {
          Label(
            portfolioDifferenceSummary(report),
            systemImage: "arrow.triangle.branch"
          )
          .foregroundStyle(.secondary)
          .accessibilityLabel(portfolioDifferenceSummary(report))
        }
        VStack(spacing: 0) {
          ForEach(Array(report.profileReports.enumerated()), id: \.element.id) { item in
            ProfilePreviewRow(profile: item.element, isFree: item.offset == 0)
            if item.offset < report.profileReports.count - 1 {
              Divider()
            }
          }
        }
      } else {
        Label("Up to five named profiles", systemImage: "person.2")
      }
    }
    .font(.subheadline.weight(.medium))
  }

  private var portfolioValueHeader: some View {
    NoticeCardContent(
      title: "Compare the same opportunity across every supplier profile",
      detail:
        "Find changed outcomes without hiding the complete first-profile review behind a paywall.",
      systemImage: "square.grid.3x3.square",
      tint: .indigo
    )
  }

  private var accessPlanSummary: some View {
    ViewThatFits(in: .horizontal) {
      HStack(alignment: .top, spacing: 18) {
        accessPlan(
          title: "Free",
          detail: "1 complete profile · reasons · JSON",
          systemImage: "checkmark.circle.fill"
        )
        Divider().frame(height: 48)
        accessPlan(
          title: "Portfolio",
          detail: "Up to 5 profiles · comparison · portfolio JSON",
          systemImage: "person.2.fill"
        )
      }
      VStack(alignment: .leading, spacing: 12) {
        accessPlan(
          title: "Free",
          detail: "1 complete profile · reasons · JSON",
          systemImage: "checkmark.circle.fill"
        )
        Divider()
        accessPlan(
          title: "Portfolio",
          detail: "Up to 5 profiles · comparison · portfolio JSON",
          systemImage: "person.2.fill"
        )
      }
    }
  }

  private func accessPlan(title: String, detail: String, systemImage: String) -> some View {
    HStack(alignment: .top, spacing: 10) {
      Image(systemName: systemImage)
        .foregroundStyle(.indigo)
        .frame(width: 18)
        .accessibilityHidden(true)
      VStack(alignment: .leading, spacing: 3) {
        Text(title).font(.subheadline.weight(.semibold))
        Text(detail)
          .font(.caption)
          .foregroundStyle(.secondary)
          .fixedSize(horizontal: false, vertical: true)
      }
    }
    .frame(maxWidth: .infinity, alignment: .leading)
    .accessibilityElement(children: .combine)
  }
}

struct ProfilePreviewRow: View {
  let profile: ProfileReport
  let isFree: Bool

  private var accessDescription: String {
    isFree ? "included" : "Premium"
  }

  var body: some View {
    HStack(spacing: 10) {
      Image(systemName: isFree ? "checkmark.circle.fill" : "lock.fill")
        .foregroundStyle(isFree ? Color.green : Color.secondary)
        .frame(width: 18)
        .accessibilityHidden(true)
      Text(profile.profile.displayName)
        .lineLimit(1)
        .truncationMode(.tail)
      Spacer()
      Text(isFree ? "Included" : "Premium")
        .font(.caption.weight(.medium))
        .foregroundStyle(.secondary)
    }
    .padding(.vertical, 8)
    .accessibilityElement(children: .combine)
    .accessibilityLabel(
      "\(profile.profile.displayName), \(accessDescription)"
    )
  }
}

private enum ReviewQueueFilter: String, CaseIterable, Identifiable {
  case all
  case openDocuments
  case watch
  case reject

  var id: String { rawValue }

  var label: String {
    switch self {
    case .all:
      return "All"
    case .openDocuments:
      return "Open"
    case .watch:
      return "Watch"
    case .reject:
      return "Reject"
    }
  }

  func includes(_ result: QualificationResult) -> Bool {
    switch self {
    case .all:
      return true
    case .openDocuments:
      return result.verdict == .openDocuments
    case .watch:
      return result.verdict == .watch
    case .reject:
      return result.verdict == .reject
    }
  }
}

struct ReviewQueue: View {
  let report: ProfileReport
  @Environment(\.dynamicTypeSize) private var dynamicTypeSize
  @State private var filter = ReviewQueueFilter.all
  @State private var searchText = ""
  @State private var buyerText = ""
  @State private var deadlinePresence = DeadlinePresenceFilter.any
  @State private var displayLimit = 8

  private var filteredResults: [QualificationResult] {
    ReviewQuery(
      searchText: searchText,
      buyerText: buyerText,
      deadlinePresence: deadlinePresence
    )
    .apply(to: report.results)
    .filter(filter.includes)
  }

  private var visibleResults: [QualificationResult] {
    Array(filteredResults.prefix(displayLimit))
  }

  private var reportIdentity: String {
    "\(report.id):\(report.asOf):\(report.provenance.noticesSHA256)"
  }

  private var hasActiveFilters: Bool {
    filter != .all || !searchText.isEmpty || !buyerText.isEmpty || deadlinePresence != .any
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      ViewThatFits(in: .horizontal) {
        HStack(alignment: .firstTextBaseline, spacing: 18) {
          queueHeading
          Spacer(minLength: 18)
          filterPicker
        }
        VStack(alignment: .leading, spacing: 10) {
          queueHeading
          filterPicker
        }
      }

      VStack(alignment: .leading, spacing: 10) {
        TextField("Search title, buyer, notice or lot ID", text: $searchText)
          .textFieldStyle(.roundedBorder)
          .accessibilityLabel("Search the review queue")
        ViewThatFits(in: .horizontal) {
          HStack(spacing: 10) { secondaryFilters }
          VStack(alignment: .leading, spacing: 10) { secondaryFilters }
        }
      }

      if report.results.isEmpty {
        NoticeCard(
          title: "No notices in this run",
          detail: "The input was valid, but the shared notice set was empty.",
          systemImage: "tray",
          tint: .gray
        )
      } else if visibleResults.isEmpty {
        VStack(alignment: .leading, spacing: 10) {
          NoticeCard(
            title: "No results in this view",
            detail: "Adjust the search, buyer, deadline, or verdict filters to continue.",
            systemImage: "line.3.horizontal.decrease.circle",
            tint: .gray
          )
          if hasActiveFilters {
            Button("Clear all filters") { clearFilters() }
              .buttonStyle(.bordered)
          }
        }
      } else {
        LazyVStack(spacing: 10) {
          ForEach(visibleResults) { result in
            QualificationResultCard(result: result)
          }
        }
      }

      if visibleResults.count < filteredResults.count {
        Button {
          displayLimit += 8
        } label: {
          Label(
            "Show \(min(8, filteredResults.count - visibleResults.count)) more",
            systemImage: "chevron.down"
          )
        }
        .buttonStyle(.bordered)
      }
    }
    .onChange(of: filter) { _ in
      displayLimit = 8
    }
    .onChange(of: searchText) { _ in displayLimit = 8 }
    .onChange(of: buyerText) { _ in displayLimit = 8 }
    .onChange(of: deadlinePresence) { _ in displayLimit = 8 }
    .onChange(of: reportIdentity) { _ in clearFilters() }
  }

  private var queueHeading: some View {
    VStack(alignment: .leading, spacing: 3) {
      Text("Review queue")
        .font(.headline)
      Text("Open the reasoning only where a human needs more context.")
        .font(.subheadline)
        .foregroundStyle(.secondary)
    }
  }

  private var filterPicker: some View {
    Group {
      if dynamicTypeSize.isAccessibilitySize {
        verdictPicker
          .pickerStyle(.menu)
      } else {
        verdictPicker
          .pickerStyle(.segmented)
      }
    }
    .frame(maxWidth: 360)
  }

  private var verdictPicker: some View {
    Picker("Verdict filter", selection: $filter) {
      ForEach(ReviewQueueFilter.allCases) { item in
        Text(item.label).tag(item)
      }
    }
  }

  @ViewBuilder
  private var secondaryFilters: some View {
    Picker("Buyer", selection: $buyerText) {
      Text("All buyers").tag("")
      ForEach(availableBuyers, id: \.self) { buyer in
        Text(normalizedDisplayText(buyer)).tag(buyer)
      }
    }
    .pickerStyle(.menu)
    .frame(maxWidth: 260)

    Picker("Deadline", selection: $deadlinePresence) {
      Text("Any deadline").tag(DeadlinePresenceFilter.any)
      Text("Deadline supplied").tag(DeadlinePresenceFilter.supplied)
      Text("Deadline missing").tag(DeadlinePresenceFilter.missing)
    }
    .pickerStyle(.menu)
    .frame(maxWidth: 220)

    Text("\(filteredResults.count) results")
      .font(.caption.monospacedDigit())
      .foregroundStyle(.secondary)

    if hasActiveFilters {
      Button("Clear filters") {
        clearFilters()
      }
      .buttonStyle(.borderless)
    }
  }

  private func clearFilters() {
    filter = .all
    searchText = ""
    buyerText = ""
    deadlinePresence = .any
    displayLimit = 8
  }

  private var availableBuyers: [String] {
    Array(
      Set(
        report.results.compactMap { result in
          let buyer = result.buyer?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
          return buyer.isEmpty ? nil : buyer
        }
      )
    ).sorted { $0.localizedCaseInsensitiveCompare($1) == .orderedAscending }
  }
}

struct QualificationResultCard: View {
  let result: QualificationResult
  @State private var detailsVisible = false

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      HStack(alignment: .top, spacing: 14) {
        VStack(alignment: .leading, spacing: 4) {
          Text(result.displayTitle)
            .font(.headline)
            .fixedSize(horizontal: false, vertical: true)
          Text(result.displayReference)
            .font(.caption.monospaced())
            .foregroundStyle(.tertiary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        VerdictBadge(verdict: result.verdict)
      }

      ViewThatFits(in: .horizontal) {
        HStack(spacing: 18) {
          metadata
        }
        VStack(alignment: .leading, spacing: 6) {
          metadata
        }
      }

      HStack(alignment: .top, spacing: 9) {
        Image(systemName: "arrow.turn.down.right")
          .foregroundStyle(result.verdict.tint)
          .accessibilityHidden(true)
        Text(result.displayHumanNextStep)
          .font(.subheadline.weight(.medium))
          .fixedSize(horizontal: false, vertical: true)
      }

      DisclosureGroup("Why this verdict", isExpanded: $detailsVisible) {
        VStack(alignment: .leading, spacing: 12) {
          if !result.displayVerdictDrivers.isEmpty {
            explanationGroup(title: "Verdict drivers", values: result.displayVerdictDrivers)
          }
          if !result.displayUnknowns.isEmpty {
            explanationGroup(title: "Needs confirmation", values: result.displayUnknowns)
          }
          if !result.displaySupportingChecks.isEmpty {
            explanationGroup(title: "Checks passed", values: result.displaySupportingChecks)
          }
          if let sourceURL = result.safeSourceURL {
            Link(destination: sourceURL) {
              Label("Open supplied source", systemImage: "arrow.up.right.square")
            }
            .buttonStyle(.link)
            .help(sourceURL.absoluteString)
          }
        }
        .padding(.top, 8)
        .frame(maxWidth: .infinity, alignment: .leading)
      }
      .font(.subheadline)
    }
    .padding(18)
    .background(
      RoundedRectangle(cornerRadius: 20, style: .continuous)
        .fill(Color(nsColor: .controlBackgroundColor))
    )
    .overlay {
      RoundedRectangle(cornerRadius: 20, style: .continuous)
        .stroke(result.verdict.tint.opacity(0.18), lineWidth: 1)
    }
    .accessibilityElement(children: .contain)
  }

  @ViewBuilder
  private var metadata: some View {
    Label(result.displayBuyer, systemImage: "building.2")
      .lineLimit(1)
    Label(result.displayDeadline, systemImage: "calendar")
      .lineLimit(1)
  }

  private func explanationGroup(title: String, values: [String]) -> some View {
    VStack(alignment: .leading, spacing: 7) {
      Text(title)
        .font(.caption.weight(.semibold))
        .foregroundStyle(.secondary)
      ForEach(Array(values.enumerated()), id: \.offset) { item in
        HStack(alignment: .top, spacing: 9) {
          Image(systemName: "circle.fill")
            .font(.system(size: 4))
            .padding(.top, 7)
            .foregroundStyle(.tertiary)
            .accessibilityHidden(true)
          Text(item.element)
            .fixedSize(horizontal: false, vertical: true)
        }
      }
    }
  }
}

struct PortfolioComparison: View {
  let report: PortfolioWorkspaceReport
  @State private var searchText = ""
  @State private var buyerText = ""
  @State private var deadlinePresence = DeadlinePresenceFilter.any
  @State private var displayLimit = 12
  @State private var selection: ComparisonSelection?

  private var primaryResults: [QualificationResult] {
    let results = report.profileReports.first?.results ?? []
    return ReviewQuery(
      searchText: searchText,
      buyerText: buyerText,
      deadlinePresence: deadlinePresence
    ).apply(to: results)
  }

  private var visibleResults: [QualificationResult] {
    Array(primaryResults.prefix(displayLimit))
  }

  private var reportIdentity: String {
    let profiles = report.profileReports.map(\.id).joined(separator: ":")
    return
      "\(profiles):\(report.asOf):\(report.profileReports.first?.provenance.noticesSHA256 ?? "")"
  }

  var body: some View {
    PremiumCard(tint: .indigo) {
      VStack(alignment: .leading, spacing: 14) {
        VStack(alignment: .leading, spacing: 4) {
          Text("Same notices. Different outcomes.")
            .font(.headline)
          Text("Each cell is an independent verdict. Profiles are never scored or ranked.")
            .font(.subheadline)
            .foregroundStyle(.secondary)
        }

        TextField("Find a notice across every profile", text: $searchText)
          .textFieldStyle(.roundedBorder)
          .accessibilityLabel("Search the portfolio comparison")

        ViewThatFits(in: .horizontal) {
          HStack(spacing: 10) { comparisonFilters }
          VStack(alignment: .leading, spacing: 10) { comparisonFilters }
        }

        if primaryResults.isEmpty {
          Label(
            report.summary.noticeCount == 0
              ? "The shared notice set is empty."
              : "No shared notices match these filters.",
            systemImage: "tray"
          )
          .foregroundStyle(.secondary)
        } else {
          ScrollView(.horizontal, showsIndicators: true) {
            Grid(alignment: .leading, horizontalSpacing: 8, verticalSpacing: 8) {
              GridRow {
                Text("Notice")
                  .font(.caption.weight(.semibold))
                  .foregroundStyle(.secondary)
                  .frame(width: 224, alignment: .leading)
                ForEach(report.profileReports) { profile in
                  Text(profile.profile.displayName)
                    .font(.caption.weight(.semibold))
                    .lineLimit(2)
                    .frame(width: 126, alignment: .leading)
                    .frame(minHeight: 34, alignment: .leading)
                }
              }

              ForEach(visibleResults) { notice in
                ComparisonGridRow(report: report, notice: notice) { selectedProfileID in
                  selection = ComparisonSelection(
                    profileID: selectedProfileID,
                    resultID: notice.id
                  )
                }
              }
            }
          }

          if visibleResults.count < primaryResults.count {
            Button {
              displayLimit += 12
            } label: {
              Label(
                "Show \(min(12, primaryResults.count - visibleResults.count)) more comparisons",
                systemImage: "chevron.down"
              )
            }
            .buttonStyle(.bordered)
          }
        }
      }
    }
    .onChange(of: searchText) { _ in displayLimit = 12 }
    .onChange(of: buyerText) { _ in displayLimit = 12 }
    .onChange(of: deadlinePresence) { _ in displayLimit = 12 }
    .onChange(of: reportIdentity) { _ in clearFilters() }
    .sheet(item: $selection) { selected in
      ComparisonDetailView(report: report, selection: selected)
    }
  }

  @ViewBuilder
  private var comparisonFilters: some View {
    Picker("Buyer", selection: $buyerText) {
      Text("All buyers").tag("")
      ForEach(availableBuyers, id: \.self) { buyer in
        Text(normalizedDisplayText(buyer)).tag(buyer)
      }
    }
    .pickerStyle(.menu)
    .frame(maxWidth: 260)

    Picker("Deadline", selection: $deadlinePresence) {
      Text("Any deadline").tag(DeadlinePresenceFilter.any)
      Text("Deadline supplied").tag(DeadlinePresenceFilter.supplied)
      Text("Deadline missing").tag(DeadlinePresenceFilter.missing)
    }
    .pickerStyle(.menu)
    .frame(maxWidth: 220)

    Text("\(primaryResults.count) shared notices")
      .font(.caption.monospacedDigit())
      .foregroundStyle(.secondary)

    if !searchText.isEmpty || !buyerText.isEmpty || deadlinePresence != .any {
      Button("Clear filters") {
        clearFilters()
      }
      .buttonStyle(.borderless)
    }
  }

  private func clearFilters() {
    searchText = ""
    buyerText = ""
    deadlinePresence = .any
    displayLimit = 12
    selection = nil
  }

  private var availableBuyers: [String] {
    Array(
      Set(
        (report.profileReports.first?.results ?? []).compactMap { result in
          let buyer = result.buyer?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
          return buyer.isEmpty ? nil : buyer
        }
      )
    ).sorted { $0.localizedCaseInsensitiveCompare($1) == .orderedAscending }
  }

}

private struct ComparisonGridRow: View {
  let report: PortfolioWorkspaceReport
  let notice: QualificationResult
  let selectProfile: (String) -> Void

  var body: some View {
    GridRow {
      VStack(alignment: .leading, spacing: 3) {
        Text(notice.displayTitle)
          .font(.subheadline.weight(.medium))
          .lineLimit(2)
        Text(notice.displayReference)
          .font(.caption2.monospaced())
          .foregroundStyle(.tertiary)
      }
      .padding(10)
      .frame(width: 224, alignment: .leading)
      .frame(minHeight: 58, alignment: .leading)
      .background(
        RoundedRectangle(cornerRadius: 12, style: .continuous)
          .fill(Color.primary.opacity(0.035))
      )

      ForEach(report.profileReports) { profile in
        if let result = report.result(profileID: profile.id, resultID: notice.id) {
          ComparisonVerdictCell(
            profileName: profile.profile.displayName,
            noticeTitle: notice.displayTitle,
            result: result
          ) {
            selectProfile(profile.id)
          }
        } else {
          Text("Unavailable")
            .font(.caption)
            .foregroundStyle(.secondary)
            .frame(width: 126)
            .frame(minHeight: 58)
        }
      }
    }
  }
}

private struct ComparisonVerdictCell: View {
  let profileName: String
  let noticeTitle: String
  let result: QualificationResult
  let action: () -> Void

  var body: some View {
    Button(action: action) {
      VerdictBadge(verdict: result.verdict, compact: true)
        .frame(width: 126)
        .frame(minHeight: 58)
        .contentShape(Rectangle())
        .background(
          RoundedRectangle(cornerRadius: 12, style: .continuous)
            .fill(result.verdict.tint.opacity(0.055))
        )
    }
    .buttonStyle(.plain)
    .help("Open reasons and unknowns")
    .accessibilityLabel(accessibilityLabel)
  }

  private var accessibilityLabel: String {
    "\(profileName), \(noticeTitle), \(result.verdict.label). Open details."
  }
}

struct VerdictBadge: View {
  let verdict: QualificationVerdict
  var compact = false
  @Environment(\.colorSchemeContrast) private var contrast

  var body: some View {
    Label(compact ? verdict.shortLabel : verdict.label, systemImage: verdict.systemImage)
      .font(.caption.weight(.semibold))
      .foregroundStyle(verdict.tint)
      .lineLimit(1)
      .padding(.horizontal, compact ? 9 : 11)
      .padding(.vertical, 7)
      .background(
        Capsule(style: .continuous)
          .fill(verdict.tint.opacity(contrast == .increased ? 0.18 : 0.11))
      )
      .overlay {
        Capsule(style: .continuous)
          .stroke(
            verdict.tint.opacity(contrast == .increased ? 0.42 : 0.16),
            lineWidth: contrast == .increased ? 1.5 : 1
          )
      }
      .accessibilityLabel(verdict.label)
  }
}

extension QualificationVerdict {
  fileprivate var label: String {
    switch self {
    case .openDocuments:
      return "Open documents"
    case .watch:
      return "Watch"
    case .reject:
      return "Reject"
    }
  }

  fileprivate var shortLabel: String {
    self == .openDocuments ? "Open" : label
  }

  fileprivate var systemImage: String {
    switch self {
    case .openDocuments:
      return "doc.text.magnifyingglass"
    case .watch:
      return "eye"
    case .reject:
      return "xmark.circle"
    }
  }

  fileprivate var tint: Color {
    switch self {
    case .openDocuments:
      return .green
    case .watch:
      return .orange
    case .reject:
      return .red
    }
  }
}

struct ProfileCard: View {
  let report: ProfileReport
  @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
  @Environment(\.colorSchemeContrast) private var contrast

  var body: some View {
    ViewThatFits(in: .horizontal) {
      HStack(alignment: .center, spacing: 22) {
        profileTitle
        profileMetrics
      }
      VStack(alignment: .leading, spacing: 14) {
        profileTitle
        HStack(spacing: 10) { profileMetrics }
      }
    }
    .padding(18)
    .background(
      RoundedRectangle(cornerRadius: 20, style: .continuous)
        .fill(Color(nsColor: .controlBackgroundColor))
        .shadow(
          color: reduceTransparency ? .clear : Color.indigo.opacity(0.07),
          radius: reduceTransparency ? 0 : 12,
          y: reduceTransparency ? 0 : 5
        )
    )
    .overlay {
      RoundedRectangle(cornerRadius: 20, style: .continuous)
        .stroke(
          Color.primary.opacity(contrast == .increased ? 0.24 : 0.08),
          lineWidth: contrast == .increased ? 1.5 : 1
        )
    }
    .accessibilityElement(children: .combine)
    .accessibilityLabel(
      "\(report.profile.displayName), \(report.summary.openDocuments) open, "
        + "\(report.summary.watch) watch, \(report.summary.reject) reject"
    )
  }

  private var profileTitle: some View {
    VStack(alignment: .leading, spacing: 5) {
      Text(report.profile.displayName)
        .font(.headline)
        .lineLimit(2)
      Text("\(report.summary.total) notices · schema \(report.schemaVersion)")
        .font(.caption)
        .foregroundStyle(.secondary)
    }
    .frame(maxWidth: .infinity, alignment: .leading)
  }

  @ViewBuilder
  private var profileMetrics: some View {
    VerdictMetric(value: report.summary.openDocuments, label: "Open", tint: .green)
    VerdictMetric(value: report.summary.watch, label: "Watch", tint: .orange)
    VerdictMetric(value: report.summary.reject, label: "Reject", tint: .red)
  }
}

struct VerdictMetric: View {
  let value: Int
  let label: String
  let tint: Color

  var body: some View {
    VStack(spacing: 3) {
      Text(value, format: .number)
        .font(.title3.monospacedDigit().weight(.semibold))
        .foregroundStyle(tint)
      Text(label)
        .font(.caption)
        .foregroundStyle(.secondary)
    }
    .frame(minWidth: 54)
    .padding(.horizontal, 5)
    .padding(.vertical, 8)
    .background(
      RoundedRectangle(cornerRadius: 12, style: .continuous)
        .fill(tint.opacity(0.09))
    )
  }
}

struct PremiumCard<Content: View>: View {
  let tint: Color
  @ViewBuilder let content: Content
  @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
  @Environment(\.colorSchemeContrast) private var contrast

  var body: some View {
    content
      .padding(20)
      .frame(maxWidth: .infinity, alignment: .leading)
      .background(
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .fill(Color(nsColor: .controlBackgroundColor))
          .shadow(
            color: reduceTransparency ? .clear : tint.opacity(0.07),
            radius: reduceTransparency ? 0 : 14,
            y: reduceTransparency ? 0 : 6
          )
      )
      .overlay {
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .stroke(
            tint.opacity(contrast == .increased ? 0.46 : 0.2),
            lineWidth: contrast == .increased ? 1.5 : 1
          )
      }
  }
}

struct NoticeCard: View {
  let title: String
  let detail: String
  let systemImage: String
  let tint: Color
  @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
  @Environment(\.colorSchemeContrast) private var contrast

  var body: some View {
    NoticeCardContent(title: title, detail: detail, systemImage: systemImage, tint: tint)
      .padding(18)
      .frame(maxWidth: .infinity, alignment: .leading)
      .background(
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .fill(Color(nsColor: .controlBackgroundColor))
          .shadow(
            color: reduceTransparency ? .clear : tint.opacity(0.07),
            radius: reduceTransparency ? 0 : 12,
            y: reduceTransparency ? 0 : 5
          )
      )
      .overlay {
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .stroke(
            tint.opacity(contrast == .increased ? 0.42 : 0.15),
            lineWidth: contrast == .increased ? 1.5 : 1
          )
      }
  }
}

struct NoticeCardContent: View {
  let title: String
  let detail: String
  let systemImage: String
  let tint: Color

  var body: some View {
    HStack(alignment: .top, spacing: 14) {
      Image(systemName: systemImage)
        .font(.headline)
        .foregroundStyle(tint)
        .frame(width: 24)
        .accessibilityHidden(true)
      VStack(alignment: .leading, spacing: 5) {
        Text(title).font(.headline)
        Text(detail)
          .foregroundStyle(.secondary)
          .fixedSize(horizontal: false, vertical: true)
      }
    }
    .accessibilityElement(children: .combine)
  }
}

struct LoadingCard: View {
  let label: String

  var body: some View {
    HStack(spacing: 12) {
      ProgressView().controlSize(.small)
      Text(label).foregroundStyle(.secondary)
    }
    .padding(18)
    .frame(maxWidth: .infinity, alignment: .leading)
    .background(
      RoundedRectangle(cornerRadius: 20, style: .continuous)
        .fill(Color(nsColor: .controlBackgroundColor))
    )
    .accessibilityElement(children: .combine)
  }
}

struct SectionHeading: View {
  let title: String
  let detail: String

  var body: some View {
    VStack(alignment: .leading, spacing: 5) {
      Text(title).font(.title2.weight(.semibold))
      Text(detail).foregroundStyle(.secondary)
    }
    .accessibilityElement(children: .combine)
  }
}

struct StatusLabel: View {
  let title: String
  let systemImage: String

  var body: some View {
    Label(title, systemImage: systemImage)
      .font(.caption.weight(.medium))
      .lineLimit(1)
  }
}

struct PortfolioSignalMetric: View {
  let value: Int
  let title: String
  let systemImage: String

  var body: some View {
    HStack(spacing: 10) {
      Image(systemName: systemImage)
        .foregroundStyle(.indigo)
        .frame(width: 18)
        .accessibilityHidden(true)
      VStack(alignment: .leading, spacing: 1) {
        Text("\(value)")
          .font(.title3.monospacedDigit().weight(.bold))
        Text(title)
          .font(.caption)
          .foregroundStyle(.secondary)
      }
    }
    .padding(.vertical, 8)
    .padding(.horizontal, 12)
    .frame(maxWidth: .infinity, alignment: .leading)
    .background(
      RoundedRectangle(cornerRadius: 12, style: .continuous)
        .fill(Color.indigo.opacity(0.07))
    )
    .accessibilityElement(children: .combine)
    .accessibilityLabel("\(title): \(value)")
  }
}

private func portfolioDifferenceSummary(_ report: PortfolioWorkspaceReport) -> String {
  if report.summary.noticeCount == 0 {
    return "No notices were supplied; every profile is ready for the same bounded feed."
  }
  if report.summary.profileCount == 1 {
    let noticeNoun = report.summary.noticeCount == 1 ? "notice" : "notices"
    return "\(report.summary.noticeCount) shared \(noticeNoun) reviewed for profile one; "
      + "add another profile to compare decisions."
  }
  let noticeNoun = report.summary.noticeCount == 1 ? "notice" : "notices"
  let verb = report.divergentNoticeCount == 1 ? "changes" : "change"
  return "\(report.divergentNoticeCount) of \(report.summary.noticeCount) shared "
    + "\(noticeNoun) \(verb) verdict across profiles."
}
