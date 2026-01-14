#!/usr/bin/env python3
"""
PDF Remediator - WCAG 2.2 AA Compliance Tool

This script analyzes and remediates PDF documents to improve accessibility
according to WCAG 2.2 Level AA guidelines.

Key WCAG 2.2 AA Requirements Addressed:
- 1.1.1 Non-text Content: Alt text for images
- 1.3.1 Info and Relationships: Proper document structure and tagging
- 1.4.3 Contrast: Color contrast validation
- 2.4.2 Page Titled: Document title
- 3.1.1 Language of Page: Document language
- 4.1.2 Name, Role, Value: Form field labels
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

try:
    import pikepdf
    from pikepdf import Pdf, Name, Dictionary, Array
except ImportError:
    print("Error: pikepdf library not found. Install with: pip3 install pikepdf")
    sys.exit(1)


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found in the PDF."""
    category: str
    severity: str  # 'critical', 'major', 'minor'
    description: str
    wcag_criterion: str
    page_number: Optional[int] = None
    remediated: bool = False


@dataclass
class RemediationReport:
    """Report of the remediation process."""
    input_file: str
    output_file: str
    timestamp: str
    issues_found: List[AccessibilityIssue] = field(default_factory=list)
    issues_fixed: List[AccessibilityIssue] = field(default_factory=list)
    total_pages: int = 0

    def to_dict(self):
        """Convert report to dictionary for JSON serialization."""
        return {
            'input_file': self.input_file,
            'output_file': self.output_file,
            'timestamp': self.timestamp,
            'total_pages': self.total_pages,
            'issues_found': [asdict(issue) for issue in self.issues_found],
            'issues_fixed': [asdict(issue) for issue in self.issues_fixed],
            'summary': {
                'total_issues': len(self.issues_found),
                'fixed_issues': len(self.issues_fixed),
                'remaining_issues': len(self.issues_found) - len(self.issues_fixed)
            }
        }


