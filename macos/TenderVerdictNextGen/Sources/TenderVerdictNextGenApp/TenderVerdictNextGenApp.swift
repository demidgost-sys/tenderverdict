import AppKit
import Darwin
import SwiftUI
import TenderVerdictNextGenCore

@main
struct TenderVerdictNextGenApp: App {
  @StateObject private var model: AppModel

  init() {
    if CommandLine.arguments.contains("--smoke-test") {
      Self.runSmokeTest()
    }
    _model = StateObject(wrappedValue: AppModel())
  }

  var body: some Scene {
    WindowGroup("TenderVerdict Next Gen") {
      ContentView(model: model)
        .frame(minWidth: 860, minHeight: 680)
    }
    .defaultSize(width: 980, height: 820)
  }

  private static func runSmokeTest() -> Never {
    do {
      let runner = try TenderVerdictProcess()
      let report = try runner.loadSyntheticPortfolioSynchronously()
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
}

@MainActor
final class AppModel: ObservableObject {
  @Published private(set) var report: PortfolioWorkspaceReport?
  @Published private(set) var loadError: String?
  let revenueCat: RevenueCatAccessController

  private let runner: TenderVerdictProcess?
  private var started = false

  init() {
    revenueCat = RevenueCatAccessController()
    do {
      runner = try TenderVerdictProcess()
    } catch {
      runner = nil
      loadError =
        (error as? LocalizedError)?.errorDescription
        ?? "TenderVerdict source root is unavailable."
    }
  }

  func start() {
    guard !started else {
      return
    }
    started = true

    Task {
      await revenueCat.start()
    }
    guard let runner else {
      return
    }
    Task {
      do {
        report = try await runner.loadSyntheticPortfolio()
      } catch {
        loadError =
          (error as? LocalizedError)?.errorDescription
          ?? "The synthetic portfolio could not be loaded."
      }
    }
  }
}

struct ContentView: View {
  @ObservedObject var model: AppModel

  var body: some View {
    ScrollView {
      VStack(alignment: .leading, spacing: 28) {
        header
        sourceStatus
        freeAnalysis
        PremiumWorkspaceSection(report: model.report, controller: model.revenueCat)
        footer
      }
      .frame(maxWidth: 900, alignment: .leading)
      .padding(.horizontal, 36)
      .padding(.vertical, 32)
    }
    .background(Color(nsColor: .windowBackgroundColor))
    .task {
      model.start()
    }
  }

  private var header: some View {
    VStack(alignment: .leading, spacing: 10) {
      Text("SHIPATON · NEXT GEN")
        .font(.caption.weight(.semibold))
        .foregroundStyle(.secondary)
        .tracking(1.4)
      Text("Tender intelligence for every supplier profile.")
        .font(.system(size: 36, weight: .bold, design: .rounded))
      Text(
        "Run the same explainable notice review across a named portfolio, "
          + "while preserving one free analysis."
      )
      .font(.title3)
      .foregroundStyle(.secondary)
      .fixedSize(horizontal: false, vertical: true)
    }
    .accessibilityElement(children: .combine)
  }

  private var sourceStatus: some View {
    HStack(spacing: 18) {
      StatusLabel(title: "Local analysis", systemImage: "lock.shield")
      StatusLabel(title: "Schema verified", systemImage: "checkmark.seal")
      StatusLabel(title: "RevenueCat SDK 5.83.0", systemImage: "shippingbox")
    }
    .foregroundStyle(.secondary)
  }

  @ViewBuilder
  private var freeAnalysis: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        eyebrow: "FREE",
        title: "Single-profile analysis",
        detail: "The existing verdict workflow remains available without Premium."
      )
      if let loadError = model.loadError {
        NoticeCard(
          title: "Portfolio data unavailable",
          detail: loadError,
          systemImage: "exclamationmark.triangle",
          tint: .orange
        )
      } else if let report = model.report,
        let primary = report.visibleProfileReports(premiumUnlocked: false).first
      {
        ProfileCard(report: primary)
      } else {
        LoadingCard(label: "Running the local synthetic analysis…")
      }
    }
  }

  private var footer: some View {
    HStack(alignment: .firstTextBaseline) {
      Label("Synthetic local demo · no tender data uploaded", systemImage: "externaldrive")
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

struct PremiumWorkspaceSection: View {
  let report: PortfolioWorkspaceReport?
  @ObservedObject var controller: RevenueCatAccessController

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      SectionHeading(
        eyebrow: "PREMIUM",
        title: "Portfolio Workspace",
        detail: "Evaluate up to five named profiles against one shared notice set."
      )
      premiumContent
    }
  }

  @ViewBuilder
  private var premiumContent: some View {
    switch controller.state {
    case .configurationMissing:
      lockedCard(
        title: "Test Store configuration is missing",
        detail: "The app stays locked and makes no RevenueCat request. "
          + "Supply a Test Store key only in the developer environment."
      )
    case .configurationRejected:
      lockedCard(
        title: "Non-Test Store configuration rejected",
        detail: "This competition build accepts only a RevenueCat key beginning with test_."
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

  private func lockedCard(title: String, detail: String) -> some View {
    PremiumCard(tint: .indigo) {
      HStack(alignment: .top, spacing: 16) {
        Image(systemName: "lock")
          .font(.title2.weight(.semibold))
          .foregroundStyle(.indigo)
          .frame(width: 30)
          .accessibilityHidden(true)
        VStack(alignment: .leading, spacing: 8) {
          Text(title).font(.headline)
          Text(detail).foregroundStyle(.secondary)
          portfolioPreview
          Text("Entitlement: \(RevenueCatAccessController.entitlementIdentifier)")
            .font(.caption.monospaced())
            .foregroundStyle(.tertiary)
        }
      }
    }
  }

  private func actionableLockedCard(title: String, detail: String) -> some View {
    PremiumCard(tint: .indigo) {
      VStack(alignment: .leading, spacing: 16) {
        HStack(alignment: .top, spacing: 16) {
          Image(systemName: "lock")
            .font(.title2.weight(.semibold))
            .foregroundStyle(.indigo)
            .frame(width: 30)
            .accessibilityHidden(true)
          VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.headline)
            Text(detail).foregroundStyle(.secondary)
            portfolioPreview
          }
        }
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
          detail:
            "Check the Test Store project, offering, entitlement, and connection, then retry.",
          systemImage: "exclamationmark.arrow.triangle.2.circlepath",
          tint: .orange
        )
        HStack(spacing: 10) {
          Button("Retry") {
            Task { await controller.refresh() }
          }
          .buttonStyle(.borderedProminent)
          Button("Restore access") {
            Task { await controller.restore() }
          }
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
        ForEach(report.visibleProfileReports(premiumUnlocked: true)) { profile in
          ProfileCard(report: profile)
        }
      }
    } else {
      LoadingCard(label: "Loading the local portfolio…")
    }
  }

  private var portfolioPreview: some View {
    Group {
      if let report {
        Label(
          "\(report.summary.profileCount) named profiles · "
            + "\(report.summary.noticeCount) shared notices",
          systemImage: "person.2"
        )
      } else {
        Label("Up to five named profiles", systemImage: "person.2")
      }
    }
    .font(.subheadline.weight(.medium))
    .padding(.top, 2)
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
      RoundedRectangle(cornerRadius: 18, style: .continuous)
        .fill(Color(nsColor: .controlBackgroundColor))
        .shadow(color: .black.opacity(0.08), radius: 8, y: 3)
    )
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
        RoundedRectangle(cornerRadius: 22, style: .continuous)
          .fill(tint.opacity(0.08))
          .shadow(color: .black.opacity(0.07), radius: 10, y: 4)
      )
      .overlay {
        RoundedRectangle(cornerRadius: 22, style: .continuous)
          .stroke(tint.opacity(0.24), lineWidth: 1)
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
        RoundedRectangle(cornerRadius: 18, style: .continuous)
          .fill(Color(nsColor: .controlBackgroundColor))
          .shadow(color: .black.opacity(0.07), radius: 8, y: 3)
      )
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
      RoundedRectangle(cornerRadius: 18, style: .continuous)
        .fill(Color(nsColor: .controlBackgroundColor))
    )
  }
}

struct SectionHeading: View {
  let eyebrow: String
  let title: String
  let detail: String

  var body: some View {
    VStack(alignment: .leading, spacing: 4) {
      Text(eyebrow)
        .font(.caption2.weight(.bold))
        .foregroundStyle(.secondary)
        .tracking(1.1)
      Text(title).font(.title2.weight(.bold))
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
  }
}
