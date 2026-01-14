#!/usr/bin/env python3
"""
PDF Remediator Wrapper for Claude Code
Easy-to-use interface for remediating PDFs for accessibility
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Add the directory containing pdf_remediator.py to the path
sys.path.insert(0, str(Path.home()))

try:
    from pdf_remediator import EnhancedPDFRemediator
except ImportError:
    print("Error: Could not import pdf_remediator module")
    print(f"Looking for module at: {Path.home() / 'pdf_remediator.py'}")
    sys.exit(1)


def remediate_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    append_date: bool = True,
    title: Optional[str] = None,
    author: Optional[str] = None,
    subject: Optional[str] = None,
    keywords: Optional[str] = None,
    language: str = "en-US",
    flatten: bool = True,
    analyze_only: bool = False,
    generate_report: bool = True,
    report_format: str = "text"
) -> Dict:
    """
    Remediate a PDF file for accessibility compliance.

    Args:
        input_path: Path to the input PDF file
        output_path: Full path to output file (optional, will be auto-generated if not provided)
        output_dir: Directory for output file (optional, defaults to same as input)
        append_date: Whether to append date to output filename (default: True)
        title: Document title (optional, will use filename if not provided)
        author: Document author (optional)
        subject: Document subject (optional)
        keywords: Document keywords (optional)
        language: Document language code (default: "en-US")
        flatten: Whether to flatten PDF layers (default: True)
        analyze_only: Only analyze, don't remediate (default: False)
        generate_report: Generate a remediation report (default: True)
        report_format: Report format - "text" or "json" (default: "text")

    Returns:
        Dictionary with:
            - success: bool
            - output_file: str (path to remediated file)
            - report: str (remediation report)
            - issues_found: int
            - issues_fixed: int
            - error: str (if failed)
    """

    result = {
        "success": False,
        "output_file": None,
        "report": None,
        "issues_found": 0,
        "issues_fixed": 0,
        "error": None
    }

    try:
        # Validate input file
        input_path = Path(input_path)
        if not input_path.exists():
            result["error"] = f"Input file not found: {input_path}"
            return result

        if not input_path.suffix.lower() == '.pdf':
            result["error"] = f"Input file must be a PDF: {input_path}"
            return result

        # Determine output path
        if output_path:
            output_path = Path(output_path)
        else:
            # Auto-generate output filename
            stem = input_path.stem
            suffix = input_path.suffix

            # Add "remediated" to filename
            if append_date:
                today = datetime.now().strftime("%Y-%m-%d")
                new_name = f"{stem}_remediated_{today}{suffix}"
            else:
                new_name = f"{stem}_remediated{suffix}"

            # Determine output directory
            if output_dir:
                output_path = Path(output_dir) / new_name
            else:
                output_path = input_path.parent / new_name

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize remediator
        print(f"Loading PDF: {input_path}")
        remediator = EnhancedPDFRemediator(str(input_path), str(output_path))

        if not remediator.load_pdf():
            result["error"] = "Failed to load PDF"
            return result

        # Analyze PDF
        print(f"Analyzing PDF ({remediator.report.total_pages} pages)...")
        issues = remediator.analyze()
        result["issues_found"] = len(issues)

        print(f"Found {len(issues)} accessibility issues")

        # Remediate if not analyze-only
        if not analyze_only:
            print("Performing comprehensive remediation...")

            # Prepare options
            options = {
                'title': title or input_path.stem.replace('_', ' ').replace('-', ' ').title(),
                'author': author,
                'subject': subject,
                'keywords': keywords,
                'language': language,
                'flatten': flatten
            }

            fixed = remediator.remediate(options)
            result["issues_fixed"] = len(remediator.report.issues_fixed)

            print(f"Fixed {fixed} categories of issues")

            # Save remediated PDF
            print(f"Saving remediated PDF: {output_path}")
            if remediator.save():
                print("PDF saved successfully")
                result["success"] = True
                result["output_file"] = str(output_path)
            else:
                result["error"] = "Failed to save PDF"
                remediator.close()
                return result
        else:
            result["success"] = True
            result["output_file"] = None

        # Generate report
        if generate_report:
            report = remediator.generate_report(report_format)
            result["report"] = report

            if not analyze_only:
                # Save report to file
                report_file = output_path.parent / f"{output_path.stem}_report.txt"
                with open(report_file, 'w') as f:
                    f.write(report)
                print(f"Report saved to: {report_file}")

        remediator.close()

    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()

    return result


def remediate_batch(
    input_dir: str,
    output_dir: str,
    pattern: str = "*.pdf",
    **kwargs
) -> Dict:
    """
    Remediate multiple PDF files in a directory.

    Args:
        input_dir: Directory containing PDFs to remediate
        output_dir: Directory for remediated PDFs
        pattern: File pattern to match (default: "*.pdf")
        **kwargs: Additional arguments passed to remediate_pdf()

    Returns:
        Dictionary with:
            - total: int (total files processed)
            - successful: int (number of successful remediations)
            - failed: int (number of failed remediations)
            - results: list (results for each file)
    """

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # Find all PDF files
    pdf_files = list(input_dir.glob(pattern))

    results = {
        "total": len(pdf_files),
        "successful": 0,
        "failed": 0,
        "results": []
    }

    for pdf_file in pdf_files:
        print(f"\n{'='*70}")
        print(f"Processing: {pdf_file.name}")
        print(f"{'='*70}")

        result = remediate_pdf(
            input_path=str(pdf_file),
            output_dir=str(output_dir),
            **kwargs
        )

        if result["success"]:
            results["successful"] += 1
        else:
            results["failed"] += 1

        results["results"].append({
            "file": pdf_file.name,
            "result": result
        })

    print(f"\n{'='*70}")
    print(f"Batch Processing Complete")
    print(f"Total: {results['total']}, Successful: {results['successful']}, Failed: {results['failed']}")
    print(f"{'='*70}")

    return results


def main():
    """Command-line interface for the wrapper."""
    import argparse

    parser = argparse.ArgumentParser(
        description="PDF Remediator Wrapper - Easy accessibility remediation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remediate a single PDF
  %(prog)s input.pdf

  # Remediate with custom output directory
  %(prog)s input.pdf --output-dir /path/to/output

  # Remediate with metadata
  %(prog)s input.pdf --title "My Document" --author "John Doe"

  # Batch remediate all PDFs in a directory
  %(prog)s --batch /path/to/input/dir --output-dir /path/to/output/dir

  # Analyze only (no changes)
  %(prog)s input.pdf --analyze-only
        """
    )

    parser.add_argument('input', nargs='?', help='Input PDF file (or directory if --batch)')
    parser.add_argument('-o', '--output', dest='output_path', help='Output PDF file path')
    parser.add_argument('-d', '--output-dir', help='Output directory')
    parser.add_argument('--no-date', action='store_false', dest='append_date',
                       help='Do not append date to output filename')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--author', help='Document author')
    parser.add_argument('--subject', help='Document subject')
    parser.add_argument('--keywords', help='Document keywords')
    parser.add_argument('--language', default='en-US', help='Document language (default: en-US)')
    parser.add_argument('--no-flatten', action='store_false', dest='flatten',
                       help='Skip flattening PDF layers')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze, do not remediate')
    parser.add_argument('--no-report', action='store_false', dest='generate_report',
                       help='Do not generate report')
    parser.add_argument('--report-format', choices=['text', 'json'], default='text',
                       help='Report format (default: text)')
    parser.add_argument('--batch', action='store_true',
                       help='Batch mode - remediate all PDFs in input directory')
    parser.add_argument('--pattern', default='*.pdf',
                       help='File pattern for batch mode (default: *.pdf)')

    args = parser.parse_args()

    if not args.input:
        parser.error("input is required")

    if args.batch:
        # Batch mode
        if not args.output_dir:
            parser.error("--output-dir is required in batch mode")

        result = remediate_batch(
            input_dir=args.input,
            output_dir=args.output_dir,
            pattern=args.pattern,
            append_date=args.append_date,
            title=args.title,
            author=args.author,
            subject=args.subject,
            keywords=args.keywords,
            language=args.language,
            flatten=args.flatten,
            analyze_only=args.analyze_only,
            generate_report=args.generate_report,
            report_format=args.report_format
        )

        sys.exit(0 if result["failed"] == 0 else 1)
    else:
        # Single file mode
        result = remediate_pdf(
            input_path=args.input,
            output_path=args.output_path,
            output_dir=args.output_dir,
            append_date=args.append_date,
            title=args.title,
            author=args.author,
            subject=args.subject,
            keywords=args.keywords,
            language=args.language,
            flatten=args.flatten,
            analyze_only=args.analyze_only,
            generate_report=args.generate_report,
            report_format=args.report_format
        )

        if not result["success"]:
            print(f"\nError: {result['error']}")
            if "traceback" in result:
                print(result["traceback"])
            sys.exit(1)

        print("\nDone!")
        sys.exit(0)


if __name__ == '__main__':
    main()
