import Foundation
import TenderVerdictNextGenCore

enum CheckFailure: Error, LocalizedError {
  case failed(String)

  var errorDescription: String? {
    switch self {
    case .failed(let message):
      return message
    }
  }
}

@main
enum TenderVerdictNextGenChecks {
  static func main() async throws {
    try checkPortfolioContractPreservesFreeAndPremiumSurfaces()
    try checkPortfolioContractPreservesResultDetails()
    try checkShareableReviewBriefRespectsAccessAndEscapesContent()
    try checkDisplayTextMakesControlsVisible()
    try checkVerdictPresentationHelpers()
    try checkReviewPointValidation()
    try checkPortfolioContractAcceptsEmptyNoticeSet()
    try checkPortfolioContractRejectsInconsistentProfileCount()
    try checkPortfolioContractRejectsDifferentNoticeDigests()
    try checkPortfolioContractRejectsDifferentNoticeOrder()
    try checkPortfolioContractRejectsInvalidNestedTotals()
    try checkPortfolioContractRejectsResultSummaryMismatch()
    try checkWorkspaceDocumentIsStrictBoundedAndDeterministic()
    try checkNoticeImportPreviewContract()
    try checkReviewQueryAndStableResultLookup()
    try checkLargeReviewQueryPreservesStableIdentities()
    try checkJudgeAccessAndExpiryTransitions()
    try checkPremiumAccessibilityOutcomes()
    try await checkTestStoreConfigurationFailsClosed()
    try checkProcessAdapterPreservesDeterministicBytes()
    print("NEXT_GEN_CHECKS_OK checks=20")
  }

  private static func checkPortfolioContractPreservesFreeAndPremiumSurfaces() throws {
    let firstProfileName = "München\u{7f} Services"
    let report = try PortfolioWorkspaceReport.decode(
      makeReportData(profileCount: 3, firstProfileName: firstProfileName)
    )

    try require(report.schemaVersion == 1, "workspace schema was not preserved")
    try require(report.summary.profileCount == 3, "profile count was not preserved")
    try require(report.summary.noticeCount == 3, "notice count was not preserved")
    try require(
      report.visibleProfileReports(premiumUnlocked: false).map(\.profile.name),
      equals: [firstProfileName],
      "free projection exposed more than one profile"
    )
    try require(
      report.visibleProfileReports(premiumUnlocked: true).map(\.profile.name),
      equals: [firstProfileName, "Profile 2", "Profile 3"],
      "premium projection did not preserve profile order"
    )

    let firstFreeExport = try report.profileReports[0].deterministicJSONData()
    let secondFreeExport = try report.profileReports[0].deterministicJSONData()
    try require(firstFreeExport == secondFreeExport, "free export bytes were not deterministic")
    try require(
      firstFreeExport.allSatisfy { $0 < 0x80 },
      "free export was not ASCII-safe"
    )
    try require(!firstFreeExport.contains(0x7f), "free export contained raw DEL")
    let exported = try requireDictionary(firstFreeExport, "free export was not a JSON object")
    try require(exported["schema_version"] as? Int == 3, "free export changed report schema")
    try require(exported["profile_reports"] == nil, "free export exposed the portfolio envelope")
    let exportedProfile = exported["profile"] as? [String: Any]
    try require(
      exportedProfile?["name"] as? String == firstProfileName,
      "free export changed the first profile"
    )
    let exportedProvenance = exported["provenance"] as? [String: Any]
    let exportedGenerator = exportedProvenance?["generator"] as? [String: Any]
    try require(
      exportedGenerator?["name"] as? String == "TenderVerdict"
        && exportedGenerator?["version"] as? String == "0.2.0a1"
        && exportedProvenance?["source_kind"] as? String == "ted_api"
        && exportedProvenance?["ted_query"] as? String == "fixture query"
        && exportedProvenance?["retrieved_at"] as? String == "2026-08-02T10:00:00Z"
        && exportedProvenance?["lot_policy"] as? String == "verified_lots",
      "free export dropped schema-3 provenance"
    )
  }

  private static func checkPortfolioContractRejectsInconsistentProfileCount() throws {
    let data = try makeReportData(profileCount: 2, declaredProfileCount: 3)
    try requireContractError(.inconsistentProfileCount, data: data)
  }

  private static func checkPortfolioContractPreservesResultDetails() throws {
    let report = try PortfolioWorkspaceReport.decode(makeReportData(profileCount: 1))
    let result = try requireFirst(report.profileReports[0].results, "result details were omitted")

    try require(result.publicationNumber == "SYN-OPEN-001", "publication number changed")
    try require(result.title == "Application maintenance services", "title changed")
    try require(result.verdict == .openDocuments, "verdict changed")
    try require(result.reasons.count == 2, "reasons changed")
    try require(result.unknowns.isEmpty, "unknowns changed")
    try require(result.safeSourceURL != nil, "safe source URL was rejected")
    try require(
      result.humanNextStep == "Open and review the official procurement documents.",
      "human next step changed"
    )

    for sourceURL in [
      "https://procurement.example/white space",
      "https://procurement.example/line\nbreak",
      "https://procurement.example/tab\tvalue",
      "https://procurement.example/control\u{1}",
      "https://procurement.example/del\u{7f}value",
      "https://procurement.example/bidi\u{202e}value",
    ] {
      let unsafe = try PortfolioWorkspaceReport.decode(
        makeReportData(profileCount: 1, firstSourceURL: sourceURL)
      )
      let unsafeResult = try requireFirst(
        unsafe.profileReports[0].results,
        "unsafe URL fixture omitted its result"
      )
      try require(unsafeResult.safeSourceURL == nil, "unsafe URL became an active link")
    }
  }

