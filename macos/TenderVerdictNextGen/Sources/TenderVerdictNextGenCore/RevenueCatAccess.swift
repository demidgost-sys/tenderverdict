import Combine
import CryptoKit
import Foundation
@preconcurrency import RevenueCat

public enum TestStoreConfigurationStatus: Equatable, Sendable {
  case unavailableInRelease
  case missing
  case rejected
  case accepted
}

public enum RevenueCatTestStoreConfiguration {
  public static let environmentName = "REVENUECAT_TEST_STORE_API_KEY"

  public static var isAvailableInCurrentBuild: Bool {
    #if DEBUG
      true
    #else
      false
    #endif
  }

  public static func status(in environment: [String: String]) -> TestStoreConfigurationStatus {
    guard isAvailableInCurrentBuild else {
      return .unavailableInRelease
    }
    guard environment[environmentName] != nil else {
      return .missing
    }
    return apiKey(in: environment) == nil ? .rejected : .accepted
  }

  static func apiKey(in environment: [String: String]) -> String? {
    guard isAvailableInCurrentBuild else {
      return nil
    }
    guard let rawValue = environment[environmentName] else {
      return nil
    }
    let value = rawValue.trimmingCharacters(in: .whitespacesAndNewlines)
    let forbiddenCharacters = CharacterSet.whitespacesAndNewlines.union(.controlCharacters)
    guard value.hasPrefix("test_"),
      (12...512).contains(value.utf8.count),
      value.unicodeScalars.allSatisfy({ scalar in !forbiddenCharacters.contains(scalar) })
    else {
      return nil
    }
    return value
  }
}

public enum PremiumAccessState: Equatable, Sendable {
  case testStoreUnavailableInRelease
  case configurationMissing
  case configurationRejected
  case loading
  case locked(price: String?)
  case unlocked
  case cancelled(price: String?)
  case failed

  public var isUnlocked: Bool {
    self == .unlocked
  }

  public var isBusy: Bool {
    self == .loading
  }

  public var terminalAccessibilityOutcome: PremiumAccessAccessibilityOutcome? {
    switch self {
    case .testStoreUnavailableInRelease:
      return PremiumAccessAccessibilityOutcome(
        announcement:
          "RevenueCat Test Store is unavailable in this release-configuration build. "
          + "Use a Debug evaluation build for Test Store evidence.",
        recoveryActions: [],
        focusTarget: nil
      )
    case .configurationMissing:
      return PremiumAccessAccessibilityOutcome(
        announcement: "RevenueCat Test Store is not connected. Enter a Test Store API key.",
        recoveryActions: [.connectTestStore],
        focusTarget: .testStoreAPIKey
      )
    case .configurationRejected:
      return PremiumAccessAccessibilityOutcome(
        announcement:
          "RevenueCat Test Store key rejected. Use a key beginning with test underscore, "
          + "between 12 and 512 bytes, without spaces or control characters.",
        recoveryActions: [.connectTestStore],
        focusTarget: .testStoreAPIKey
      )
    case .loading:
      return nil
    case .locked(let price):
      if price == nil {
        return PremiumAccessAccessibilityOutcome(
          announcement:
            "Premium access is locked. The expected Test Store offering, monthly package, "
            + "or product is unavailable. Restore access or refresh the offering.",
          recoveryActions: [.restore, .refreshOffering],
          focusTarget: .restore
        )
      }
      return PremiumAccessAccessibilityOutcome(
        announcement:
          "Premium access is locked. A Test Store package is available. "
          + "You can purchase, restore, or refresh access.",
        recoveryActions: [.purchase, .restore, .refreshOffering],
        focusTarget: .purchase
      )
    case .unlocked:
      return PremiumAccessAccessibilityOutcome(
        announcement: "Portfolio Workspace unlocked. Premium access is active.",
        recoveryActions: [.restore],
        focusTarget: .restore
      )
    case .cancelled(let price):
      if price == nil {
        return PremiumAccessAccessibilityOutcome(
          announcement:
            "Test Store purchase cancelled. Premium access remains locked. "
            + "The expected package is unavailable; restore access or refresh the offering.",
          recoveryActions: [.restore, .refreshOffering],
          focusTarget: .restore
        )
      }
      return PremiumAccessAccessibilityOutcome(
        announcement:
          "Test Store purchase cancelled. Premium access remains locked. "
          + "You can retry the purchase, restore, or refresh access.",
        recoveryActions: [.purchase, .restore, .refreshOffering],
        focusTarget: .purchase
      )
    case .failed:
      return PremiumAccessAccessibilityOutcome(
        announcement: "Premium status could not be refreshed. Retry or restore access.",
        recoveryActions: [.retry, .restore],
        focusTarget: .retry
      )
    }
  }
}

