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

      if !visibleWarnings.isEmpty {
        DisclosureGroup {
          VStack(alignment: .leading, spacing: 7) {
            ForEach(Array(visibleWarnings.enumerated()), id: \.offset) { item in
              Label(item.element, systemImage: "exclamationmark.triangle")
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
            }
          }
          .padding(.top, 6)
        } label: {
          Label(
            "\(visibleWarnings.count) metadata warning"
              + (visibleWarnings.count == 1 ? " in preview" : "s in preview"),
            systemImage: "exclamationmark.triangle.fill"
          )
          .font(.caption.weight(.semibold))
          .foregroundStyle(.orange)
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
        Text(record.displayTitle)
          .font(.subheadline.weight(.semibold))
          .lineLimit(2)
        Text(record.displayReference)
          .font(.caption.monospaced())
          .foregroundStyle(.tertiary)
      }
      .frame(maxWidth: .infinity, alignment: .leading)
      VStack(alignment: .trailing, spacing: 4) {
        Text(record.displayBuyer)
          .lineLimit(1)
        Text(record.displayDeadline)
          .foregroundStyle(.secondary)
      }
      .font(.caption)
      .frame(maxWidth: 230, alignment: .trailing)
      if !record.metadataWarnings.isEmpty {
        Image(systemName: "exclamationmark.triangle.fill")
          .foregroundStyle(.orange)
          .help(record.displayMetadataWarnings.joined(separator: "\n"))
          .accessibilityLabel(record.displayMetadataWarnings.joined(separator: ". "))
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

  private var visibleWarnings: [String] {
    preview.preview.flatMap { record in
      record.displayMetadataWarnings.map { warning in
        "\(record.displayReference): \(warning)"
      }
    }
  }

}