  private static func checkShareableReviewBriefRespectsAccessAndEscapesContent() throws {
    let firstProfileName = "Profile <script>alert(\"x\")</script>\n\u{202e}"
    let report = try PortfolioWorkspaceReport.decode(
      makeReportData(profileCount: 3, firstProfileName: firstProfileName)
    )

    let freeBrief = try report.shareableReviewBriefHTMLData(premiumUnlocked: false)
    let repeatedFreeBrief = try report.shareableReviewBriefHTMLData(premiumUnlocked: false)
    let premiumBrief = try report.shareableReviewBriefHTMLData(premiumUnlocked: true)
    let freeHTML = String(decoding: freeBrief, as: UTF8.self)
    let premiumHTML = String(decoding: premiumBrief, as: UTF8.self)

    try require(freeBrief == repeatedFreeBrief, "review brief bytes were not deterministic")
    try require(freeBrief.last == 0x0a, "review brief did not end with one newline")
    try require(freeHTML.hasPrefix("<!doctype html>"), "review brief omitted its doctype")
    try require(
      freeHTML.contains("default-src 'none'; style-src 'unsafe-inline'"),
      "review brief omitted its restrictive content security policy"
    )
    try require(
      freeHTML.contains("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; \\u202e"),
      "review brief did not escape or expose unsafe profile display text"
    )
    try require(
      !freeHTML.lowercased().contains("<script"),
      "review brief allowed injected script markup"
    )
    try require(freeHTML.contains("First profile review"), "free brief did not label its scope")
    try require(
      freeHTML.contains("Application maintenance services")
        && freeHTML.contains("Software support services")
        && freeHTML.contains("Software implementation services"),
      "free brief omitted first-profile notices"
    )
    guard let openNotice = freeHTML.range(of: "Application maintenance services"),
      let watchNotice = freeHTML.range(of: "Software support services"),
      let rejectNotice = freeHTML.range(of: "Software implementation services")
    else {
      throw CheckFailure.failed("free brief omitted ordered notice content")
    }
    try require(
      openNotice.lowerBound < watchNotice.lowerBound
        && watchNotice.lowerBound < rejectNotice.lowerBound,
      "review brief changed notice order"
    )
    try require(
      !freeHTML.contains("Profile 2") && !freeHTML.contains("Profile 3"),
      "free brief exposed gated profile content"
    )
    try require(
      freeHTML.contains(
        "href=\"https://procurement.example/notices/SYN-OPEN-001\""
      ),
      "review brief omitted a validated HTTPS source link"
    )
    try require(
      premiumHTML.contains("Complete portfolio review"),
      "premium brief did not label its complete scope"
    )
    guard let secondProfile = premiumHTML.range(of: "Profile 2"),
      let thirdProfile = premiumHTML.range(of: "Profile 3")
    else {
      throw CheckFailure.failed("premium brief omitted profile content")
    }
    try require(
      secondProfile.lowerBound < thirdProfile.lowerBound,
      "premium brief changed profile order"
    )
    for forbidden in ["score", "ranking", "recommendation"] {
      try require(
        !premiumHTML.lowercased().contains(forbidden),
        "review brief added forbidden cross-profile language: \(forbidden)"
      )
    }

    let unsafeReport = try PortfolioWorkspaceReport.decode(
      makeReportData(
        profileCount: 1,
        firstSourceURL: "https://procurement.example/line\nbreak"
      )
    )
    let unsafeHTML = String(
      decoding: try unsafeReport.shareableReviewBriefHTMLData(premiumUnlocked: false),
      as: UTF8.self
    )
    try require(
      unsafeHTML.contains("No verified HTTPS link supplied")
        && !unsafeHTML.contains("https://procurement.example/line"),
      "review brief exposed an unsafe source URL"
    )

    let emptyReport = try PortfolioWorkspaceReport.decode(
      makeReportData(profileCount: 2, noticeCount: 0)
    )
    let emptyHTML = String(
      decoding: try emptyReport.shareableReviewBriefHTMLData(premiumUnlocked: true),
      as: UTF8.self
    )
    try require(
      emptyHTML.contains("No notices were included at this review point."),
      "review brief omitted its empty-notice state"
    )
  }

  private static func checkDisplayTextMakesControlsVisible() throws {
    try require(
      normalizedDisplayText(" A\r\n\tB\u{1}\u{7f}\u{85}\u{202e}C ")
        == "A B\\u0001\\u007f\\u0085\\u202eC",
      "display normalization did not expose control and bidi characters"
    )
    try require(
      normalizedDisplayText("München 👩🏽‍💻") == "München 👩🏽\\u200d💻",
      "display normalization did not preserve ordinary Unicode or expose joiner formatting"
    )

    let report = try PortfolioWorkspaceReport.decode(
      makeReportData(profileCount: 1, firstProfileName: "München\u{7f} Services")
    )
    try require(
      report.profileReports[0].profile.displayName == "München\\u007f Services",
      "profile display text exposed a raw DEL character"
    )
  }

