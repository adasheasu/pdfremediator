#!/usr/bin/env python3
"""
Basic Usage Example - PDF Remediator

This example demonstrates the simplest way to remediate a PDF
for WCAG 2.2 Level AA compliance.
"""

from pdf_remediator import EnhancedPDFRemediator

def main():
    # Define paths
    input_pdf = "input.pdf"  # Replace with your PDF path
    output_pdf = "output_remediated.pdf"

    # Initialize remediator
    print("Initializing PDF Remediator...")
    remediator = EnhancedPDFRemediator(input_pdf, output_pdf)

    try:
        # Load PDF
        print(f"Loading: {input_pdf}")
        remediator.load_pdf()

        # Analyze issues (optional)
        print("\nAnalyzing PDF for accessibility issues...")
        issues = remediator.analyze()
        print(f"Found {len(issues)} issues")

        # Remediate with basic options
        print("\nRemediating PDF...")
        options = {
            'title': 'Document Title',
            'author': 'Author Name',
            'language': 'en-US',
            'flatten': True
        }
        remediator.remediate(options)

        # Save
        print(f"\nSaving: {output_pdf}")
        remediator.save()

        # Get statistics
        stats = remediator.get_statistics()
        print("\n=== Remediation Complete ===")
        print(f"Images tagged: {stats['images_tagged']}")
        print(f"  Decorative: {stats['images_decorative']}")
        print(f"  Descriptive: {stats['images_descriptive']}")
        print(f"Tables tagged: {stats['tables_tagged']}")
        print(f"Links fixed: {stats['links_fixed']}")
        print(f"Issues fixed: {stats['issues_fixed']}/{stats['issues_found']}")

    except FileNotFoundError:
        print(f"Error: File not found: {input_pdf}")
    except Exception as e:
        print(f"Error during remediation: {e}")
    finally:
        # Always close
        remediator.close()

if __name__ == "__main__":
    main()
