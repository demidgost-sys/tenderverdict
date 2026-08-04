import SwiftUI
import TenderVerdictNextGenCore

struct NoticeImportPreviewView: View {
  let preview: NoticeImportPreview

  var body: some View {
    VStack(alignment: .leading, spacing: 14) {
      ViewThatFits(in: .horizontal) {
        HStack(alignment: .firstTextBaseline, spacing: 16) { previewHeader }
        VStack(alignment: .leading, spacing: 6) { previewHeader }
      }

      if preview.noticeCount == 0 {
        Label("The file is valid and contains no notices.", systemImage: "tray")
          .foregroundStyle(.secondary)
      } else {
        VStack(spacing: 0) {
          ForEach(Array(preview.preview.enumerated()), id: \.element.id) { item in
            previewRow(item.element)
            if item.offset < preview.preview.count - 1 {
              Divider()
            }
          }
        }
      }

      if !missingFields.isEmpty {
        VStack(alignment: .leading, spacing: 7) {
          Text("Metadata gaps in the full file")
            .font(.caption.weight(.semibold))
            .foregroundStyle(.secondary)
          ViewThatFits(in: .horizontal) {
            HStack(spacing: 8) { missingFieldBadges }
            VStack(alignment: .leading, spacing: 7) { missingFieldBadges }
          }
        }
      }
    }
    .padding(16)
    .background(
      RoundedRectangle(cornerRadius: 16, style: .continuous)
        .fill(Color(nsColor: .textBackgroundColor).opacity(0.55))
    )
    .overlay {
      RoundedRectangle(cornerRadius: 16, style: .continuous)
        .stroke(Color.green.opacity(0.18), lineWidth: 1)
    }
    .accessibilityElement(children: .contain)
  }

  @ViewBuilder
  private var previewHeader: some View {
    Label("Import ready", systemImage: "checkmark.seal.fill")
      .font(.headline)
      .foregroundStyle(.green)
    Spacer()
    Text("\(preview.noticeCount) notices · \(sourceLabel)")
      .font(.subheadline.monospacedDigit())
      .foregroundStyle(.secondary)
  }

  private func previewRow(_ record: NoticeImportRecord) -> some View {
    HStack(alignment: .top, spacing: 12) {
      VStack(alignment: .leading, spacing: 4) {
        Text(displayTitle(record))
          .font(.subheadline.weight(.semibold))
          .lineLimit(2)
        Text(referenceLabel(record))
          .font(.caption.monospaced())
          .foregroundStyle(.tertiary)
      }
      .frame(maxWidth: .infinity, alignment: .leading)
      VStack(alignment: .trailing, spacing: 4) {
        Text(displayBuyer(record))
          .lineLimit(1)
        Text(record.deadlineAt ?? record.deadline ?? "No deadline")
          .foregroundStyle(.secondary)
      }
      .font(.caption)
      .frame(maxWidth: 230, alignment: .trailing)
      if !record.metadataWarnings.isEmpty {
        Image(systemName: "exclamationmark.triangle.fill")
          .foregroundStyle(.orange)
          .help(record.metadataWarnings.joined(separator: "\n"))
          .accessibilityLabel(record.metadataWarnings.joined(separator: ". "))
      }
    }
    .padding(.vertical, 9)
    .accessibilityElement(children: .combine)
  }

  @ViewBuilder
  private var missingFieldBadges: some View {
    ForEach(missingFields, id: \.name) { item in
      Text("\(item.name): \(item.count)")
        .font(.caption.monospacedDigit().weight(.medium))
        .padding(.horizontal, 9)
        .padding(.vertical, 5)
        .background(
          Capsule(style: .continuous)
            .fill(Color.orange.opacity(0.10))
        )
        .accessibilityLabel("\(item.name) missing in \(item.count) notices")
    }
  }

  private var missingFields: [(name: String, count: Int)] {
    let counts = preview.missingFieldCounts
    return [
      ("Type", counts.noticeType),
      ("Title", counts.title),
      ("Buyer", counts.buyer),
      ("CPV", counts.cpvCodes),
      ("Country", counts.countries),
      ("Deadline", counts.deadline),
      ("Source", counts.sourceURL),
    ].filter { $0.count > 0 }
  }

  private var sourceLabel: String {
    switch preview.sourceKind {
    case "local_csv":
      return "CSV"
    case "local_json":
      return "JSON"
    case "ted_search_api":
      return "TED snapshot"
    default:
      return preview.sourceKind
    }
  }

  private func displayTitle(_ record: NoticeImportRecord) -> String {
    let title = record.title?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
    return title.isEmpty ? "Untitled notice" : title
  }

  private func displayBuyer(_ record: NoticeImportRecord) -> String {
    let buyer = record.buyer?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
    return buyer.isEmpty ? "Buyer not supplied" : buyer
  }

  private func referenceLabel(_ record: NoticeImportRecord) -> String {
    guard let lotID = record.lotID, !lotID.isEmpty else {
      return record.publicationNumber
    }
    return "\(record.publicationNumber) / \(lotID)"
  }
}