  private static func checkVerdictPresentationHelpers() throws {
    let report = try PortfolioWorkspaceReport.decode(makeReportData(profileCount: 1))
    let openResult = report.profileReports[0].results[0]
    let watchResult = report.profileReports[0].results[1]

    try require(
      openResult.displayVerdictDrivers.isEmpty,
      "routine positive checks were shown as verdict drivers"
    )
    try require(
      openResult.displaySupportingChecks == [
        "Exact CPV match: 72260000.", "Country match: AUT.",
      ],
      "positive checks were not preserved"
    )
    try require(
      watchResult.displayVerdictDrivers == ["Broader CPV class match."],
      "watch driver was hidden among supporting checks"
    )
    try require(
      watchResult.displayUnknowns == ["Confirm the exact procurement scope."],
      "watch unknowns changed"
    )
  }

  private static func checkReviewPointValidation() throws {
    for value in [
      "2026-08-02",
      "2026-08-02T12:30:00Z",
      "2026-08-02T12:30:00+02:00",
    ] {
      try require(
        ReviewPointInputValidator.validationMessage(for: value) == nil,
        "valid review point was rejected: \(value)"
      )
    }
    for value in [
      "",
      "2026-02-30",
      "2026-8-2",
      "2026-02-30T12:30:00Z",
      "2026-08-02 12:30:00Z",
      "2026-08-02T12:30:00",
      "2026-08-02T12:30:00.000Z",
      "2026-08-02T25:30:00+02:00",
      "2026-08-02T12:30:00+24:00",
    ] {
      try require(
        ReviewPointInputValidator.validationMessage(for: value)
          == ReviewPointInputValidator.guidance,
        "invalid review point was accepted: \(value)"
      )
    }
    try require(
      ReviewPointInputValidator.todayString(
        referenceDate: Date(timeIntervalSince1970: 0),
        timeZone: TimeZone(secondsFromGMT: 0)!
      ) == "1970-01-01",
      "today shortcut changed calendar or time-zone semantics"
    )
  }

  private static func checkPortfolioContractAcceptsEmptyNoticeSet() throws {
    let report = try PortfolioWorkspaceReport.decode(
      makeReportData(profileCount: 2, noticeCount: 0)
    )
    try require(report.summary.noticeCount == 0, "empty notice count changed")
    try require(
      report.profileReports.allSatisfy { profile in
        profile.results.isEmpty && profile.summary.total == 0
      },
      "empty notice results were not preserved"
    )
  }

  private static func checkPortfolioContractRejectsDifferentNoticeDigests() throws {
    let data = try makeReportData(
      profileCount: 2,
      secondNoticeDigest: String(repeating: "b", count: 64)
    )
    try requireContractError(.inconsistentNoticeSet, data: data)
  }

  private static func checkPortfolioContractRejectsDifferentNoticeOrder() throws {
    let data = try makeReportData(profileCount: 2, reverseSecondResults: true)
    try requireContractError(.inconsistentNoticeSet, data: data)
  }

  private static func checkPortfolioContractRejectsInvalidNestedTotals() throws {
    let data = try makeReportData(profileCount: 1, invalidNestedTotal: true)
    try requireContractError(.invalidProfileReport, data: data)
  }

  private static func checkPortfolioContractRejectsResultSummaryMismatch() throws {
    let data = try makeReportData(profileCount: 2, mismatchSecondSummary: true)
    try requireContractError(.invalidProfileReport, data: data)
  }

