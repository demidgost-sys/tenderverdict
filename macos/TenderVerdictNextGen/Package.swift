// swift-tools-version: 6.0

import PackageDescription

let package = Package(
  name: "TenderVerdictNextGen",
  platforms: [
    .macOS(.v13)
  ],
  products: [
    .executable(name: "TenderVerdictNextGen", targets: ["TenderVerdictNextGenApp"]),
    .executable(
      name: "TenderVerdictNextGenChecks",
      targets: ["TenderVerdictNextGenChecks"]
    ),
  ],
  dependencies: [
    .package(
      url: "https://github.com/RevenueCat/purchases-ios.git",
      exact: "5.83.0"
    )
  ],
  targets: [
    .target(
      name: "TenderVerdictNextGenCore",
      dependencies: [
        .product(name: "RevenueCat", package: "purchases-ios")
      ]
    ),
    .executableTarget(
      name: "TenderVerdictNextGenApp",
      dependencies: ["TenderVerdictNextGenCore"]
    ),
    .executableTarget(
      name: "TenderVerdictNextGenChecks",
      dependencies: ["TenderVerdictNextGenCore"],
      path: "Tests/TenderVerdictNextGenCoreTests"
    ),
  ]
)
