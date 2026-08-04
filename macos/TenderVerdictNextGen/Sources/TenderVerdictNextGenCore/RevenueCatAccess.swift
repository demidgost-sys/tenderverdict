import Combine
import Foundation
@preconcurrency import RevenueCat

public enum TestStoreConfigurationStatus: Equatable, Sendable {
  case missing
  case rejected
  case accepted
}

public enum RevenueCatTestStoreConfiguration {
  public static let environmentName = "REVENUECAT_TEST_STORE_API_KEY"

  public static func status(in environment: [String: String]) -> TestStoreConfigurationStatus {
    guard environment[environmentName] != nil else {
      return .missing
    }
    return apiKey(in: environment) == nil ? .rejected : .accepted
  }

  static func apiKey(in environment: [String: String]) -> String? {
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
}

@MainActor
public final class RevenueCatAccessController: ObservableObject {
  public static let entitlementIdentifier = "supplier_profiles_plus"

  @Published public private(set) var state: PremiumAccessState

  private var apiKey: String?
  private var currentPackage: Package?
  private var didConfigure = false

  public init(environment: [String: String] = ProcessInfo.processInfo.environment) {
    apiKey = RevenueCatTestStoreConfiguration.apiKey(in: environment)
    switch RevenueCatTestStoreConfiguration.status(in: environment) {
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

  public func configure(testStoreAPIKey: String) async {
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
      } else if Self.hasPremiumAccess(result.customerInfo) {
        state = .unlocked
      } else {
        state = .failed
      }
    } catch {
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
      state =
        Self.hasPremiumAccess(customerInfo)
        ? .unlocked
        : .locked(price: currentPackage?.localizedPriceString)
    } catch {
      state = .failed
    }
  }

  private func refreshConfiguredAccess() async {
    state = .loading
    do {
      let customerInfo = try await Purchases.shared.customerInfo()
      if Self.hasPremiumAccess(customerInfo) {
        currentPackage = nil
        state = .unlocked
        return
      }
      let offerings = try await Purchases.shared.offerings()
      currentPackage = offerings.current?.availablePackages.first
      state = .locked(price: currentPackage?.localizedPriceString)
    } catch {
      state = .failed
    }
  }

  private static func hasPremiumAccess(_ customerInfo: CustomerInfo) -> Bool {
    customerInfo.entitlements[entitlementIdentifier]?.isActive == true
  }
}