  private static func checkWorkspaceDocumentIsStrictBoundedAndDeterministic() throws {
    let profile = try SupplierProfile(
      name: "Example Austria Services",
      cpvCodes: ["72260000", "72261000"],
      countries: ["AUT", "DEU"],
      minimumDaysToDeadline: 14
    )
    let document = try PortfolioWorkspaceDocument(profiles: [profile])
    let first = try document.normalizedJSONData()
    let second = try document.normalizedJSONData()

    try require(first == second, "workspace encoding was not deterministic")
    try require(first.last == 0x0a, "workspace encoding did not end with a newline")
    try require(
      try PortfolioWorkspaceDocument.decode(first) == document,
      "workspace encoding did not round trip"
    )

    let profilePayload: [String: Any] = [
      "schema_version": 1,
      "name": "Example Austria Services",
      "cpv_codes": ["72260000"],
      "countries": ["AUT"],
      "minimum_days_to_deadline": 14,
    ]
    let unknown = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [profilePayload],
        "unexpected": true,
      ]
    )
    try requireThrows("workspace unknown fields were accepted") {
      _ = try PortfolioWorkspaceDocument.decode(unknown)
    }

    let empty = try JSONSerialization.data(
      withJSONObject: ["schema_version": 1, "profiles": []]
    )
    try requireThrows("an empty workspace was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(empty)
    }

    let tooManyProfiles = (1...6).map { index in
      profilePayload.merging(["name": "Profile \(index)"]) { _, replacement in replacement }
    }
    let oversizedEnvelope = try JSONSerialization.data(
      withJSONObject: ["schema_version": 1, "profiles": tooManyProfiles]
    )
    try requireThrows("a six-profile workspace was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(oversizedEnvelope)
    }

    let duplicate = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [
          profilePayload,
          profilePayload.merging(["name": "example austria services"]) { _, replacement in
            replacement
          },
        ],
      ]
    )
    try requireThrows("duplicate workspace profile names were accepted") {
      _ = try PortfolioWorkspaceDocument.decode(duplicate)
    }

    let unnormalizedProfile = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [
          profilePayload.merging(["countries": ["aut"]]) { _, replacement in replacement }
        ],
      ]
    )
    try requireThrows("unnormalized workspace countries were accepted") {
      _ = try PortfolioWorkspaceDocument.decode(unnormalizedProfile)
    }

    let invalidMinimum = try JSONSerialization.data(
      withJSONObject: [
        "schema_version": 1,
        "profiles": [
          profilePayload.merging(["minimum_days_to_deadline": 3_651]) { _, replacement in
            replacement
          }
        ],
      ]
    )
    try requireThrows("an out-of-range minimum deadline was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(invalidMinimum)
    }

    try requireThrows("oversized workspace data was accepted") {
      _ = try PortfolioWorkspaceDocument.decode(
        Data(repeating: 0x20, count: PortfolioWorkspaceDocument.maximumBytes + 1)
      )
    }
  }

  private static func checkNoticeImportPreviewContract() throws {
    let preview = try NoticeImportPreview.decode(makeNoticePreviewData())

    try require(preview.schemaVersion == 1, "notice preview schema changed")
    try require(preview.kind == "notice_import_preview", "notice preview kind changed")
    try require(preview.sourceKind == "local_json", "notice preview source changed")
    try require(preview.noticeCount == 2, "notice preview count changed")
    try require(preview.preview.count == 1, "notice preview limit changed")
    try require(
      preview.canonicalFields == NoticeImportPreview.expectedCanonicalFields,
      "notice preview canonical fields changed"
    )
    let row = try requireFirst(preview.preview, "notice preview row was omitted")
    try require(row.lotID == "LOT-0001", "notice preview lot changed")
    try require(row.deadlineAt == "2026-09-15T12:00:00+02:00", "exact deadline changed")
    try require(row.metadataWarnings == ["Public warning"], "metadata warnings changed")
    try require(preview.missingFieldCounts.buyer == 1, "missing buyer count changed")
    try require(preview.missingFieldCounts.deadline == 1, "missing deadline count changed")

    try requireThrows("non-canonical notice fields were accepted") {
      _ = try NoticeImportPreview.decode(
        makeNoticePreviewData(canonicalFields: ["publication_number"])
      )
    }
    try requireThrows("a preview row with two deadlines was accepted") {
      _ = try NoticeImportPreview.decode(makeNoticePreviewData(includeBothDeadlines: true))
    }
    try requireThrows("an impossible missing-field count was accepted") {
      _ = try NoticeImportPreview.decode(makeNoticePreviewData(missingBuyerCount: 3))
    }
    try requireThrows("an oversized notice preview was accepted") {
      _ = try NoticeImportPreview.decode(
        Data(repeating: 0x20, count: NoticeImportPreview.maximumBytes + 1)
      )
    }
  }

  private static func checkReviewQueryAndStableResultLookup() throws {
    let report = try PortfolioWorkspaceReport.decode(makeReportData(profileCount: 3))
    let primary = report.profileReports[0]

    let searched = ReviewQuery(
      searchText: "software support",
      buyerText: "Example Regional Authority",
      deadlinePresence: .supplied
    ).apply(to: primary.results)
    try require(searched.count == 1, "review search did not narrow to one notice")
    try require(searched[0].publicationNumber == "SYN-WATCH-001", "review search found wrong row")
    try require(
      ReviewQuery(buyerText: "Example Regional").apply(to: primary.results).isEmpty,
      "buyer picker filter used a prefix match instead of exact normalized equality"
    )

    let separatorIdentity = NoticeIdentity(
      publicationNumber: "A\u{1f}LOT-0001",
      lotID: nil
    )
    let structuredIdentity = NoticeIdentity(publicationNumber: "A", lotID: "LOT-0001")
    try require(
      separatorIdentity != structuredIdentity,
      "notice identity was vulnerable to delimiter collisions"
    )
    try require(
      NoticeIdentity(publicationNumber: "ABC", lotID: nil)
        != NoticeIdentity(publicationNumber: "ＡＢＣ", lotID: nil),
      "notice identity collapsed Python-distinct width variants"
    )
    try require(
      NoticeIdentity(publicationNumber: "ABC", lotID: "LOT")
        == NoticeIdentity(publicationNumber: "abc", lotID: "lot"),
      "notice identity stopped mirroring Python case-insensitive duplicate handling"
    )

    let missingDeadline = ReviewQuery(deadlinePresence: .missing).apply(to: primary.results)
    try require(missingDeadline.count == 1, "missing-deadline filter changed")
    try require(
      missingDeadline[0].publicationNumber == "SYN-REJECT-001",
      "missing-deadline filter found wrong row"
    )

    let secondProfile = report.profileReports[1]
    let resolved = report.result(profileID: secondProfile.id, resultID: missingDeadline[0].id)
    try require(resolved?.publicationNumber == "SYN-REJECT-001", "stable lookup used row offset")
    try require(
      report.profileReport(id: secondProfile.id) == secondProfile, "profile lookup failed")
    try require(
      report.result(profileID: "missing", resultID: missingDeadline[0].id) == nil,
      "unknown profile lookup did not fail closed"
    )
  }

  private static func checkLargeReviewQueryPreservesStableIdentities() throws {
    let report = try PortfolioWorkspaceReport.decode(
      makeLargeReportData(profileCount: 3, noticeCount: 125)
    )
    try require(
      report.divergentNoticeCount == 125,
      "portfolio disagreement teaser changed shared verdict comparison"
    )
    let primary = report.profileReports[0]
    let missing = ReviewQuery(deadlinePresence: .missing).apply(to: primary.results)
    try require(missing.count == 13, "large missing-deadline filter changed")

    let searched = ReviewQuery(
      searchText: "0124 synthetic service",
      buyerText: "Example Buyer 05",
      deadlinePresence: .supplied
    ).apply(to: primary.results)
    try require(searched.count == 1, "large review search did not find the final row")
    try require(
      searched[0].publicationNumber == "SYN-LARGE-0124",
      "large review search found wrong row"
    )

    let secondProfile = report.profileReports[1]
    let resolved = report.result(profileID: secondProfile.id, resultID: searched[0].id)
    try require(
      resolved?.publicationNumber == "SYN-LARGE-0124",
      "large stable lookup confused filtered index with source index"
    )
  }

  private static func checkTestStoreConfigurationFailsClosed() async throws {
    let syntheticTestStoreKey = "test_" + "public_fixture"
    try require(
      RevenueCatAccessController.isExpectedPackage(
        offeringIdentifier: "supplier_profiles_plus",
        packageIdentifier: "$rc_monthly",
        productIdentifier: "supplier_profiles_plus_monthly"
      ),
      "documented RevenueCat package contract was rejected"
    )
    try require(
      !RevenueCatAccessController.isExpectedPackage(
        offeringIdentifier: "supplier_profiles_plus",
        packageIdentifier: "$rc_annual",
        productIdentifier: "supplier_profiles_plus_annual"
      ),
      "unexpected RevenueCat package was accepted"
    )
    #if DEBUG
      try require(
        RevenueCatTestStoreConfiguration.status(in: [:]) == .missing,
        "missing Test Store key did not fail closed"
      )
      try require(
        RevenueCatTestStoreConfiguration.status(
          in: [RevenueCatTestStoreConfiguration.environmentName: ""]
        ) == .rejected,
        "empty Test Store key was accepted"
      )
      try require(
        RevenueCatTestStoreConfiguration.status(
          in: [RevenueCatTestStoreConfiguration.environmentName: "appl_public_fixture"]
        ) == .rejected,
        "non-Test Store key was accepted"
      )
      try require(
        RevenueCatTestStoreConfiguration.status(
          in: [RevenueCatTestStoreConfiguration.environmentName: syntheticTestStoreKey]
        ) == .accepted,
        "synthetic Test Store-shaped key was rejected in Debug"
      )
    #else
      for environment in [
        [:],
        [RevenueCatTestStoreConfiguration.environmentName: syntheticTestStoreKey],
        [RevenueCatTestStoreConfiguration.environmentName: "appl_public_fixture"],
      ] {
        try require(
          RevenueCatTestStoreConfiguration.status(in: environment) == .unavailableInRelease,
          "Release build exposed RevenueCat configuration"
        )
      }
      let controller = await RevenueCatAccessController(
        environment: [
          RevenueCatTestStoreConfiguration.environmentName: syntheticTestStoreKey
        ]
      )
      await controller.configure(testStoreAPIKey: syntheticTestStoreKey)
      await controller.start()
      let finalState = await controller.state
      try require(
        finalState == .testStoreUnavailableInRelease,
        "Release controller reached RevenueCat configuration"
      )
    #endif
  }

  private static func checkJudgeAccessAndExpiryTransitions() throws {
    let cutoff = RevenueCatJudgeAccess.expiresAt
    let beforeCutoff = cutoff.addingTimeInterval(-1)
    let afterCutoff = cutoff.addingTimeInterval(1)
    let knownDigest = "4e118a47833348f05045f3cf9146faf4ba095874cb1a922db81f99ae8384b3db"
    let judgeAppUserID = RevenueCatJudgeAccess.appUserID(forDigest: knownDigest)

    try require(
      RevenueCatJudgeAccess.validate("not-a-judge-code", now: beforeCutoff) == .invalid,
      "unknown Judge Access code was accepted"
    )
    try require(
      RevenueCatJudgeAccess.validate("any-code-after-cutoff", now: afterCutoff) == .expired,
      "Judge Access remained redeemable after its documented cutoff"
    )
    try require(
      RevenueCatJudgeAccess.isKnownAppUserID(judgeAppUserID),
      "configured Judge Access customer was not recognized"
    )
    try require(
      !RevenueCatJudgeAccess.isKnownAppUserID("tvj_public_fixture"),
      "unknown Judge Access customer was accepted"
    )
    try require(
      RevenueCatAccessController.resolvedAccessSource(
        entitlementIsActive: true,
        store: .testStore,
        expirationDate: cutoff,
        appUserID: "$RCAnonymousID:public-fixture",
        now: beforeCutoff
      ) == .testStore,
      "active Test Store entitlement did not unlock Premium"
    )
    try require(
      RevenueCatAccessController.resolvedAccessSource(
        entitlementIsActive: true,
        store: .promotional,
        expirationDate: cutoff.addingTimeInterval(3_600),
        appUserID: judgeAppUserID,
        now: beforeCutoff
      ) == .judgeAccess(expiresAt: cutoff),
      "RevenueCat granted entitlement was not bounded to the Judge Access cutoff"
    )
    try require(
      RevenueCatAccessController.resolvedAccessSource(
        entitlementIsActive: true,
        store: .promotional,
        expirationDate: cutoff.addingTimeInterval(3_600),
        appUserID: judgeAppUserID,
        now: afterCutoff
      ) == nil,
      "Judge Access remained unlocked after the local campaign cutoff"
    )
    try require(
      RevenueCatAccessController.resolvedAccessSource(
        entitlementIsActive: false,
        store: .testStore,
        expirationDate: cutoff,
        appUserID: "$RCAnonymousID:public-fixture",
        now: beforeCutoff
      ) == nil,
      "inactive entitlement unlocked Premium"
    )
  }

  private static func checkPremiumAccessibilityOutcomes() throws {
    let offeringMarker = "TEST-OFFERING"
    let knownDigestMarker = "4e118a47833348f0"
    let cases: [(PremiumAccessState, PremiumAccessRecoveryAction, PremiumAccessFocusTarget)] = [
      (.configurationMissing, .connectTestStore, .testStoreAPIKey),
      (.configurationRejected, .connectTestStore, .testStoreAPIKey),
      (.locked(price: nil), .restore, .restore),
      (.locked(price: offeringMarker), .purchase, .purchase),
      (.unlocked, .restore, .restore),
      (.cancelled(price: nil), .restore, .restore),
      (.cancelled(price: offeringMarker), .purchase, .purchase),
      (.failed, .retry, .retry),
    ]
    try require(
      PremiumAccessState.loading.terminalAccessibilityOutcome == nil,
      "loading state emitted a terminal accessibility outcome"
    )
    guard
      let unavailable = PremiumAccessState.testStoreUnavailableInRelease
        .terminalAccessibilityOutcome
    else {
      throw CheckFailure.failed("Release Test Store state omitted accessibility outcome")
    }
    try require(
      unavailable.primaryRecoveryAction == nil && unavailable.focusTarget == nil,
      "Release Test Store state exposed an unavailable recovery control"
    )
    for (state, primaryAction, focusTarget) in cases {
      guard let outcome = state.terminalAccessibilityOutcome else {
        throw CheckFailure.failed("terminal RevenueCat state omitted accessibility outcome")
      }
      try require(!outcome.announcement.isEmpty, "accessibility announcement was empty")
      try require(
        outcome.primaryRecoveryAction == primaryAction,
        "accessibility primary recovery action changed"
      )
      try require(outcome.focusTarget == focusTarget, "accessibility recovery focus changed")
      try require(
        !outcome.announcement.contains("test_")
          && !outcome.announcement.contains("appl_")
          && !outcome.announcement.contains(offeringMarker),
        "accessibility announcement exposed configuration or package data"
      )
    }

    let judgeCases:
      [(JudgeAccessActivationState, PremiumAccessRecoveryAction?, PremiumAccessFocusTarget)] = [
        (.invalidCode, .activateJudgeAccess, .judgeAccessCode),
        (.expired, nil, .judgeAccessCode),
        (.entitlementMissing, .activateJudgeAccess, .judgeAccessCode),
        (.failed, .activateJudgeAccess, .judgeAccessCode),
        (.active(expiresAt: RevenueCatJudgeAccess.expiresAt), .restore, .restore),
      ]
    for (state, primaryAction, focusTarget) in judgeCases {
      guard let outcome = state.terminalAccessibilityOutcome else {
        throw CheckFailure.failed("terminal Judge Access state omitted accessibility outcome")
      }
      try require(
        outcome.primaryRecoveryAction == primaryAction,
        "Judge Access recovery action changed"
      )
      try require(outcome.focusTarget == focusTarget, "Judge Access recovery focus changed")
      try require(
        !outcome.announcement.contains(knownDigestMarker),
        "Judge Access announcement exposed a customer identifier"
      )
    }
  }

  private static func checkProcessAdapterPreservesDeterministicBytes() throws {
    let runner = try TenderVerdictProcess()
    guard let worktree = runner.worktree else {
      throw CheckFailure.failed("source adapter worktree was not discovered")
    }
    let workspace = worktree.appendingPathComponent(
      "examples/synthetic/portfolio-workspace.json"
    )
    let notices = worktree.appendingPathComponent("examples/synthetic/notices.json")
    let first = try runner.runPortfolioSynchronously(
      workspace: workspace,
      notices: notices,
      asOf: TenderVerdictProcess.syntheticAsOf
    )
    let second = try runner.runPortfolioSynchronously(
      workspace: workspace,
      notices: notices,
      asOf: TenderVerdictProcess.syntheticAsOf
    )

    try require(first.report == second.report, "selected-input reports were not deterministic")
    try require(first.jsonData == second.jsonData, "selected-input JSON bytes changed between runs")
    try require(
      first.report.summary.profileCount == 3,
      "selected workspace did not preserve profile count"
    )

    let normalizedFirst = try runner.normalizeWorkspaceSynchronously(workspace)
    let normalizedSecond = try runner.normalizeWorkspaceSynchronously(workspace)
    try require(
      normalizedFirst == normalizedSecond,
      "workspace normalization changed between source-adapter runs"
    )
    try require(
      normalizedFirst.document.profiles.map(\.name)
        == ["Example Austria Services", "Example Germany Support", "Example DACH Operations"],
      "workspace normalization changed profile order"
    )

    let preview = try runner.inspectNoticesSynchronously(notices, limit: 2)
    try require(preview.noticeCount == 3, "notice inspection changed the source count")
    try require(preview.preview.count == 2, "notice inspection ignored its bounded limit")
    try require(
      preview.preview[0].publicationNumber == "SYN-OPEN-001",
      "notice inspection changed input order"
    )
    try requireThrows("an invalid native preview limit was accepted") {
      _ = try runner.inspectNoticesSynchronously(notices, limit: 21)
    }
  }

  private static func require(_ condition: Bool, _ message: String) throws {
    guard condition else {
      throw CheckFailure.failed(message)
    }
  }

  private static func require<T: Equatable>(
    _ actual: T,
    equals expected: T,
    _ message: String
  ) throws {
    try require(actual == expected, message)
  }

  private static func requireThrows(
    _ message: String,
    operation: () throws -> Void
  ) throws {
    do {
      try operation()
    } catch {
      return
    }
    throw CheckFailure.failed(message)
  }

  private static func requireContractError(
    _ expected: PortfolioContractError,
    data: Data
  ) throws {
    do {
      _ = try PortfolioWorkspaceReport.decode(data)
    } catch let error as PortfolioContractError {
      try require(error == expected, "unexpected contract error: \(error)")
      return
    }
    throw CheckFailure.failed("invalid portfolio report was accepted")
  }

  private static func requireFirst<T>(_ values: [T], _ message: String) throws -> T {
    guard let value = values.first else {
      throw CheckFailure.failed(message)
    }
    return value
  }

  private static func requireDictionary(_ data: Data, _ message: String) throws
    -> [String: Any]
  {
    guard let value = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
      throw CheckFailure.failed(message)
    }
    return value
  }
}

