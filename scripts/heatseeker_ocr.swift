import Foundation
import Vision
import AppKit

struct OCRLine: Codable {
    let text: String
    let confidence: Float
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct OCRResult: Codable {
    let image_path: String
    let lines: [OCRLine]
}

func fail(_ message: String) -> Never {
    fputs("ERROR: \(message)\n", stderr)
    exit(1)
}

let args = CommandLine.arguments
if args.count != 2 {
    fail("usage: swift heatseeker_ocr.swift <image_path>")
}

let imagePath = args[1]
let url = URL(fileURLWithPath: imagePath)
guard let image = NSImage(contentsOf: url) else {
    fail("cannot open image: \(imagePath)")
}

guard let tiff = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let cgImage = bitmap.cgImage else {
    fail("cannot convert image: \(imagePath)")
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
request.recognitionLanguages = ["en-US"]
request.minimumTextHeight = 0.008

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
} catch {
    fail("Vision OCR failed: \(error)")
}

var lines: [OCRLine] = []
if let observations = request.results {
    for observation in observations {
        guard let candidate = observation.topCandidates(1).first else { continue }
        let box = observation.boundingBox
        lines.append(OCRLine(
            text: candidate.string,
            confidence: candidate.confidence,
            x: Double(box.origin.x),
            y: Double(box.origin.y),
            width: Double(box.size.width),
            height: Double(box.size.height)
        ))
    }
}

// Stable reading order: top-to-bottom, then left-to-right.
lines.sort {
    let ay = $0.y + $0.height
    let by = $1.y + $1.height
    if abs(ay - by) > 0.015 { return ay > by }
    return $0.x < $1.x
}

let result = OCRResult(image_path: imagePath, lines: lines)
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
let data = try encoder.encode(result)
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data("\n".utf8))