public enum PremiumAccessRecoveryAction: Hashable, Sendable {
  case activateJudgeAccess
  case connectTestStore
  case purchase
  case refreshOffering
  case retry
  case restore
}

public enum PremiumAccessFocusTarget: Hashable, Sendable {
  case judgeAccessCode
  case testStoreAPIKey
  case purchase
  case refreshOffering
  case retry
  case restore
}

public struct PremiumAccessAccessibilityOutcome: Equatable, Sendable {
  public let announcement: String
  public let recoveryActions: [PremiumAccessRecoveryAction]
  public let focusTarget: PremiumAccessFocusTarget?

  public var primaryRecoveryAction: PremiumAccessRecoveryAction? {
    recoveryActions.first
  }

  public init(
    announcement: String,
    recoveryActions: [PremiumAccessRecoveryAction],
    focusTarget: PremiumAccessFocusTarget?
  ) {
    self.announcement = announcement
    self.recoveryActions = recoveryActions
    self.focusTarget = focusTarget
  }
}

public enum PremiumAccessSource: Equatable, Sendable {
  case testStore
  case judgeAccess(expiresAt: Date?)
  case otherRevenueCat
}

public enum JudgeAccessCodeValidation: Equatable, Sendable {
  case accepted(appUserID: String)
  case expired
  case invalid
}

public enum RevenueCatJudgeAccess {
  public static let expiresAt = Date(timeIntervalSince1970: 1_798_761_599)
  public static let expiryLabel = "December 31, 2026"

  public static func expirationLabel(
    for expirationDate: Date?,
    timeZone: TimeZone = .current
  ) -> String {
    guard let expirationDate else {
      return expiryLabel
    }
    let effectiveExpiration = min(expirationDate, expiresAt)
    let formatter = DateFormatter()
    formatter.calendar = Calendar(identifier: .gregorian)
    formatter.locale = Locale(identifier: "en_US_POSIX")
    formatter.timeZone = timeZone
    formatter.dateStyle = .long
    formatter.timeStyle = .none
    return formatter.string(from: effectiveExpiration)
  }

  private static let acceptedCodeDigests: Set<String> = [
    "0d6240bc8f3b8cd77a6457b5ce0330726077c60213e7c1373906051504108a26",
    "4e118a47833348f05045f3cf9146faf4ba095874cb1a922db81f99ae8384b3db",
    "6d64362bdfe7bafdde7f2c98b179ef320bc25d57ad5bb7f18eeb0c2d5bc69e2e",
    "ca472cf3cacdd4da8f2732e379c2843f5693b1aa763fd37889a68a9ca828128c",
    "fe56bfb274e8efe55aa5b7dd29830545e13e66a6a96900874d7e0bc1ee59b4e4",
  ]

  public static func validate(
    _ rawCode: String,
    now: Date = Date()
  ) -> JudgeAccessCodeValidation {
    guard now <= expiresAt else {
      return .expired
    }
    let code = rawCode.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
    guard (20...96).contains(code.utf8.count),
      code.unicodeScalars.allSatisfy({ scalar in
        scalar.isASCII
          && (CharacterSet.alphanumerics.contains(scalar) || scalar.value == 45)
      })
    else {
      return .invalid
    }
    let digest = digestHex(code)
    guard acceptedCodeDigests.contains(digest) else {
      return .invalid
    }
    return .accepted(appUserID: appUserID(forDigest: digest))
  }

  public static func isKnownAppUserID(_ appUserID: String) -> Bool {
    guard appUserID.hasPrefix("tvj_") else {
      return false
    }
    return acceptedCodeDigests.contains(String(appUserID.dropFirst(4)))
  }

  public static func appUserID(forDigest digest: String) -> String {
    "tvj_\(digest)"
  }

  public static func digestHex(_ value: String) -> String {
    SHA256.hash(data: Data(value.utf8))
      .map { String(format: "%02x", $0) }
      .joined()
  }
}

public enum JudgeAccessActivationState: Equatable, Sendable {
  case idle
  case checking
  case invalidCode
  case expired
  case entitlementMissing
  case failed
  case active(expiresAt: Date?)