private func makeNoticePreviewData(
  canonicalFields: [String] = NoticeImportPreview.expectedCanonicalFields,
  includeBothDeadlines: Bool = false,
  missingBuyerCount: Int = 1
) throws -> Data {
  let row: [String: Any] = [
    "publication_number": "SYN-FULL-001",
    "lot_id": "LOT-0001",
    "notice_type": "competition",
    "title": "Full notice",
    "buyer": "Example Buyer",
    "cpv_codes": ["72260000"],
    "countries": ["AUT"],
    "deadline": includeBothDeadlines ? "2026-09-15" : NSNull(),
    "deadline_at": "2026-09-15T12:00:00+02:00",
    "publication_date": "2026-08-01",
    "source_url": "https://procurement.example/full",
    "metadata_warnings": ["Public warning"],
  ]
  let payload: [String: Any] = [
    "schema_version": 1,
    "kind": "notice_import_preview",
    "source_kind": "local_json",
    "notice_count": 2,
    "canonical_fields": canonicalFields,
    "preview": [row],
    "missing_field_counts": [
      "notice_type": 1,
      "title": 0,
      "buyer": missingBuyerCount,
      "cpv_codes": 1,
      "countries": 1,
      "deadline": 1,
      "source_url": 1,
    ],
  ]
  return try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
}

