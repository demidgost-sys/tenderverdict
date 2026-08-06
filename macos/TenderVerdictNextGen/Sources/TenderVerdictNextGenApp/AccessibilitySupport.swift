import AppKit
import TenderVerdictNextGenCore

@MainActor
enum PremiumAccessibilityAnnouncer {
  static func post(_ outcome: PremiumAccessAccessibilityOutcome?) {
    guard let outcome,
      NSWorkspace.shared.isVoiceOverEnabled,
      let window = NSApplication.shared.keyWindow ?? NSApplication.shared.mainWindow,
      window.isVisible,
      let contentView = window.contentView
    else {
      return
    }

    NSAccessibility.post(
      element: contentView,
      notification: .announcementRequested,
      userInfo: [
        .announcement: outcome.announcement,
        .priority: NSAccessibilityPriorityLevel.medium.rawValue,
      ]
    )
  }
}
