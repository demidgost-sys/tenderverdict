import AppKit
import Darwin
import SwiftUI
import TenderVerdictNextGenCore
import UniformTypeIdentifiers

@main
struct TenderVerdictNextGenApp: App {
  @StateObject private var model: AppModel

  init() {
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
      print(
        "NEXT_GEN_SMOKE_OK schema=\(report.schemaVersion) "
          + "profiles=\(report.summary.profileCount) "
          + "notices=\(report.summary.noticeCount) "
          + "free_visible=\(freeCount) premium_visible=\(premiumCount) "
          + "entitlement=\(RevenueCatAccessController.entitlementIdentifier)"
      )
      Darwin.exit(EXIT_SUCCESS)
    } catch {
      let message = (error as? LocalizedError)?.errorDescription ?? "unknown error"
      FileHandle.standardError.write(Data("NEXT_GEN_SMOKE_FAIL: \(message)\n".utf8))
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
      let logicalWidth: CGFloat = 760
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
  @Published private(set) var isLoading = false
  @Published private(set) var workspaceURL: URL?
  @Published private(set) var noticesURL: URL?
  @Published private(set) var sourceDescription = "Synthetic example"
  @Published private(set) var statusMessage: String?
  @Published var asOf = TenderVerdictProcess.syntheticAsOf

  let revenueCat: RevenueCatAccessController

  private let runner: TenderVerdictProcess?
  private var reportData: Data?
  private var started = false

  init() {
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
    workspaceURL != nil && noticesURL != nil && !asOf.trimmingCharacters(in: .whitespaces).isEmpty
      && !isLoading
  }

  var canExport: Bool {
    reportData != nil && !isLoading
  }

  var workspaceName: String {
    workspaceURL?.lastPathComponent ?? "Choose a workspace v1 JSON file"
  }

  var noticesName: String {
    noticesURL?.lastPathComponent ?? "Choose normalized CSV or JSON notices"
  }

  func start() {
    guard !started else {
      return
    }
    started = true
    Task { await revenueCat.start() }
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
    workspaceURL = url
    statusMessage = "Workspace selected. Choose notices and run the analysis."
  }

  func chooseNotices() {
    let panel = NSOpenPanel()
    panel.title = "Choose normalized tender notices"
    panel.prompt = "Choose Notices"
    panel.allowedContentTypes = [.json, .commaSeparatedText, .plainText]
    panel.allowsMultipleSelection = false
    panel.canChooseDirectories = false
    guard panel.runModal() == .OK, let url = panel.url else {
      return
    }
    noticesURL = url
    statusMessage = "Notices selected. Review the as-of value and run the analysis."
  }

  func runSelectedPortfolio() {
    guard let runner, let workspaceURL, let noticesURL, canRunSelected else {
      return
    }
    beginLoading()
    let reviewPoint = asOf.trimmingCharacters(in: .whitespacesAndNewlines)
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
    guard let reportData else {
      return
    }
    let panel = NSSavePanel()
    panel.title = "Export deterministic portfolio report"
    panel.prompt = "Export JSON"
    panel.allowedContentTypes = [.json]
    panel.canCreateDirectories = true
    panel.nameFieldStringValue = "tenderverdict-portfolio-report.json"
    guard panel.runModal() == .OK, let url = panel.url else {
      return
    }
    do {
      try reportData.write(to: url, options: [.atomic])
      statusMessage = "Exported \(url.lastPathComponent)."
      loadError = nil
    } catch {
      loadError = Self.message(for: error, fallback: "The report could not be exported.")
    }
  }

  private func beginLoading() {
    isLoading = true
    loadError = nil
    statusMessage = "Running local deterministic analysis…"
  }

  private func apply(_ execution: PortfolioExecution, source: String) {
    report = execution.report
    reportData = execution.jsonData
    sourceDescription = source
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
    (error as? LocalizedError)?.errorDescription ?? fallback
  }
}

struct ContentView: View {
  @ObservedObject var model: AppModel
  var startsAutomatically = true
  var scrollable = true

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
  }