private func makeLargeReportData(profileCount: Int, noticeCount: Int) throws -> Data {
  let sharedNoticeDigest = String(repeating: "a", count: 64)
  let verdicts = ["open_documents", "watch", "reject"]
  let reports: [[String: Any]] = (1...profileCount).map { profileIndex in
    var counts = ["open_documents": 0, "watch": 0, "reject": 0]
    let results: [[String: Any]] = (0..<noticeCount).map { noticeIndex in
      let verdict = verdicts[(noticeIndex + profileIndex - 1) % verdicts.count]
      counts[verdict, default: 0] += 1
      let hasDeadline = noticeIndex % 10 != 0
      return [
        "publication_number": String(format: "SYN-LARGE-%04d", noticeIndex),
        "lot_id": NSNull(),
        "title": "Synthetic service \(noticeIndex)",
        "buyer": String(format: "Example Buyer %02d", noticeIndex % 7),
        "deadline": hasDeadline ? "2026-09-15" : NSNull(),
        "deadline_at": NSNull(),
        "publication_date": "2026-08-01",
        "source_url": "https://procurement.example/large/\(noticeIndex)",
        "verdict": verdict,
        "reasons": ["Synthetic deterministic reason."],
        "unknowns": [],
        "human_next_step": "Review the supplied metadata.",
      ]
    }
    return [
      "schema_version": 3,
      "provenance": [
        "generator": ["name": "TenderVerdict", "version": "0.2.0a1"],
        "source_kind": "local_json",
        "profile_sha256": String(repeating: String(profileIndex), count: 64),
        "notices_sha256": sharedNoticeDigest,
      ],
      "profile": [
        "schema_version": 1,
        "name": "Large Profile \(profileIndex)",
        "cpv_codes": ["72260000"],
        "countries": ["AUT"],
        "minimum_days_to_deadline": 14,
      ],
      "as_of": "2026-08-02",
      "summary": [
        "total": noticeCount,
        "open_documents": counts["open_documents", default: 0],
        "watch": counts["watch", default: 0],
        "reject": counts["reject", default: 0],
      ],
      "results": results,
    ]
  }
  let payload: [String: Any] = [
    "schema_version": 1,
    "kind": "portfolio_workspace_report",
    "as_of": "2026-08-02",
    "summary": [
      "profile_count": profileCount,
      "notice_count": noticeCount,
    ],
    "profile_reports": reports,
  ]
  return try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
}

