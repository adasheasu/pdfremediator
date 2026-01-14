# Changelog

All notable changes to PDF Remediator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-10-24

### Added
- **Artifact Marking Infrastructure**: New `mark_unmarked_content_as_artifacts()` method to ensure all content in PDFs is either included in the Tags tree or explicitly marked as decorative artifacts
- **Enhanced WCAG 1.3.1 Compliance**: Automatic detection and marking of unmarked XObjects (images and Form XObjects) as artifacts
- **Artifacts Marked Statistic**: New `artifacts_marked` field in RemediationReport dataclass to track unmarked content marked as artifacts
- **Comprehensive Content Tracking**: Smart detection that tracks already-tagged content (images, form fields, annotations) to avoid duplicate marking
- **Form XObject Handling**: Automatic marking of Form XObjects (headers, footers) as artifacts when not explicitly tagged
- **Enhanced Reporting**: Updated text and JSON reports to include artifacts_marked statistics

### Changed
- **Remediation Workflow**: Integrated artifact marking as step 9.5 in the remediation process (after annotation tagging, before link fixing)
- **Report Output**: Added "Artifacts Marked" line to REMEDIATION STATISTICS section in text reports
- **JSON Serialization**: Updated `to_dict()` method to include artifacts_marked in statistics

### Technical Details
- New method: `mark_unmarked_content_as_artifacts()` (lines 669-790)
- Enhanced RemediationReport dataclass with artifacts_marked field
- Creates proper /Artifact structure elements with empty /Alt strings
- Implements WCAG 1.3.1 requirement that all content must be either tagged or marked as decorative
- Detects unmarked images by comparing against tagged_images set
- Handles both Image and Form XObject subtypes

### WCAG Compliance
- **Enhanced 1.3.1 Info and Relationships**: Now ensures ALL content is either in Tags tree or marked as artifact
- Maintains existing compliance for all other WCAG 2.2 AA criteria

### Files Modified
- `pdf_remediator.py`: Core remediation script with artifact marking capability
- `README.md`: Updated documentation with new feature
- `CHANGELOG.md`: New file documenting version history

## [2.0.0] - 2025-10-23

### Added
- **Form Field Tagging**: Comprehensive tagging of form fields with proper labels and tooltips
- **Annotation Tagging**: Accessibility tagging for annotations with alt text
- **Screen Reader Optimization**: Explicit configuration of MarkInfo properties for screen readers
- **Enhanced Image Tagging**: BBox, proper parent linking, and Adobe Acrobat compliance
- **Content-Aware Alt Text Validation**: Ensures alt text represents actual content, not generic descriptions
- **Annotation Overlap Protection**: Checks if images hide annotations

### Changed
- **Image Tagging**: Proper distinction between /Alt (alternative description) and /ActualText (text-in-image)
- **Structure Elements**: Enhanced with proper parent tree linking and MCID references

### Technical Details
- New method: `tag_form_fields()` for WCAG 4.1.2 compliance
- New method: `tag_annotations()` for annotation accessibility
- New method: `_set_screen_reader_preferences()` for screen reader configuration
- Enhanced `tag_images()` with validation and annotation overlap checking

## [1.0.0] - 2025-10-20

### Added
- **Initial Release**: Comprehensive PDF accessibility remediation tool
- **Intelligent Image Classification**: Automatic detection of decorative vs. descriptive images
- **Alt Text Generation**: Context-aware alt text based on image characteristics
- **Document Structure**: Complete tagging structure with StructTreeRoot
- **Reading Order**: Optimization for screen readers
- **Link Improvement**: Conversion of generic link text to descriptive alternatives
- **Layer Flattening**: Processing of layered PDFs for proper tagging
- **Metadata Management**: Complete document metadata configuration
- **WCAG 2.2 AA Compliance**: Coverage for major accessibility criteria

### Features
- Document title and language configuration
- Structure tree creation
- Image tagging (decorative vs descriptive)
- Basic table detection
- Link text improvement
- Reading order optimization
- Metadata management
- Comprehensive reporting (text and JSON formats)

### Command-Line Interface
- `-o, --output`: Specify output file
- `--analyze-only`: Analyze without remediating
- `--title`: Set document title
- `--author`: Set document author
- `--subject`: Set document subject
- `--keywords`: Set document keywords
- `--language`: Set document language (default: en-US)
- `--flatten/--no-flatten`: Control PDF layer flattening
- `--report-format`: Choose text or JSON report format
- `--report-file`: Save report to file

### WCAG Compliance
- 1.1.1 Non-text Content: Alt text for images
- 1.3.1 Info and Relationships: Document structure, tables, headings
- 1.3.2 Meaningful Sequence: Reading order optimization
- 2.4.2 Page Titled: Document title
- 2.4.4 Link Purpose: Descriptive link text
- 2.4.6 Headings and Labels: Heading hierarchy
- 3.1.1 Language of Page: Document language
- 4.1.2 Name, Role, Value: Form field labels

### Dependencies
- Python 3.7+
- pikepdf 8.0.0+

## [Unreleased]

### Planned Features
- OCR integration for scanned PDFs
- Machine learning for better alt text generation
- Automatic heading detection from font analysis
- Enhanced form field auto-labeling
- Color contrast checking
- Batch processing capabilities
- Mathematical formula support (MathML)
- Embedded multimedia handling

---

## Types of Changes
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

## Version Numbering

This project follows Semantic Versioning:
- **MAJOR** version: Incompatible API changes
- **MINOR** version: Add functionality (backward compatible)
- **PATCH** version: Bug fixes (backward compatible)

## Links
- [GitHub Repository](https://github.com/adasheasu/pdfremediator)
- [Issue Tracker](https://github.com/adasheasu/pdfremediator/issues)
- [Documentation](docs/)

---

**Note**: Version 2.1.0 represents a significant enhancement in WCAG 1.3.1 compliance
by ensuring that all content in PDF documents is either properly tagged or explicitly
marked as decorative artifacts. This addresses a critical accessibility requirement
that unmarked content must not exist in accessible PDFs.