  private var content: some View {
    VStack(alignment: .leading, spacing: 28) {
      header
      sourceStatus
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
      .shadow(color: Color.indigo.opacity(0.18), radius: 10, y: 4)
      .accessibilityHidden(true)

      VStack(alignment: .leading, spacing: 9) {
        Text("TenderVerdict")
          .font(.subheadline.weight(.semibold))
          .foregroundStyle(.indigo)
        Text("Tender intelligence for every supplier profile.")
          .font(.system(size: 38, weight: .bold, design: .default))
          .tracking(-1.1)
        Text(
          "Run one explainable notice review across a named supplier portfolio, "
            + "with the first profile always available for free."
        )
        .font(.title3)
        .foregroundStyle(.secondary)
        .fixedSize(horizontal: false, vertical: true)
      }
    }
    .accessibilityElement(children: .combine)
  }

  private var sourceStatus: some View {
    HStack(spacing: 0) {
      StatusLabel(title: "Local analysis", systemImage: "lock.shield")
      statusDivider
      StatusLabel(title: "Schema verified", systemImage: "checkmark.seal")
      statusDivider
      StatusLabel(title: "RevenueCat SDK 5.83.0", systemImage: "shippingbox")
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
  private var freeAnalysis: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        title: "Single-profile analysis",
        detail: "The first named profile and the existing verdict workflow remain free."
      )
      if let report = model.report,
        let primary = report.visibleProfileReports(premiumUnlocked: false).first
      {
        ProfileCard(report: primary)
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

  private var footer: some View {
    HStack(alignment: .firstTextBaseline) {
      Label("Local source: \(model.sourceDescription)", systemImage: "externaldrive")
        .lineLimit(1)
      Spacer()
      if let report = model.report {
        Text("Review point \(report.asOf)")
      }
    }
    .font(.caption)
    .foregroundStyle(.tertiary)
    .accessibilityElement(children: .combine)
  }
}

struct PortfolioInputSection: View {
  @ObservedObject var model: AppModel

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        title: "Portfolio inputs",
        detail: "Choose local files once, then run the same bounded notice set for every profile."
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
          inputRow(
            title: "Notices",
            systemImage: "doc.on.doc",
            value: model.noticesName,
            buttonTitle: "Choose notices…",
            action: model.chooseNotices
          )
          HStack(alignment: .firstTextBaseline, spacing: 16) {
            Label("Review point", systemImage: "calendar")
              .font(.subheadline.weight(.semibold))
              .frame(width: 128, alignment: .leading)
            TextField("YYYY-MM-DD or RFC 3339", text: $model.asOf)
              .textFieldStyle(.roundedBorder)
              .accessibilityLabel("Review date or RFC 3339 instant")
          }
          Divider()
          HStack(spacing: 10) {
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
              Label("Load synthetic example", systemImage: "sparkles")
                .lineLimit(1)
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
            .disabled(model.isLoading)

            Spacer()

            Button {
              model.exportReport()
            } label: {
              Label("Export JSON…", systemImage: "square.and.arrow.down")
                .lineLimit(1)
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
            .disabled(!model.canExport)
          }

          if model.isLoading {
            HStack(spacing: 10) {
              ProgressView().controlSize(.small)
              Text("Running locally…")
            }
            .foregroundStyle(.secondary)
            .accessibilityElement(children: .combine)
          } else if let error = model.loadError {
            Label(error, systemImage: "exclamationmark.triangle.fill")
              .foregroundStyle(.orange)
              .fixedSize(horizontal: false, vertical: true)
              .accessibilityLabel("Analysis error: \(error)")
          } else if let status = model.statusMessage {
            Label(status, systemImage: "checkmark.circle.fill")
              .foregroundStyle(.secondary)
              .accessibilityLabel("Analysis status: \(status)")
          }
        }
      }
    }
  }

  private func inputRow(
    title: String,
    systemImage: String,
    value: String,
    buttonTitle: String,
    action: @escaping () -> Void
  ) -> some View {
    HStack(spacing: 16) {
      Label(title, systemImage: systemImage)
        .font(.subheadline.weight(.semibold))
        .frame(width: 128, alignment: .leading)
      Text(value)
        .foregroundStyle(.secondary)
        .lineLimit(1)
        .truncationMode(.middle)
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityLabel("\(title): \(value)")
      Button(buttonTitle, action: action)
        .buttonStyle(.bordered)
        .controlSize(.large)
        .lineLimit(1)
    }
  }
}

