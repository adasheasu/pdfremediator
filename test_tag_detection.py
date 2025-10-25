#!/usr/bin/env python3
"""
Test Enhanced Tag Detection

This script tests the new tag-aware remediation features that skip already-tagged content.
"""

import sys
from pathlib import Path

try:
    from pdf_remediator import EnhancedPDFRemediator
except ImportError:
    print("Error: pdf_remediator module not found")
    sys.exit(1)

def test_tag_detection():
    """Test that the tool correctly detects and skips already-tagged PDFs."""

    print("=" * 70)
    print("ENHANCED TAG DETECTION TEST")
    print("=" * 70)
    print()

    # Test scenario: Create a PDF, remediate it, then remediate again
    # Second run should skip already-tagged content

    test_pdf_path = "/Users/alejandradashe/ASU Dropbox/Alejandra Dashe/ASM 246 UPDATES 2023/ASM 246 - Current Lecture Slides - Fall 2023/Week 6 - Out of Africa and Eurasian Occupation/PDFs of slides/6_ASM_246_Week_6_-_Neandertals_Part_1.pdf"

    if not Path(test_pdf_path).exists():
        print(f"Test PDF not found: {test_pdf_path}")
        print()
        print("To test the enhanced tag detection:")
        print("1. Place a PDF in the pdfremediator_github directory")
        print("2. Run: python test_tag_detection.py your_test.pdf")
        return

    print(f"Testing with: {Path(test_pdf_path).name}")
    print()

    # First remediation pass
    print("=" * 70)
    print("FIRST REMEDIATION PASS (should tag everything)")
    print("=" * 70)
    print()

    output_path = Path("/Users/alejandradashe/pdfremediator_github/test_output_pass1.pdf")

    remediator1 = EnhancedPDFRemediator(test_pdf_path, str(output_path))

    if not remediator1.load_pdf():
        print("Failed to load PDF")
        return

    print(f"Loaded PDF: {remediator1.report.total_pages} pages")

    # Analyze and remediate
    issues = remediator1.analyze()
    print(f"Found {len(issues)} issues")
    print()

    options = {
        'title': 'Test Document',
        'author': 'Test Author',
        'language': 'en-US',
        'flatten': False  # Skip flattening for faster testing
    }

    fixed = remediator1.remediate(options)
    print(f"\nFirst pass tagged: {remediator1.report.images_tagged} images")

    # Save
    if remediator1.save():
        print(f"Saved to: {output_path}")
    else:
        print("Failed to save")
        remediator1.close()
        return

    remediator1.close()

    # Second remediation pass - should skip already-tagged content
    print()
    print("=" * 70)
    print("SECOND REMEDIATION PASS (should skip already-tagged content)")
    print("=" * 70)
    print()

    output_path2 = Path("/Users/alejandradashe/pdfremediator_github/test_output_pass2.pdf")

    remediator2 = EnhancedPDFRemediator(str(output_path), str(output_path2))

    if not remediator2.load_pdf():
        print("Failed to load remediated PDF")
        return

    print(f"Loaded remediated PDF: {remediator2.report.total_pages} pages")

    # Analyze and remediate again
    issues2 = remediator2.analyze()
    print(f"Found {len(issues2)} issues")
    print()

    fixed2 = remediator2.remediate(options)
    print(f"\nSecond pass tagged: {remediator2.report.images_tagged} images")
    print("(Should be 0 or very few if already properly tagged)")

    # Save
    if remediator2.save():
        print(f"Saved to: {output_path2}")
    else:
        print("Failed to save")

    remediator2.close()

    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print()
    print(f"First pass images tagged:  {remediator1.report.images_tagged}")
    print(f"Second pass images tagged: {remediator2.report.images_tagged}")
    print()

    if remediator2.report.images_tagged < remediator1.report.images_tagged:
        print("✓ SUCCESS: Tool correctly skips already-tagged content!")
        print(f"  Skipped {remediator1.report.images_tagged - remediator2.report.images_tagged} already-tagged images")
    else:
        print("⚠ WARNING: Tool may be re-tagging already-tagged content")
        print("  This could indicate an issue with tag detection")

    print()
    print("Check the console output above for 'Skipping' messages")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use provided PDF path
        test_pdf_path = sys.argv[1]
        if not Path(test_pdf_path).exists():
            print(f"Error: File not found: {test_pdf_path}")
            sys.exit(1)

    test_tag_detection()