private func makeReportData(
  profileCount: Int,
  declaredProfileCount: Int? = nil,
  secondNoticeDigest: String? = nil,
  invalidNestedTotal: Bool = false,
  reverseSecondResults: Bool = false,
  mismatchSecondSummary: Bool = false,
  noticeCount: Int = 3,
  firstProfileName: String? = nil,
  firstSourceURL: String? = nil
) throws -> Data {
  let sharedNoticeDigest = String(repeating: "a", count: 64)
  let reports: [[String: Any]] = (1...profileCount).map { index in
    let noticeDigest = index == 2 ? secondNoticeDigest ?? sharedNoticeDigest : sharedNoticeDigest
    var results =
      noticeCount == 0
      ? []
      : makeResults(firstSourceURL: index == 1 ? firstSourceURL : nil)
    if index == 2 && reverseSecondResults {
      results.reverse()
    }
    if index == 2 && mismatchSecondSummary {
      results[0]["verdict"] = "reject"
    }
    let summary: [String: Any]
    if invalidNestedTotal {
      summary = ["total": 3, "open_documents": 1, "watch": 1, "reject": 2]
    } else if noticeCount == 0 {
      summary = ["total": 0, "open_documents": 0, "watch": 0, "reject": 0]
    } else {
      summary = ["total": 3, "open_documents": 1, "watch": 1, "reject": 1]
    }
    return [
      "schema_version": 3,
      "provenance": [
        "generator": ["name": "TenderVerdict", "version": "0.2.0a1"],
        "source_kind": "ted_api",
        "profile_sha256": String(repeating: String(index), count: 64),
        "notices_sha256": noticeDigest,
        "ted_query": "fixture query",
        "retrieved_at": "2026-08-02T10:00:00Z",
        "lot_policy": "verified_lots",
      ],
      "profile": [
        "schema_version": 1,
        "name": index == 1 ? firstProfileName ?? "Profile 1" : "Profile \(index)",
        "cpv_codes": ["72260000"],
        "countries": ["AUT"],
        "minimum_days_to_deadline": 14,
      ],
      "as_of": "2026-08-02",
      "summary": summary,
      "results": results,
    ]
  }
  let payload: [String: Any] = [
    "schema_version": 1,
    "kind": "portfolio_workspace_report",
    "as_of": "2026-08-02",
    "summary": [
      "profile_count": declaredProfileCount ?? profileCount,
      "notice_count": noticeCount,
    ],
    "profile_reports": reports,
  ]
  return try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
}