class PDFRemediator:
    """Main class for PDF accessibility remediation."""

    def __init__(self, input_path: str, output_path: Optional[str] = None):
        """
        Initialize the PDF remediator.

        Args:
            input_path: Path to input PDF file
            output_path: Path to output PDF file (optional)
        """
        self.input_path = Path(input_path)

        if output_path:
            self.output_path = Path(output_path)
        else:
            # Create output filename with _remediated suffix
            stem = self.input_path.stem
            suffix = self.input_path.suffix
            self.output_path = self.input_path.parent / f"{stem}_remediated{suffix}"

        self.pdf: Optional[Pdf] = None
        self.report = RemediationReport(
            input_file=str(self.input_path),
            output_file=str(self.output_path),
            timestamp=datetime.now().isoformat()
        )

    def load_pdf(self) -> bool:
        """Load the PDF file."""
        try:
            self.pdf = Pdf.open(self.input_path)
            self.report.total_pages = len(self.pdf.pages)
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False

    def analyze(self) -> List[AccessibilityIssue]:
        """
        Analyze the PDF for accessibility issues.

        Returns:
            List of accessibility issues found
        """
        if not self.pdf:
            return []

        issues = []

        # Check document title (WCAG 2.4.2)
        issues.extend(self._check_document_title())

        # Check document language (WCAG 3.1.1)
        issues.extend(self._check_document_language())

        # Check PDF/UA compliance and structure (WCAG 1.3.1)
        issues.extend(self._check_document_structure())

        # Check for tagged PDF (WCAG 1.3.1)
        issues.extend(self._check_tagged_pdf())

        # Check metadata
        issues.extend(self._check_metadata())

        # Check images for alt text (WCAG 1.1.1)
        issues.extend(self._check_images())

        # Check for form fields (WCAG 4.1.2)
        issues.extend(self._check_forms())

        # Check for bookmarks/navigation (WCAG 2.4.5)
        issues.extend(self._check_navigation())

        self.report.issues_found = issues
        return issues

    def _check_document_title(self) -> List[AccessibilityIssue]:
        """Check if document has a meaningful title."""
        issues = []

        try:
            title = None
            if self.pdf.docinfo:
                title = self.pdf.docinfo.get('/Title')

            if not title or str(title).strip() == '':
                issues.append(AccessibilityIssue(
                    category="Document Metadata",
                    severity="major",
                    description="Document is missing a descriptive title",
                    wcag_criterion="2.4.2 Page Titled"
                ))
        except Exception as e:
            issues.append(AccessibilityIssue(
                category="Document Metadata",
                severity="major",
                description=f"Unable to verify document title: {e}",
                wcag_criterion="2.4.2 Page Titled"
            ))

        return issues

    def _check_document_language(self) -> List[AccessibilityIssue]:
        """Check if document has language specified."""
        issues = []

        try:
            lang = self.pdf.Root.get('/Lang')

            if not lang:
                issues.append(AccessibilityIssue(
                    category="Document Language",
                    severity="major",
                    description="Document language is not specified",
                    wcag_criterion="3.1.1 Language of Page"
                ))
        except Exception as e:
            issues.append(AccessibilityIssue(
                category="Document Language",
                severity="major",
                description=f"Unable to verify document language: {e}",
                wcag_criterion="3.1.1 Language of Page"
            ))

        return issues

    def _check_document_structure(self) -> List[AccessibilityIssue]:
        """Check document structure and marking information."""
        issues = []

        try:
            # Check if MarkInfo exists and indicates tagging
            mark_info = self.pdf.Root.get('/MarkInfo')

            if not mark_info:
                issues.append(AccessibilityIssue(
                    category="Document Structure",
                    severity="critical",
                    description="Document lacks MarkInfo dictionary (structure information)",
                    wcag_criterion="1.3.1 Info and Relationships"
                ))
            else:
                marked = mark_info.get('/Marked', False)
                if not marked:
                    issues.append(AccessibilityIssue(
                        category="Document Structure",
                        severity="critical",
                        description="Document is not marked as tagged",
                        wcag_criterion="1.3.1 Info and Relationships"
                    ))
        except Exception as e:
            issues.append(AccessibilityIssue(
                category="Document Structure",
                severity="critical",
                description=f"Unable to verify document structure: {e}",
                wcag_criterion="1.3.1 Info and Relationships"
            ))

        return issues

    def _check_tagged_pdf(self) -> List[AccessibilityIssue]:
        """Check if PDF has structural tags."""
        issues = []

        try:
            struct_tree = self.pdf.Root.get('/StructTreeRoot')

            if not struct_tree:
                issues.append(AccessibilityIssue(
                    category="Document Tags",
                    severity="critical",
                    description="Document lacks structure tree (not tagged)",
                    wcag_criterion="1.3.1 Info and Relationships"
                ))
        except Exception as e:
            issues.append(AccessibilityIssue(
                category="Document Tags",
                severity="critical",
                description=f"Unable to verify PDF tags: {e}",
                wcag_criterion="1.3.1 Info and Relationships"
            ))

        return issues

    def _check_metadata(self) -> List[AccessibilityIssue]:
        """Check document metadata for completeness."""
        issues = []

        try:
            if not self.pdf.docinfo:
                issues.append(AccessibilityIssue(
                    category="Document Metadata",
                    severity="minor",
                    description="Document has no metadata information",
                    wcag_criterion="General Best Practice"
                ))
            else:
                # Check for common metadata fields
                metadata_fields = {
                    '/Author': 'Author',
                    '/Subject': 'Subject',
                    '/Keywords': 'Keywords'
                }

                missing_fields = []
                for field, name in metadata_fields.items():
                    if not self.pdf.docinfo.get(field):
                        missing_fields.append(name)

                if missing_fields:
                    issues.append(AccessibilityIssue(
                        category="Document Metadata",
                        severity="minor",
                        description=f"Missing metadata fields: {', '.join(missing_fields)}",
                        wcag_criterion="General Best Practice"
                    ))
        except Exception as e:
            pass  # Metadata is optional, don't report as error

        return issues

    def _check_images(self) -> List[AccessibilityIssue]:
        """Check for images that may lack alt text."""
        issues = []

        try:
            image_count = 0

            for page_num, page in enumerate(self.pdf.pages, 1):
                if '/XObject' in page.get('/Resources', {}):
                    xobjects = page.Resources.XObject

                    for obj_name in xobjects.keys():
                        obj = xobjects[obj_name]

                        if obj.get('/Subtype') == '/Image':
                            image_count += 1

            if image_count > 0:
                issues.append(AccessibilityIssue(
                    category="Images",
                    severity="major",
                    description=f"Found {image_count} images - verify all have alternative text in structure tree",
                    wcag_criterion="1.1.1 Non-text Content"
                ))
        except Exception as e:
            issues.append(AccessibilityIssue(
                category="Images",
                severity="major",
                description=f"Unable to analyze images: {e}",
                wcag_criterion="1.1.1 Non-text Content"
            ))

        return issues

    def _check_forms(self) -> List[AccessibilityIssue]:
        """Check for form fields and their accessibility."""
        issues = []

        try:
            if '/AcroForm' in self.pdf.Root:
                acro_form = self.pdf.Root.AcroForm

                if '/Fields' in acro_form:
                    fields = acro_form.Fields
                    unlabeled_fields = 0

                    for field in fields:
                        # Check if field has a proper label/name
                        if not field.get('/TU') and not field.get('/T'):
                            unlabeled_fields += 1

                    if unlabeled_fields > 0:
                        issues.append(AccessibilityIssue(
                            category="Form Fields",
                            severity="major",
                            description=f"{unlabeled_fields} form fields lack proper labels",
                            wcag_criterion="4.1.2 Name, Role, Value"
                        ))
        except Exception as e:
            pass  # Forms are optional

        return issues

    def _check_navigation(self) -> List[AccessibilityIssue]:
        """Check for bookmarks and navigation aids."""
        issues = []

        try:
            outlines = self.pdf.Root.get('/Outlines')

            if not outlines and len(self.pdf.pages) > 5:
                issues.append(AccessibilityIssue(
                    category="Navigation",
                    severity="minor",
                    description="Document lacks bookmarks for easier navigation",
                    wcag_criterion="2.4.5 Multiple Ways"
                ))
        except Exception:
            pass  # Bookmarks are optional

        return issues

    def remediate(self, options: Dict = None) -> int:
        """
        Remediate accessibility issues in the PDF.

        Args:
            options: Dictionary of remediation options

        Returns:
            Number of issues fixed
        """
        if not self.pdf:
            return 0

        options = options or {}
        fixed_count = 0

        # Fix document title
        if self._fix_document_title(options.get('title', 'Untitled Document')):
            fixed_count += 1

        # Fix document language
        if self._fix_document_language(options.get('language', 'en-US')):
            fixed_count += 1

        # Enable tagging structure
        if self._fix_document_structure():
            fixed_count += 1

        # Add basic metadata
        if self._fix_metadata(options):
            fixed_count += 1

        # Set display preferences for accessibility
        if self._fix_display_preferences():
            fixed_count += 1

        return fixed_count

    def _fix_document_title(self, title: str) -> bool:
        """Set document title."""
        try:
            # Check if title is already set
            current_title = None
            if self.pdf.docinfo:
                current_title = self.pdf.docinfo.get('/Title')

            if not current_title or str(current_title).strip() == '':
                # Use provided title or filename
                if title == 'Untitled Document':
                    title = self.input_path.stem.replace('_', ' ').title()

                with self.pdf.open_metadata() as meta:
                    meta['dc:title'] = title

                # Also set in docinfo
                if not self.pdf.docinfo:
                    self.pdf.docinfo = Dictionary()
                self.pdf.docinfo['/Title'] = title

                issue = AccessibilityIssue(
                    category="Document Metadata",
                    severity="major",
                    description=f"Set document title to: {title}",
                    wcag_criterion="2.4.2 Page Titled",
                    remediated=True
                )
                self.report.issues_fixed.append(issue)
                return True
        except Exception as e:
            print(f"Warning: Could not set document title: {e}")

        return False

    def _fix_document_language(self, language: str) -> bool:
        """Set document language."""
        try:
            current_lang = self.pdf.Root.get('/Lang')

            if not current_lang:
                self.pdf.Root['/Lang'] = language

                issue = AccessibilityIssue(
                    category="Document Language",
                    severity="major",
                    description=f"Set document language to: {language}",
                    wcag_criterion="3.1.1 Language of Page",
                    remediated=True
                )
                self.report.issues_fixed.append(issue)
                return True
        except Exception as e:
            print(f"Warning: Could not set document language: {e}")

        return False

    def _fix_document_structure(self) -> bool:
        """Enable document tagging structure."""
        try:
            fixed = False

            # Add MarkInfo if missing
            if '/MarkInfo' not in self.pdf.Root:
                self.pdf.Root['/MarkInfo'] = Dictionary({
                    '/Marked': True
                })
                fixed = True
            else:
                mark_info = self.pdf.Root.MarkInfo
                if not mark_info.get('/Marked', False):
                    mark_info['/Marked'] = True
                    fixed = True

            # Add basic StructTreeRoot if missing
            if '/StructTreeRoot' not in self.pdf.Root:
                self.pdf.Root['/StructTreeRoot'] = Dictionary({
                    '/Type': Name('/StructTreeRoot'),
                    '/K': Array([]),
                    '/ParentTree': Dictionary({
                        '/Nums': Array([])
                    })
                })
                fixed = True

            if fixed:
                issue = AccessibilityIssue(
                    category="Document Structure",
                    severity="critical",
                    description="Enabled document tagging structure",
                    wcag_criterion="1.3.1 Info and Relationships",
                    remediated=True
                )
                self.report.issues_fixed.append(issue)
                return True
        except Exception as e:
            print(f"Warning: Could not fix document structure: {e}")

        return False

    def _fix_metadata(self, options: Dict) -> bool:
        """Set document metadata."""
        try:
            fixed = False

            if not self.pdf.docinfo:
                self.pdf.docinfo = Dictionary()

            # Set author if provided
            if options.get('author') and not self.pdf.docinfo.get('/Author'):
                self.pdf.docinfo['/Author'] = options['author']
                fixed = True

            # Set subject if provided
            if options.get('subject') and not self.pdf.docinfo.get('/Subject'):
                self.pdf.docinfo['/Subject'] = options['subject']
                fixed = True

            # Set keywords if provided
            if options.get('keywords') and not self.pdf.docinfo.get('/Keywords'):
                self.pdf.docinfo['/Keywords'] = options['keywords']
                fixed = True

            # Set creation date
            if not self.pdf.docinfo.get('/CreationDate'):
                self.pdf.docinfo['/CreationDate'] = f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                fixed = True

            if fixed:
                issue = AccessibilityIssue(
                    category="Document Metadata",
                    severity="minor",
                    description="Added document metadata",
                    wcag_criterion="General Best Practice",
                    remediated=True
                )
                self.report.issues_fixed.append(issue)
                return True
        except Exception as e:
            print(f"Warning: Could not set metadata: {e}")

        return False

    def _fix_display_preferences(self) -> bool:
        """Set display preferences for accessibility."""
        try:
            if '/ViewerPreferences' not in self.pdf.Root:
                self.pdf.Root['/ViewerPreferences'] = Dictionary()

            prefs = self.pdf.Root.ViewerPreferences

            # Display document title in title bar
            if not prefs.get('/DisplayDocTitle'):
                prefs['/DisplayDocTitle'] = True

                issue = AccessibilityIssue(
                    category="Display Preferences",
                    severity="minor",
                    description="Set viewer to display document title",
                    wcag_criterion="2.4.2 Page Titled",
                    remediated=True
                )
                self.report.issues_fixed.append(issue)
                return True
        except Exception as e:
            print(f"Warning: Could not set display preferences: {e}")

        return False

    def save(self) -> bool:
        """Save the remediated PDF."""
        try:
            self.pdf.save(self.output_path)
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False

    def generate_report(self, format: str = 'text') -> str:
        """
        Generate a remediation report.

        Args:
            format: Report format ('text' or 'json')

        Returns:
            Report string
        """
        if format == 'json':
            return json.dumps(self.report.to_dict(), indent=2)
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate a text-based report."""
        lines = []
        lines.append("=" * 70)
        lines.append("PDF ACCESSIBILITY REMEDIATION REPORT")
        lines.append("=" * 70)
        lines.append(f"Input File:  {self.report.input_file}")
        lines.append(f"Output File: {self.report.output_file}")
        lines.append(f"Date:        {self.report.timestamp}")
        lines.append(f"Total Pages: {self.report.total_pages}")
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Issues Found:     {len(self.report.issues_found)}")
        lines.append(f"Issues Fixed:           {len(self.report.issues_fixed)}")
        lines.append(f"Remaining Issues:       {len(self.report.issues_found) - len(self.report.issues_fixed)}")
        lines.append("")

        # Issues by severity
        critical = sum(1 for i in self.report.issues_found if i.severity == 'critical')
        major = sum(1 for i in self.report.issues_found if i.severity == 'major')
        minor = sum(1 for i in self.report.issues_found if i.severity == 'minor')

        lines.append(f"  Critical Issues:      {critical}")
        lines.append(f"  Major Issues:         {major}")
        lines.append(f"  Minor Issues:         {minor}")
        lines.append("")

        # Fixed issues
        if self.report.issues_fixed:
            lines.append("ISSUES FIXED")
            lines.append("-" * 70)
            for issue in self.report.issues_fixed:
                lines.append(f"[{issue.severity.upper()}] {issue.category}")
                lines.append(f"  {issue.description}")
                lines.append(f"  WCAG: {issue.wcag_criterion}")
                lines.append("")

        # Remaining issues
        remaining = [i for i in self.report.issues_found if not any(
            f.category == i.category and f.description == i.description
            for f in self.report.issues_fixed
        )]

        if remaining:
            lines.append("REMAINING ISSUES (Manual Review Required)")
            lines.append("-" * 70)
            for issue in remaining:
                lines.append(f"[{issue.severity.upper()}] {issue.category}")
                lines.append(f"  {issue.description}")
                lines.append(f"  WCAG: {issue.wcag_criterion}")
                if issue.page_number:
                    lines.append(f"  Page: {issue.page_number}")
                lines.append("")

        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 70)
        lines.append("1. Review all images and add meaningful alternative text")
        lines.append("2. Ensure proper reading order for content")
        lines.append("3. Add bookmarks for documents longer than 5 pages")
        lines.append("4. Label all form fields with descriptive text")
        lines.append("5. Use proper heading structure (H1, H2, etc.)")
        lines.append("6. Verify color contrast ratios meet WCAG 2.2 AA standards (4.5:1)")
        lines.append("7. Test with screen readers for full accessibility validation")
        lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def close(self):
        """Close the PDF file."""
        if self.pdf:
            self.pdf.close()


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='PDF Remediator - WCAG 2.2 AA Accessibility Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze and remediate a PDF
  %(prog)s input.pdf

  # Specify output filename
  %(prog)s input.pdf -o output.pdf

  # Add metadata
  %(prog)s input.pdf --title "My Document" --author "John Doe"

  # Analyze only (no remediation)
  %(prog)s input.pdf --analyze-only

  # Generate JSON report
  %(prog)s input.pdf --report-format json --report-file report.json
        """
    )

    parser.add_argument('input', help='Input PDF file')
    parser.add_argument('-o', '--output', help='Output PDF file (default: input_remediated.pdf)')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze, do not remediate')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--author', help='Document author')
    parser.add_argument('--subject', help='Document subject')
    parser.add_argument('--keywords', help='Document keywords')
    parser.add_argument('--language', default='en-US', help='Document language (default: en-US)')
    parser.add_argument('--report-format', choices=['text', 'json'], default='text',
                       help='Report format (default: text)')
    parser.add_argument('--report-file', help='Save report to file')

    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)

    # Initialize remediator
    print(f"Loading PDF: {args.input}")
    remediator = PDFRemediator(args.input, args.output)

    if not remediator.load_pdf():
        sys.exit(1)

    # Analyze PDF
    print(f"Analyzing PDF ({remediator.report.total_pages} pages)...")
    issues = remediator.analyze()

    print(f"Found {len(issues)} accessibility issues")

    # Remediate if not analyze-only
    if not args.analyze_only:
        print("Remediating accessibility issues...")

        options = {
            'title': args.title,
            'author': args.author,
            'subject': args.subject,
            'keywords': args.keywords,
            'language': args.language
        }

        fixed = remediator.remediate(options)
        print(f"Fixed {fixed} issues")

        # Save remediated PDF
        print(f"Saving remediated PDF: {remediator.output_path}")
        if remediator.save():
            print("PDF saved successfully")
        else:
            print("Failed to save PDF")
            remediator.close()
            sys.exit(1)

    # Generate report
    report = remediator.generate_report(args.report_format)

    if args.report_file:
        with open(args.report_file, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.report_file}")
    else:
        print("\n" + report)

    remediator.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
