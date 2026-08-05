import SwiftUI
import TenderVerdictNextGenCore

struct ComparisonSelection: Identifiable {
  struct ID: Hashable {
    let profileID: String
    let resultID: NoticeIdentity
  }

  let profileID: String
  let resultID: NoticeIdentity

  var id: ID { ID(profileID: profileID, resultID: resultID) }
}

struct ComparisonDetailView: View {
  @Environment(\.dismiss) private var dismiss

  let report: PortfolioWorkspaceReport
  let selection: ComparisonSelection

  private var profile: ProfileReport? {
    report.profileReport(id: selection.profileID)
  }

  private var result: QualificationResult? {
    report.result(profileID: selection.profileID, resultID: selection.resultID)
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 0) {
      if let profile, let result {
        ScrollView {
          VStack(alignment: .leading, spacing: 20) {
            header(profile: profile, result: result)
            Divider()
            detailGroup(title: "Recommended next step", values: [result.displayHumanNextStep])
            detailGroup(title: "Reasons", values: result.displayReasons)
            detailGroup(
              title: "Unknowns",
              values: result.unknowns.isEmpty
                ? ["None from the supplied metadata."]
                : result.displayUnknowns
            )
            if let sourceURL = result.safeSourceURL {
              Link(destination: sourceURL) {
                Label("Open supplied HTTPS source", systemImage: "arrow.up.right.square")
              }
              .buttonStyle(.bordered)
            }
          }
          .padding(24)
        }
      } else {
        NoticeCard(
          title: "This comparison is no longer available",
          detail: "Close the detail and choose another verdict cell.",
          systemImage: "exclamationmark.triangle",
          tint: .orange
        )
        .padding(24)
      }
      Divider()
      HStack {
        Spacer()
        Button("Done") { dismiss() }
          .keyboardShortcut(.defaultAction)
          .buttonStyle(.borderedProminent)
      }
      .padding(18)
    }
    .frame(minWidth: 560, minHeight: 480)
  }

  private func header(profile: ProfileReport, result: QualificationResult) -> some View {
    VStack(alignment: .leading, spacing: 10) {
      Text(profile.profile.displayName)
        .font(.subheadline.weight(.semibold))
        .foregroundStyle(.indigo)
      Text(result.displayTitle)
        .font(.title2.weight(.semibold))
        .fixedSize(horizontal: false, vertical: true)
      ViewThatFits(in: .horizontal) {
        HStack(spacing: 12) { headerMetadata(result) }
        VStack(alignment: .leading, spacing: 8) { headerMetadata(result) }
      }
    }
  }

  @ViewBuilder
  private func headerMetadata(_ result: QualificationResult) -> some View {
    VerdictBadge(verdict: result.verdict)
    Label(result.displayReference, systemImage: "number")
    Label(result.displayBuyer, systemImage: "building.2")
    Label(result.displayDeadline, systemImage: "calendar")
  }

  private func detailGroup(title: String, values: [String]) -> some View {
    VStack(alignment: .leading, spacing: 9) {
      Text(title)
        .font(.headline)
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
