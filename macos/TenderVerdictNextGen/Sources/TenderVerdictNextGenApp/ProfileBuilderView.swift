import SwiftUI
import TenderVerdictNextGenCore

struct ProfileBuilderView: View {
  private struct DraftProfile: Identifiable {
    let id = UUID()
    var name: String
    var cpvCodes: String
    var countries: String
    var minimumDays: String

    init(profile: SupplierProfile) {
      name = profile.name
      cpvCodes = profile.cpvCodes.joined(separator: ", ")
      countries = profile.countries.joined(separator: ", ")
      minimumDays = String(profile.minimumDaysToDeadline)
    }

    init(name: String, cpvCodes: String, countries: String, minimumDays: Int) {
      self.name = name
      self.cpvCodes = cpvCodes
      self.countries = countries
      self.minimumDays = String(minimumDays)
    }
  }

  @Environment(\.dismiss) private var dismiss
  @State private var profiles: [DraftProfile]
  @State private var attemptedSave = false

  let externalError: String?
  let isSaving: Bool
  let onSave: (PortfolioWorkspaceDocument) -> Void

  init(
    document: PortfolioWorkspaceDocument?,
    externalError: String?,
    isSaving: Bool,
    onSave: @escaping (PortfolioWorkspaceDocument) -> Void
  ) {
    let values = document?.profiles.map(DraftProfile.init(profile:)) ?? Self.exampleProfiles
    _profiles = State(initialValue: values)
    self.externalError = externalError
    self.isSaving = isSaving
    self.onSave = onSave
  }

