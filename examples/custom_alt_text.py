#!/usr/bin/env python3
"""
Custom Alt Text Example - PDF Remediator

This example demonstrates how to add custom alternative text
to images instead of using auto-generated descriptions.
"""

from pdf_remediator import EnhancedPDFRemediator

def main():
    # Define paths
    input_pdf = "input.pdf"
    output_pdf = "output_with_custom_alt.pdf"

    print("Custom Alt Text Remediation Example")
    print("=" * 60)

    # Initialize
    remediator = EnhancedPDFRemediator(input_pdf, output_pdf)

    try:
        # Load PDF
        print(f"\nLoading: {input_pdf}")
        remediator.load_pdf()

        # Analyze images first
        print("\nAnalyzing images...")
        images = remediator.analyze_images()

        print(f"Found {len(images)} images:")
        for img in images:
            decorative = "Decorative" if img.is_decorative else "Descriptive"
            print(f"  {img.name} (Page {img.page_number}): {decorative}")
            print(f"    Size: {img.width}x{img.height}")
            if not img.is_decorative:
                print(f"    Auto-generated: '{img.alt_text}'")

        # Define custom alt text for specific images
        # Adjust these based on your PDF's actual images
        custom_alt_text = {
            '/Im1': 'Company logo featuring a mountain peak with the tagline "Reaching New Heights"',
            '/Im2': 'Process flow diagram showing 5 steps: Planning, Design, Development, Testing, and Deployment',
            '/Im3': 'Bar chart comparing quarterly revenue from 2020 to 2024, showing 25% growth',
            '/Im4': 'Team photo of 12 employees at the annual company retreat',
            '/Im5': 'Screenshot of the dashboard interface with key metrics highlighted'
        }

        # Apply custom alt text
        print("\nApplying custom alt text...")
        for img_name, alt_text in custom_alt_text.items():
            # Check if this image exists in the PDF
            matching_img = next((img for img in images if img.name == img_name), None)

            if matching_img:
                if not matching_img.is_decorative:
                    remediator.add_alt_text(img_name, alt_text)
                    print(f"  ✓ {img_name}: '{alt_text[:50]}...'")
                else:
                    print(f"  ⊘ {img_name}: Skipped (decorative)")
            else:
                print(f"  ? {img_name}: Not found in PDF")

        # Optionally mark some images as decorative
        decorative_images = ['/Im6', '/Im7']  # Borders, separators, etc.

        print("\nMarking decorative images...")
        for img_name in decorative_images:
            matching_img = next((img for img in images if img.name == img_name), None)
            if matching_img:
                remediator.mark_image_decorative(img_name)
                print(f"  ✓ {img_name}: Marked as decorative")

        # Complete remediation
        print("\nRemediating PDF...")
        options = {
            'title': 'Annual Report 2024',
            'author': 'Finance Department',
            'subject': 'Financial Analysis and Projections',
            'keywords': 'finance, report, annual, revenue, growth',
            'language': 'en-US',
            'flatten': True
        }
        remediator.remediate(options)

        # Save
        print(f"\nSaving: {output_pdf}")
        remediator.save()

        # Report statistics
        stats = remediator.get_statistics()
        print("\n=== Remediation Complete ===")
        print(f"Images tagged: {stats['images_tagged']}")
        print(f"  Decorative: {stats['images_decorative']}")
        print(f"  Descriptive: {stats['images_descriptive']}")
        print(f"Issues fixed: {stats['issues_fixed']}/{stats['issues_found']}")

        print("\nRecommendations:")
        print("  1. Review custom alt text for accuracy")
        print("  2. Test with screen reader (NVDA, JAWS, VoiceOver)")
        print("  3. Verify decorative images are truly decorative")
        print("  4. Validate with accessibility checker (PAC 3)")

    except FileNotFoundError:
        print(f"\nError: File not found: {input_pdf}")
        print("Please ensure the PDF exists and the path is correct.")

    except Exception as e:
        print(f"\nError during remediation: {e}")

    finally:
        remediator.close()


if __name__ == "__main__":
    main()