private func makeResults(firstSourceURL: String? = nil) -> [[String: Any]] {
  [
    [
      "publication_number": "SYN-OPEN-001",
      "lot_id": NSNull(),
      "title": "Application maintenance services",
      "buyer": "Example City Procurement Office",
      "deadline": "2026-09-15",
      "deadline_at": NSNull(),
      "publication_date": "2026-08-01",
      "source_url": firstSourceURL ?? "https://procurement.example/notices/SYN-OPEN-001",
      "verdict": "open_documents",
      "reasons": ["Exact CPV match: 72260000.", "Country match: AUT."],
      "unknowns": [],
      "human_next_step": "Open and review the official procurement documents.",
    ],
    [
      "publication_number": "SYN-WATCH-001",
      "lot_id": NSNull(),
      "title": "Software support services",
      "buyer": "Example Regional Authority",
      "deadline": "2026-09-20",
      "deadline_at": NSNull(),
      "publication_date": "2026-07-30",
      "source_url": "https://procurement.example/notices/SYN-WATCH-001",
      "verdict": "watch",
      "reasons": ["Broader CPV class match."],
      "unknowns": ["Confirm the exact procurement scope."],
      "human_next_step": "Verify the flagged metadata.",
    ],
    [
      "publication_number": "SYN-REJECT-001",
      "lot_id": NSNull(),
      "title": "Software implementation services",
      "buyer": "Example Federal Agency",
      "deadline": NSNull(),
      "deadline_at": NSNull(),
      "publication_date": "2026-07-15",
      "source_url": "https://procurement.example/notices/SYN-REJECT-001",
      "verdict": "reject",
      "reasons": ["Deadline is below the configured minimum."],
      "unknowns": [],
      "human_next_step": "Do not proceed for this profile.",
    ],
  ]
}
