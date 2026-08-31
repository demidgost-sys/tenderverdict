import AppKit
import Foundation

struct Canvas: Decodable {
  let width: Int
  let height: Int
  let fps: Int
}

struct Crop: Decodable {
  let x: CGFloat
  let y: CGFloat
  let width: CGFloat
  let height: CGFloat
}

struct Shot: Decodable {
  let id: String
  let duration: Double
  let source: String
  let crop: Crop?
  let eyebrow: String
  let title: String
  let body: String
  let chips: [String]
  let evidence: String
}

struct Timeline: Decodable {
  let version: Int
  let canvas: Canvas
  let shots: [Shot]
}

guard CommandLine.arguments.count == 4 else {
  fputs("usage: swift render_cards.swift <timeline.json> <output-dir> <shots.tsv>\n", stderr)
  exit(2)
}

let timelineURL = URL(fileURLWithPath: CommandLine.arguments[1]).standardizedFileURL
let packageRoot = timelineURL.deletingLastPathComponent()
let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
let tsvURL = URL(fileURLWithPath: CommandLine.arguments[3])
let timeline = try JSONDecoder().decode(Timeline.self, from: Data(contentsOf: timelineURL))

guard timeline.version == 1, timeline.canvas.width == 1920, timeline.canvas.height == 1080 else {
  throw NSError(
    domain: "TenderVerdictVideo",
    code: 1,
    userInfo: [NSLocalizedDescriptionKey: "Unsupported timeline or canvas"]
  )
}

try FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

let canvasSize = NSSize(width: timeline.canvas.width, height: timeline.canvas.height)
let accent = NSColor(calibratedRed: 0.42, green: 0.34, blue: 1.0, alpha: 1.0)
let backgroundTop = NSColor(calibratedRed: 0.055, green: 0.060, blue: 0.085, alpha: 1.0)
let backgroundBottom = NSColor(calibratedRed: 0.018, green: 0.020, blue: 0.033, alpha: 1.0)
let muted = NSColor.white.withAlphaComponent(0.68)

func drawText(
  _ text: String,
  in rect: NSRect,
  font: NSFont,
  color: NSColor,
  lineSpacing: CGFloat = 0,
  alignment: NSTextAlignment = .left
) {
  let paragraph = NSMutableParagraphStyle()
  paragraph.lineBreakMode = .byWordWrapping
  paragraph.lineSpacing = lineSpacing
  paragraph.alignment = alignment
  let attributes: [NSAttributedString.Key: Any] = [
    .font: font,
    .foregroundColor: color,
    .paragraphStyle: paragraph,
  ]
  NSAttributedString(string: text, attributes: attributes).draw(
    with: rect,
    options: [.usesLineFragmentOrigin, .usesFontLeading]
  )
}

func bitmapImage(at url: URL) throws -> NSImage {
  let data = try Data(contentsOf: url)
  guard let representation = NSBitmapImageRep(data: data) else {
    throw NSError(
      domain: "TenderVerdictVideo",
      code: 2,
      userInfo: [NSLocalizedDescriptionKey: "Cannot decode image: \(url.path)"]
    )
  }
  let image = NSImage(
    size: NSSize(width: representation.pixelsWide, height: representation.pixelsHigh)
  )
  image.addRepresentation(representation)
  return image
}

func aspectFit(_ source: NSSize, inside destination: NSRect) -> NSRect {
  let scale = min(destination.width / source.width, destination.height / source.height)
  let size = NSSize(width: source.width * scale, height: source.height * scale)
  return NSRect(
    x: destination.midX - size.width / 2,
    y: destination.midY - size.height / 2,
    width: size.width,
    height: size.height
  )
}

func sourceRect(for image: NSImage, crop: Crop?) -> NSRect {
  guard let crop else {
    return NSRect(origin: .zero, size: image.size)
  }
  let boundedX = max(0, min(crop.x, image.size.width - 1))
  let boundedY = max(0, min(crop.y, image.size.height - 1))
  let boundedWidth = max(1, min(crop.width, image.size.width - boundedX))
  let boundedHeight = max(1, min(crop.height, image.size.height - boundedY))
  return NSRect(
    x: boundedX,
    y: image.size.height - boundedY - boundedHeight,
    width: boundedWidth,
    height: boundedHeight
  )
}

var tsvLines: [String] = []

