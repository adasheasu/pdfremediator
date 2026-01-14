#!/usr/bin/env python3
"""
Batch Processing Example - PDF Remediator

This example demonstrates how to remediate multiple PDFs in a directory.
"""

import os
import glob
from pdf_remediator import EnhancedPDFRemediator

def remediate_directory(input_dir, output_dir, options):
    """
    Remediate all PDFs in a directory.

    Args:
        input_dir: Directory containing input PDFs
        output_dir: Directory for remediated PDFs
        options: Remediation options dict

    Returns:
        List of result dictionaries
    """
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Find all PDFs
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return []

    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 60)

    results = []

    for i, pdf_file in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_file)
        output_file = os.path.join(output_dir, f"remediated_{filename}")

        print(f"\n[{i}/{len(pdf_files)}] Processing: {filename}")

        try:
            # Initialize remediator
            remediator = EnhancedPDFRemediator(pdf_file, output_file)

            # Load and analyze
            remediator.load_pdf()
            issues = remediator.analyze()
            print(f"  Found {len(issues)} issues")

            # Remediate
            remediator.remediate(options)

            # Save
            remediator.save()

            # Get statistics
            stats = remediator.get_statistics()

            # Record success
            results.append({
                'file': filename,
                'status': 'success',
                'issues_found': stats['issues_found'],
                'issues_fixed': stats['issues_fixed'],
                'images_tagged': stats['images_tagged'],
                'output': output_file
            })

            print(f"  ✓ Success: {stats['issues_fixed']} issues fixed")

            # Cleanup
            remediator.close()

        except Exception as e:
            # Record error
            results.append({
                'file': filename,
                'status': 'error',
                'error': str(e)
            })

            print(f"  ✗ Error: {e}")

    return results


def print_summary(results):
    """Print summary of batch processing."""
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']

    print(f"\nTotal files: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if successful:
        print("\n✓ Successful:")
        for result in successful:
            print(f"  - {result['file']}")
            print(f"    Issues fixed: {result['issues_fixed']}/{result['issues_found']}")

    if failed:
        print("\n✗ Failed:")
        for result in failed:
            print(f"  - {result['file']}")
            print(f"    Error: {result['error']}")


def main():
    # Configuration
    input_directory = "input_pdfs"      # Change to your input directory
    output_directory = "remediated"     # Change to your output directory

    # Remediation options
    options = {
        'title': 'Document',           # Will use filename if not specified
        'author': 'Department Name',
        'language': 'en-US',
        'flatten': True
    }

    print("PDF BATCH REMEDIATION")
    print("=" * 60)
    print(f"Input directory: {input_directory}")
    print(f"Output directory: {output_directory}")
    print()

    # Process all PDFs
    results = remediate_directory(input_directory, output_directory, options)

    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