  public var terminalAccessibilityOutcome: PremiumAccessAccessibilityOutcome? {
    switch self {
    case .idle, .checking:
      return nil
    case .invalidCode:
      return PremiumAccessAccessibilityOutcome(
        announcement: "Judge access code not recognized. Check the code and try again.",
        recoveryActions: [.activateJudgeAccess],
        focusTarget: .judgeAccessCode
      )
    case .expired:
      return PremiumAccessAccessibilityOutcome(
        announcement:
          "Hackathon Judge Access ended on \(RevenueCatJudgeAccess.expiryLabel).",
        recoveryActions: [],
        focusTarget: .judgeAccessCode
      )
    case .entitlementMissing:
      return PremiumAccessAccessibilityOutcome(
        announcement:
          "Judge access code recognized, but RevenueCat has no active granted entitlement. "
          + "Check the assigned code or refresh access.",
        recoveryActions: [.activateJudgeAccess, .refreshOffering],
        focusTarget: .judgeAccessCode
      )
    case .failed:
      return PremiumAccessAccessibilityOutcome(
        announcement: "Judge access could not be checked. Check the connection and try again.",
        recoveryActions: [.activateJudgeAccess],
        focusTarget: .judgeAccessCode
      )
    case .active(let expiresAt):
      return PremiumAccessAccessibilityOutcome(
        announcement:
          "RevenueCat Judge Access expires "
          + "\(RevenueCatJudgeAccess.expirationLabel(for: expiresAt)). "
          + "No purchase was made.",
        recoveryActions: [.restore],
        focusTarget: .restore
      )
    }
  }
}

@MainActor
public final class RevenueCatAccessController: ObservableObject {
  public nonisolated static let entitlementIdentifier = "supplier_profiles_plus"
  public nonisolated static let offeringIdentifier = "supplier_profiles_plus"
  public nonisolated static let packageIdentifier = "$rc_monthly"
  public nonisolated static let productIdentifier = "supplier_profiles_plus_monthly"

  @Published public private(set) var state: PremiumAccessState
  @Published public private(set) var accessSource: PremiumAccessSource? = nil
  @Published public private(set) var judgeAccessState: JudgeAccessActivationState = .idle

  private var apiKey: String?
  private var currentPackage: Package?
  private var didConfigure = false

  public init(environment: [String: String] = ProcessInfo.processInfo.environment) {
    apiKey = RevenueCatTestStoreConfiguration.apiKey(in: environment)
    switch RevenueCatTestStoreConfiguration.status(in: environment) {
    case .unavailableInRelease:
      state = .testStoreUnavailableInRelease
    case .missing:
      state = .configurationMissing
    case .rejected:
      state = .configurationRejected
    case .accepted:
      state = .loading
    }
  }

  public var canPurchase: Bool {
    currentPackage != nil && !state.isBusy
  }

  public var canRestore: Bool {
    didConfigure && !state.isBusy
  }

  public var canActivateJudgeAccess: Bool {
    didConfigure && !state.isBusy && judgeAccessState != .checking
  }

  public nonisolated static func isExpectedPackage(
    offeringIdentifier: String,
    packageIdentifier: String,
    productIdentifier: String
  ) -> Bool {
    offeringIdentifier == Self.offeringIdentifier
      && packageIdentifier == Self.packageIdentifier
      && productIdentifier == Self.productIdentifier
  }

  public nonisolated static func resolvedAccessSource(
    entitlementIsActive: Bool,
    store: Store,
    expirationDate: Date?,
    appUserID: String,
    now: Date = Date()
  ) -> PremiumAccessSource? {
    guard entitlementIsActive else {
      return nil
    }
    if store == .promotional {
      guard RevenueCatJudgeAccess.isKnownAppUserID(appUserID) else {
        return .otherRevenueCat
      }
      if now > RevenueCatJudgeAccess.expiresAt {
        return nil
      }
      let boundedExpiration = expirationDate.map { min($0, RevenueCatJudgeAccess.expiresAt) }
      return .judgeAccess(expiresAt: boundedExpiration)
    }
    if store == .testStore {
      return .testStore
    }
    return .otherRevenueCat
  }

  public func configure(testStoreAPIKey: String) async {
    guard RevenueCatTestStoreConfiguration.isAvailableInCurrentBuild else {
      apiKey = nil
      state = .testStoreUnavailableInRelease
      return
    }
    guard !didConfigure else {
      await refreshConfiguredAccess()
      return
    }
    let environment = [
      RevenueCatTestStoreConfiguration.environmentName: testStoreAPIKey
    ]
    guard let validatedKey = RevenueCatTestStoreConfiguration.apiKey(in: environment) else {
      apiKey = nil
      state = .configurationRejected
      return
    }
    apiKey = validatedKey
    state = .loading
    await start()
  }