for shot in timeline.shots {
  let sourceURL = URL(fileURLWithPath: shot.source, relativeTo: packageRoot).standardizedFileURL
  let sourceImage = try bitmapImage(at: sourceURL)
  let cropRect = sourceRect(for: sourceImage, crop: shot.crop)

  guard
    let bitmap = NSBitmapImageRep(
      bitmapDataPlanes: nil,
      pixelsWide: timeline.canvas.width,
      pixelsHigh: timeline.canvas.height,
      bitsPerSample: 8,
      samplesPerPixel: 4,
      hasAlpha: true,
      isPlanar: false,
      colorSpaceName: .deviceRGB,
      bytesPerRow: 0,
      bitsPerPixel: 0
    ),
    let bitmapContext = NSGraphicsContext(bitmapImageRep: bitmap)
  else {
    throw NSError(
      domain: "TenderVerdictVideo",
      code: 3,
      userInfo: [NSLocalizedDescriptionKey: "Cannot create bitmap context"]
    )
  }

  NSGraphicsContext.saveGraphicsState()
  NSGraphicsContext.current = bitmapContext

  NSGradient(starting: backgroundTop, ending: backgroundBottom)?.draw(
    in: NSRect(origin: .zero, size: canvasSize),
    angle: -90
  )

  let glow = NSBezierPath(ovalIn: NSRect(x: 520, y: 210, width: 1320, height: 720))
  NSColor(calibratedRed: 0.26, green: 0.20, blue: 0.65, alpha: 0.16).setFill()
  glow.fill()

  accent.setFill()
  NSBezierPath(
    roundedRect: NSRect(x: 80, y: 1008, width: 54, height: 6),
    xRadius: 3,
    yRadius: 3
  ).fill()
  drawText(
    "TENDERVERDICT NEXT GEN  ·  SHIPATON 2026",
    in: NSRect(x: 154, y: 984, width: 760, height: 42),
    font: .systemFont(ofSize: 23, weight: .semibold),
    color: muted
  )
  drawText(
    shot.eyebrow,
    in: NSRect(x: 80, y: 875, width: 620, height: 42),
    font: .systemFont(ofSize: 22, weight: .bold),
    color: accent
  )
  drawText(
    shot.title,
    in: NSRect(x: 80, y: 620, width: 620, height: 240),
    font: .systemFont(ofSize: 52, weight: .bold),
    color: .white,
    lineSpacing: 4
  )
  drawText(
    shot.body,
    in: NSRect(x: 80, y: 390, width: 620, height: 210),
    font: .systemFont(ofSize: 29, weight: .medium),
    color: NSColor.white.withAlphaComponent(0.86),
    lineSpacing: 7
  )

  var chipX: CGFloat = 80
  var chipY: CGFloat = 304
  for chip in shot.chips {
    let chipWidth = min(590, max(150, CGFloat(chip.count) * 14.0 + 44))
    if chipX + chipWidth > 700 {
      chipX = 80
      chipY -= 54
    }
    let chipRect = NSRect(x: chipX, y: chipY, width: chipWidth, height: 42)
    NSColor.white.withAlphaComponent(0.085).setFill()
    NSBezierPath(roundedRect: chipRect, xRadius: 20, yRadius: 20).fill()
    drawText(
      chip,
      in: NSRect(
        x: chipRect.minX + 16,
        y: chipRect.minY + 8,
        width: chipRect.width - 32,
        height: 26
      ),
      font: .monospacedSystemFont(ofSize: 18, weight: .semibold),
      color: NSColor.white.withAlphaComponent(0.88),
      alignment: .center
    )
    chipX += chipWidth + 12
  }

  let mediaFrame = NSRect(x: 750, y: 132, width: 1090, height: 808)
  let mediaPath = NSBezierPath(roundedRect: mediaFrame, xRadius: 28, yRadius: 28)
  NSColor.white.withAlphaComponent(0.06).setFill()
  mediaPath.fill()
  NSColor.white.withAlphaComponent(0.13).setStroke()
  mediaPath.lineWidth = 2
  mediaPath.stroke()

  let innerFrame = mediaFrame.insetBy(dx: 24, dy: 24)
  let fitted = aspectFit(cropRect.size, inside: innerFrame)
  bitmapContext.saveGraphicsState()
  let clipPath = NSBezierPath(roundedRect: fitted, xRadius: 18, yRadius: 18)
  clipPath.addClip()
  sourceImage.draw(
    in: fitted,
    from: cropRect,
    operation: .sourceOver,
    fraction: 1.0,
    respectFlipped: true,
    hints: [.interpolation: NSImageInterpolation.high]
  )
  bitmapContext.restoreGraphicsState()

  drawText(
    shot.evidence,
    in: NSRect(x: 80, y: 58, width: 1760, height: 32),
    font: .systemFont(ofSize: 20, weight: .medium),
    color: NSColor.white.withAlphaComponent(0.66)
  )

  NSGraphicsContext.restoreGraphicsState()

  guard let png = bitmap.representation(using: .png, properties: [:]) else {
    throw NSError(
      domain: "TenderVerdictVideo",
      code: 4,
      userInfo: [NSLocalizedDescriptionKey: "Cannot encode \(shot.id)"]
    )
  }
  let outputURL = outputDirectory.appendingPathComponent("\(shot.id).png")
  try png.write(to: outputURL, options: .atomic)
  tsvLines.append("\(shot.id)\t\(String(format: "%.3f", shot.duration))\t\(outputURL.path)")
  print("RENDERED \(shot.id) duration=\(String(format: "%.3f", shot.duration))")
}

try (tsvLines.joined(separator: "\n") + "\n").write(
  to: tsvURL,
  atomically: true,
  encoding: .utf8
)
