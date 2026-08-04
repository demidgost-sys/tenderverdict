import Foundation

public enum DeadlinePresenceFilter: String, CaseIterable, Identifiable, Sendable {
  case any
  case supplied
  case missing

  public var id: String { rawValue }
}

public struct ReviewQuery: Equatable, Sendable {
  public var searchText: String
  public var buyerText: String
  public var deadlinePresence: DeadlinePresenceFilter

  public init(
    searchText: String = "",
    buyerText: String = "",
    deadlinePresence: DeadlinePresenceFilter = .any
  ) {
    self.searchText = searchText
    self.buyerText = buyerText
    self.deadlinePresence = deadlinePresence
  }

  public func apply(to results: [QualificationResult]) -> [QualificationResult] {
    let searchTerms = normalizedSearchText(searchText).split(whereSeparator: \.isWhitespace).map(
      String.init
    )
    let buyerTerm = normalizedSearchText(buyerText)
    return results.filter { result in
      let searchable = normalizedSearchText(
        [result.publicationNumber, result.lotID, result.title, result.buyer]
          .compactMap { $0 }
          .joined(separator: "\n")
      )
      let buyer = normalizedSearchText(result.buyer ?? "")
      let hasDeadline = [result.deadline, result.deadlineAt]
        .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
        .contains { !$0.isEmpty }

      guard searchTerms.allSatisfy({ searchable.contains($0) }),
        buyerTerm.isEmpty || buyer == buyerTerm
      else {
        return false
      }
      switch deadlinePresence {
      case .any:
        return true
      case .supplied:
        return hasDeadline
      case .missing:
        return !hasDeadline
      }
    }
  }
}

extension PortfolioWorkspaceReport {
  public func profileReport(id: String) -> ProfileReport? {
    profileReports.first { $0.id == id }
  }

  public func result(profileID: String, resultID: NoticeIdentity) -> QualificationResult? {
    profileReport(id: profileID)?.results.first { $0.id == resultID }
  }
}