  public func start() async {
    guard RevenueCatTestStoreConfiguration.isAvailableInCurrentBuild else {
      apiKey = nil
      state = .testStoreUnavailableInRelease
      return
    }
    guard let apiKey else {
      return
    }
    state = .loading
    if !didConfigure {
      guard !Purchases.isConfigured else {
        state = .failed
        return
      }
      Purchases.logLevel = .warn
      Purchases.configure(withAPIKey: apiKey)
      didConfigure = true
    }
    await refreshConfiguredAccess()
  }

  public func refresh() async {
    guard didConfigure else {
      await start()
      return
    }
    await refreshConfiguredAccess()
  }

  public func refreshIfConfigured() async {
    guard didConfigure, !state.isBusy else {
      return
    }
    await refreshConfiguredAccess()
  }

  public func purchaseCurrentPackage() async {
    guard let currentPackage, didConfigure else {
      state = .failed
      return
    }
    let price = currentPackage.localizedPriceString
    state = .loading
    do {
      let result = try await Purchases.shared.purchase(package: currentPackage)
      if result.userCancelled {
        state = .cancelled(price: price)
      } else if applyActiveAccess(result.customerInfo) {
        return
      } else {
        accessSource = nil
        state = .failed
      }
    } catch {
      accessSource = nil
      state = .failed
    }
  }

  public func restore() async {
    guard didConfigure else {
      state = .failed
      return
    }
    state = .loading
    do {
      let customerInfo = try await Purchases.shared.restorePurchases()
      if applyActiveAccess(customerInfo) {
        return
      }
      try await loadExpectedPackageAndLock()
    } catch {
      accessSource = nil
      state = .failed
    }
  }

  public func activateJudgeAccess(code: String, now: Date = Date()) async {
    guard didConfigure else {
      judgeAccessState = .failed
      return
    }
    switch RevenueCatJudgeAccess.validate(code, now: now) {
    case .invalid:
      judgeAccessState = .invalidCode
      return
    case .expired:
      judgeAccessState = .expired
      return
    case .accepted(let appUserID):
      judgeAccessState = .checking
      state = .loading
      do {
        let result = try await Purchases.shared.logIn(appUserID)
        if applyActiveAccess(result.customerInfo, now: now) {
          return
        }
        try await loadExpectedPackageAndLock(now: now)
      } catch {
        accessSource = nil
        judgeAccessState = .failed
        state = .failed
      }
    }
  }

  private func refreshConfiguredAccess() async {
    state = .loading
    do {
      let customerInfo = try await Purchases.shared.customerInfo(fetchPolicy: .fetchCurrent)
      if applyActiveAccess(customerInfo) {
        return
      }
      try await loadExpectedPackageAndLock()
    } catch {
      accessSource = nil
      state = .failed
    }
  }

  private func loadExpectedPackageAndLock(now: Date = Date()) async throws {
    let offerings = try await Purchases.shared.offerings()
    currentPackage = offerings.current.flatMap { offering in
      offering.availablePackages.first { package in
        Self.isExpectedPackage(
          offeringIdentifier: offering.identifier,
          packageIdentifier: package.identifier,
          productIdentifier: package.storeProduct.productIdentifier
        )
      }
    }
    accessSource = nil
    state = .locked(price: currentPackage?.localizedPriceString)
    if RevenueCatJudgeAccess.isKnownAppUserID(Purchases.shared.appUserID) {
      judgeAccessState =
        now > RevenueCatJudgeAccess.expiresAt ? .expired : .entitlementMissing
    } else if judgeAccessState == .checking {
      judgeAccessState = .entitlementMissing
    }
  }

  @discardableResult
  private func applyActiveAccess(
    _ customerInfo: CustomerInfo,
    now: Date = Date()
  ) -> Bool {
    guard let entitlement = customerInfo.entitlements[Self.entitlementIdentifier],
      let source = Self.resolvedAccessSource(
        entitlementIsActive: entitlement.isActive,
        store: entitlement.store,
        expirationDate: entitlement.expirationDate,
        appUserID: Purchases.shared.appUserID,
        now: now
      )
    else {
      return false
    }
    accessSource = source
    state = .unlocked
    if case .judgeAccess(let expiresAt) = source,
      RevenueCatJudgeAccess.isKnownAppUserID(Purchases.shared.appUserID)
    {
      judgeAccessState = .active(expiresAt: expiresAt)
    } else {
      judgeAccessState = .idle
    }
    return true
  }
}