struct PremiumWorkspaceSection: View {
  let report: PortfolioWorkspaceReport?
  @ObservedObject var controller: RevenueCatAccessController
  @State private var apiKeyEntry = ""

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        title: "Portfolio Workspace",
        detail: "Reveal up to five independent profile reports through one RevenueCat entitlement."
      )
      premiumContent
    }
  }

  @ViewBuilder
  private var premiumContent: some View {
    switch controller.state {
    case .configurationMissing:
      configurationCard(
        title: "Connect a RevenueCat Test Store project",
        detail: "Paste a test_ key for this launch. The key is not stored by TenderVerdict."
      )
    case .configurationRejected:
      configurationCard(
        title: "That key was rejected",
        detail: "Only a non-empty RevenueCat Test Store key beginning with test_ is accepted."
      )
    case .loading:
      LoadingCard(label: "Checking Premium access…")
    case .locked(let price):
      actionableLockedCard(
        title: "Portfolio Workspace is locked",
        detail: price.map { value in
          "Current Test Store package: \(value). No real charge is made."
        }
          ?? "No current RevenueCat package is available for this Test Store project."
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

  private func configurationCard(title: String, detail: String) -> some View {
    PremiumCard(tint: .indigo) {
      VStack(alignment: .leading, spacing: 16) {
        NoticeCardContent(
          title: title,
          detail: detail,
          systemImage: "lock.shield",
          tint: .indigo
        )
        HStack(spacing: 10) {
          SecureField("test_…", text: $apiKeyEntry)
            .textFieldStyle(.roundedBorder)
            .accessibilityLabel("RevenueCat Test Store API key")
          Button {
            let key = apiKeyEntry
            apiKeyEntry = ""
            Task { await controller.configure(testStoreAPIKey: key) }
          } label: {
            Label("Connect Test Store", systemImage: "link")
          }
          .buttonStyle(.borderedProminent)
          .disabled(apiKeyEntry.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
        }
        portfolioPreview
        Text("Entitlement: \(RevenueCatAccessController.entitlementIdentifier)")
          .font(.caption.monospaced())
          .foregroundStyle(.tertiary)
      }
    }
  }

  private func actionableLockedCard(title: String, detail: String) -> some View {
    PremiumCard(tint: .indigo) {
      VStack(alignment: .leading, spacing: 16) {
        NoticeCardContent(
          title: title,
          detail: detail,
          systemImage: "lock",
          tint: .indigo
        )
        portfolioPreview
        HStack(spacing: 10) {
          Button {
            Task { await controller.purchaseCurrentPackage() }
          } label: {
            Label("Run Test Store purchase", systemImage: "cart")
          }
          .buttonStyle(.borderedProminent)
          .disabled(!controller.canPurchase)

          Button {
            Task { await controller.restore() }
          } label: {
            Label("Restore access", systemImage: "arrow.clockwise")
          }
          .buttonStyle(.bordered)
          .disabled(!controller.canRestore)
        }
      }
    }
  }

  private var failedCard: some View {
    PremiumCard(tint: .orange) {
      VStack(alignment: .leading, spacing: 14) {
        NoticeCardContent(
          title: "Premium status could not be refreshed",
          detail: "Check the Test Store offering, entitlement, and connection, then retry.",
          systemImage: "exclamationmark.arrow.triangle.2.circlepath",
          tint: .orange
        )
        HStack(spacing: 10) {
          Button("Retry") { Task { await controller.refresh() } }
            .buttonStyle(.borderedProminent)
          Button("Restore access") { Task { await controller.restore() } }
            .buttonStyle(.bordered)
            .disabled(!controller.canRestore)
        }
      }
    }
  }

  @ViewBuilder
  private var unlockedWorkspace: some View {
    if let report {
      VStack(alignment: .leading, spacing: 12) {
        NoticeCard(
          title: "Portfolio Workspace unlocked",
          detail: "RevenueCat reports an active supplier_profiles_plus entitlement.",
          systemImage: "checkmark.seal.fill",
          tint: .green
        )
        HStack {
          Spacer()
          Button {
            Task { await controller.restore() }
          } label: {
            Label("Restore access", systemImage: "arrow.clockwise")
          }
          .buttonStyle(.bordered)
          .disabled(!controller.canRestore)
        }
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
          "\(report.summary.profileCount) named profiles · "
            + "\(report.summary.noticeCount) shared notices",
          systemImage: "person.2"
        )
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
      Text(profile.profile.name)
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
      "\(profile.profile.name), \(accessDescription)"
    )
  }
}

struct ProfileCard: View {
  let report: ProfileReport

  var body: some View {
    HStack(alignment: .center, spacing: 22) {
      VStack(alignment: .leading, spacing: 5) {
        Text(report.profile.name)
          .font(.headline)
          .lineLimit(2)
        Text("\(report.summary.total) notices · schema \(report.schemaVersion)")
          .font(.caption)
          .foregroundStyle(.secondary)
      }
      .frame(maxWidth: .infinity, alignment: .leading)

      VerdictMetric(value: report.summary.openDocuments, label: "Open", tint: .green)
      VerdictMetric(value: report.summary.watch, label: "Watch", tint: .orange)
      VerdictMetric(value: report.summary.reject, label: "Reject", tint: .red)
    }
    .padding(18)
    .background(
      RoundedRectangle(cornerRadius: 20, style: .continuous)
        .fill(Color(nsColor: .controlBackgroundColor))
        .shadow(color: Color.indigo.opacity(0.07), radius: 12, y: 5)
    )
    .overlay {
      RoundedRectangle(cornerRadius: 20, style: .continuous)
        .stroke(Color.primary.opacity(0.08), lineWidth: 1)
    }
    .accessibilityElement(children: .combine)
    .accessibilityLabel(
      "\(report.profile.name), \(report.summary.openDocuments) open, "
        + "\(report.summary.watch) watch, \(report.summary.reject) reject"
    )
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

  var body: some View {
    content
      .padding(20)
      .frame(maxWidth: .infinity, alignment: .leading)
      .background(
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .fill(Color(nsColor: .controlBackgroundColor))
          .shadow(color: tint.opacity(0.07), radius: 14, y: 6)
      )
      .overlay {
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .stroke(tint.opacity(0.2), lineWidth: 1)
      }
  }
}

struct NoticeCard: View {
  let title: String
  let detail: String
  let systemImage: String
  let tint: Color

  var body: some View {
    NoticeCardContent(title: title, detail: detail, systemImage: systemImage, tint: tint)
      .padding(18)
      .frame(maxWidth: .infinity, alignment: .leading)
      .background(
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .fill(Color(nsColor: .controlBackgroundColor))
          .shadow(color: tint.opacity(0.07), radius: 12, y: 5)
      )
      .overlay {
        RoundedRectangle(cornerRadius: 20, style: .continuous)
          .stroke(tint.opacity(0.15), lineWidth: 1)
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
        Text(detail).foregroundStyle(.secondary)
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