  var body: some View {
    VStack(spacing: 0) {
      header
      Divider()
      ScrollView {
        LazyVStack(alignment: .leading, spacing: 14) {
          ForEach(Array(profiles.enumerated()), id: \.element.id) { item in
            profileCard(index: item.offset)
          }
          if profiles.count < PortfolioWorkspaceDocument.maximumProfiles {
            Button {
              profiles.append(Self.blankProfile(number: profiles.count + 1))
            } label: {
              Label("Add profile", systemImage: "plus")
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
          }
        }
        .padding(24)
      }
      .disabled(isSaving)
      Divider()
      footer
    }
    .frame(minWidth: 680, minHeight: 640)
  }

  private var header: some View {
    HStack(alignment: .top, spacing: 16) {
      Image(systemName: "person.2.badge.gearshape")
        .font(.title2.weight(.semibold))
        .foregroundStyle(.indigo)
        .accessibilityHidden(true)
      VStack(alignment: .leading, spacing: 5) {
        Text("Build a supplier portfolio")
          .font(.title2.weight(.semibold))
        Text(
          "Create one to five named profiles. TenderVerdict validates every CPV and country "
            + "against its bundled authority tables before the workspace is saved."
        )
        .foregroundStyle(.secondary)
        .fixedSize(horizontal: false, vertical: true)
      }
      Spacer()
      Text("\(profiles.count) / \(PortfolioWorkspaceDocument.maximumProfiles)")
        .font(.subheadline.monospacedDigit().weight(.semibold))
        .foregroundStyle(.secondary)
        .accessibilityLabel("\(profiles.count) of 5 profiles")
    }
    .padding(24)
  }

  private var footer: some View {
    ViewThatFits(in: .horizontal) {
      HStack(spacing: 10) { footerContents }
      VStack(alignment: .leading, spacing: 10) { footerContents }
    }
    .padding(20)
  }

  @ViewBuilder
  private var footerContents: some View {
    if let externalError {
      Label(externalError, systemImage: "exclamationmark.triangle.fill")
        .font(.subheadline)
        .foregroundStyle(.orange)
        .fixedSize(horizontal: false, vertical: true)
    } else if attemptedSave, let error = validationMessage {
      Label(error, systemImage: "exclamationmark.triangle.fill")
        .font(.subheadline)
        .foregroundStyle(.orange)
        .fixedSize(horizontal: false, vertical: true)
    } else {
      Text("Names are unique without regard to case. Order is preserved in every report.")
        .font(.subheadline)
        .foregroundStyle(.secondary)
    }
    Spacer()
    Button("Reset example") {
      profiles = Self.exampleProfiles
      attemptedSave = false
    }
    .buttonStyle(.bordered)
    .disabled(isSaving)
    Button("Cancel") { dismiss() }
      .keyboardShortcut(.cancelAction)
      .disabled(isSaving)
    Button {
      attemptedSave = true
      guard let document = try? makeDocument() else { return }
      onSave(document)
    } label: {
      if isSaving {
        Label("Validating…", systemImage: "hourglass")
      } else {
        Label("Validate & Save As…", systemImage: "checkmark.shield")
      }
    }
    .buttonStyle(.borderedProminent)
    .keyboardShortcut(.defaultAction)
    .disabled(isSaving)
  }

  private func profileCard(index: Int) -> some View {
    let binding = $profiles[index]
    return VStack(alignment: .leading, spacing: 14) {
      ViewThatFits(in: .horizontal) {
        HStack(spacing: 10) { cardHeader(index: index) }
        VStack(alignment: .leading, spacing: 10) { cardHeader(index: index) }
      }

      Grid(alignment: .leading, horizontalSpacing: 14, verticalSpacing: 12) {
        GridRow {
          fieldLabel("Profile name", image: "person.text.rectangle")
          TextField("Example Austria Services", text: binding.name)
            .textFieldStyle(.roundedBorder)
            .accessibilityLabel("Profile \(index + 1) name")
        }
        GridRow {
          fieldLabel("CPV codes", image: "number.square")
          TextField("72260000, 72261000", text: binding.cpvCodes)
            .textFieldStyle(.roundedBorder)
            .accessibilityLabel("Profile \(index + 1) CPV codes")
        }
        GridRow {
          fieldLabel("Countries", image: "globe.europe.africa")
          TextField("AUT, DEU", text: binding.countries)
            .textFieldStyle(.roundedBorder)
            .accessibilityLabel("Profile \(index + 1) three-letter country codes")
        }
        GridRow {
          fieldLabel("Minimum lead time", image: "calendar.badge.clock")
          HStack(spacing: 8) {
            TextField("14", text: binding.minimumDays)
              .textFieldStyle(.roundedBorder)
              .frame(maxWidth: 110)
              .accessibilityLabel("Profile \(index + 1) minimum days to deadline")
            Text("days")
              .foregroundStyle(.secondary)
          }
        }
      }

      if attemptedSave, let error = profileValidationMessage(at: index) {
        Label(error, systemImage: "exclamationmark.circle")
          .font(.caption)
          .foregroundStyle(.orange)
      }
    }
    .padding(18)
    .background(
      RoundedRectangle(cornerRadius: 18, style: .continuous)
        .fill(Color(nsColor: .controlBackgroundColor))
    )
    .overlay {
      RoundedRectangle(cornerRadius: 18, style: .continuous)
        .stroke(Color.primary.opacity(0.09), lineWidth: 1)
    }
  }

  @ViewBuilder
  private func cardHeader(index: Int) -> some View {
    Text("Profile \(index + 1)")
      .font(.headline)
    Spacer()
    Button {
      profiles.swapAt(index, index - 1)
    } label: {
      Image(systemName: "arrow.up")
    }
    .disabled(index == 0)
    .accessibilityLabel("Move profile \(index + 1) up")
    Button {
      profiles.swapAt(index, index + 1)
    } label: {
      Image(systemName: "arrow.down")
    }
    .disabled(index == profiles.count - 1)
    .accessibilityLabel("Move profile \(index + 1) down")
    Button(role: .destructive) {
      profiles.remove(at: index)
    } label: {
      Label("Remove", systemImage: "trash")
    }
    .disabled(profiles.count == 1)
    .accessibilityLabel("Remove profile \(index + 1)")
  }

  private func fieldLabel(_ title: String, image: String) -> some View {
    Label(title, systemImage: image)
      .font(.subheadline.weight(.semibold))
      .frame(width: 150, alignment: .leading)
  }

  private var validationMessage: String? {
    do {
      _ = try makeDocument()
      return nil
    } catch let error as LocalizedError {
      return error.errorDescription ?? "Review the profile values and try again."
    } catch {
      return "Review the profile values and try again."
    }
  }

  private func profileValidationMessage(at index: Int) -> String? {
    do {
      _ = try makeProfile(from: profiles[index])
      return nil
    } catch {
      return
        "Use a name, one or more 8-digit CPV codes, one or more 3-letter countries, and 0–3650 days."
    }
  }

  private func makeDocument() throws -> PortfolioWorkspaceDocument {
    try PortfolioWorkspaceDocument(profiles: profiles.map(makeProfile(from:)))
  }

  private func makeProfile(from draft: DraftProfile) throws -> SupplierProfile {
    guard let minimumDays = Int(draft.minimumDays.trimmingCharacters(in: .whitespacesAndNewlines))
    else {
      throw WorkspaceDocumentError.invalidProfile
    }
    return try SupplierProfile(
      name: draft.name.trimmingCharacters(in: .whitespacesAndNewlines),
      cpvCodes: Self.tokens(from: draft.cpvCodes),
      countries: Self.tokens(from: draft.countries).map { $0.uppercased() },
      minimumDaysToDeadline: minimumDays
    )
  }

  private static func tokens(from value: String) -> [String] {
    var seen = Set<String>()
    return
      value
      .components(separatedBy: CharacterSet(charactersIn: ",;\n\t "))
      .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
      .filter { !$0.isEmpty && seen.insert($0).inserted }
  }

  private static let exampleProfiles = [
    DraftProfile(
      name: "Example Austria Services",
      cpvCodes: "72260000",
      countries: "AUT",
      minimumDays: 14
    ),
    DraftProfile(
      name: "DACH Software Delivery",
      cpvCodes: "72261000",
      countries: "AUT, DEU",
      minimumDays: 10
    ),
    DraftProfile(
      name: "Alpine Facilities",
      cpvCodes: "50700000",
      countries: "AUT",
      minimumDays: 21
    ),
  ]

  private static func blankProfile(number: Int) -> DraftProfile {
    DraftProfile(
      name: "Profile \(number)",
      cpvCodes: "72260000",
      countries: "AUT",
      minimumDays: 14
    )
  }
}
