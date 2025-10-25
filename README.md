# PDF Remediator - WCAG 2.2 AA Compliance Tool

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![WCAG](https://img.shields.io/badge/WCAG-2.2%20AA-success)](https://www.w3.org/WAI/WCAG22/quickref/)

A comprehensive Python tool for remediating PDF documents to meet WCAG 2.2 Level AA accessibility standards. Automatically tags content, adds alt text, optimizes reading order, and ensures PDFs are fully accessible to screen readers.

## Features

### 🎯 Core Capabilities

- **⚠️ OCR Detection** *(NEW v2.4)*: Automatically detects graphically-rendered PDFs requiring OCR before remediation
- **🤖 AI-Powered Alt Text** *(NEW)*: Uses Claude/GPT-4 vision to generate context-aware, WCAG-compliant alt-text
- **🔧 Tag Correction** *(NEW v2.3)*: Automatically detects and fixes incorrectly placed structure tags
- **🎯 Tag-Aware Remediation** *(v2.2)*: Automatically detects and preserves existing proper tags, preventing duplicates
- **Intelligent Image Tagging**: Automatically detects decorative vs. descriptive images, including full-page backgrounds
- **Alt Text Generation**: Context-aware alt text for all images (heuristic or AI)
- **Artifact Marking**: Ensures all content is either tagged or marked as decorative artifacts
- **Document Structure**: Complete tagging (headings, paragraphs, lists, tables)
- **Table Formatting**: Header detection and summary generation
- **Link Improvement**: Converts generic link text to descriptive alternatives
- **Reading Order**: Optimizes content flow for screen readers
- **Layer Flattening**: Processes layered PDFs for proper tagging
- **Metadata Management**: Complete document metadata configuration

### ✅ WCAG 2.2 AA Compliance

| Criterion | Coverage |
|-----------|----------|
| 1.1.1 Non-text Content | ✓ Alt text (decorative vs descriptive) |
| 1.3.1 Info and Relationships | ✓ Document structure, tables, headings, **artifact marking** |
| 1.3.2 Meaningful Sequence | ✓ Reading order optimization |
| 2.4.2 Page Titled | ✓ Document title |
| 2.4.4 Link Purpose | ✓ Descriptive link text |
| 2.4.6 Headings and Labels | ✓ Heading hierarchy |
| 3.1.1 Language of Page | ✓ Document language |
| 4.1.2 Name, Role, Value | ✓ Form field labels |

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/adasheasu/pdfremediator.git
cd pdfremediator

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Remediate a PDF with automatic features
python pdf_remediator.py input.pdf

# With AI-powered alt-text (NEW!)
python pdf_remediator.py input.pdf --use-ai-alt-text

# Specify output file and metadata
python pdf_remediator.py input.pdf \
  -o output.pdf \
  --title "Document Title" \
  --author "Author Name" \
  --language "en-US"
```

### 🤖 AI Alt-Text Generation *(NEW)*

Generate high-quality, context-aware alt-text using AI vision models:

```bash
# Install AI dependencies
pip install anthropic  # or: pip install openai

# Set API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Use AI alt-text
python pdf_remediator.py input.pdf --use-ai-alt-text
```

**See [AI_QUICK_START.md](AI_QUICK_START.md) for full guide**

### Analyze Only (No Changes)

```bash
# Check accessibility issues without modifying the file
python pdf_remediator.py input.pdf --analyze-only
```

## Requirements

- Python 3.7 or higher
- pikepdf 8.0.0 or higher
- Compatible with Windows, macOS, and Linux

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [Usage Guide](docs/USAGE.md) - Comprehensive usage examples
- [API Reference](docs/API.md) - Python API documentation
- [Enhanced Features](docs/ENHANCED_FEATURES.md) - Advanced capabilities
- **[OCR Detection Guide](OCR_DETECTION_GUIDE.md)** - *(NEW v2.4)* Automatic graphically-rendered PDF detection
- **[AI Alt-Text Quick Start](AI_QUICK_START.md)** - *(NEW)* Get started with AI in 5 minutes
- **[AI Alt-Text Guide](docs/AI_ALT_TEXT_GUIDE.md)** - *(NEW)* Complete AI features guide
- **[AI API Comparison](docs/AI_VISION_API_COMPARISON.md)** - *(NEW)* Provider comparison
- **[Tag Correction Guide](TAG_CORRECTION_GUIDE.md)** - *(NEW v2.3)* Automatic tag type validation and correction
- **[Tag Detection Guide](TAG_DETECTION_GUIDE.md)** - *(v2.2)* Smart tag-aware remediation
- [Contributing](CONTRIBUTING.md) - How to contribute

## Examples

### Complete Remediation

```bash
python pdf_remediator.py document.pdf \
  --title "Annual Report 2024" \
  --author "Jane Doe" \
  --subject "Financial Analysis" \
  --keywords "finance, report, 2024" \
  --language "en-US"
```

### Generate JSON Report

```bash
python pdf_remediator.py document.pdf \
  --report-format json \
  --report-file report.json
```

### Skip Layer Flattening

```bash
python pdf_remediator.py document.pdf --no-flatten
```

## Output Example

```
ENHANCED PDF ACCESSIBILITY REMEDIATION REPORT
======================================================================
Input File:  document.pdf
Output File: document_remediated.pdf
Total Pages: 15

REMEDIATION STATISTICS
----------------------------------------------------------------------
Images Tagged:           12
  - Decorative:          3
  - Descriptive:         9
Tables Tagged:           2
Headings Tagged:         5
Tag Types Corrected:     3
Hierarchy Issues Fixed:  1
Artifacts Marked:        2
Links Fixed:             8

WCAG 2.2 AA Compliance: 100%
```

## What Gets Automatically Fixed

1. ✅ **Document Title** - Sets descriptive title
2. ✅ **Language** - Specifies document language
3. ✅ **Structure Tree** - Creates complete tagging structure
4. ✅ **Image Alt Text** - Adds contextual descriptions
5. ✅ **Decorative Images** - Marks appropriately
6. ✅ **Tag Type Validation** - Corrects incorrectly placed structure tags *(NEW v2.3)*
7. ✅ **Heading Hierarchy** - Fixes skipped levels and ensures proper order *(NEW v2.3)*
8. ✅ **Artifact Marking** - Marks unmarked content as decorative artifacts
9. ✅ **Reading Order** - Optimizes for screen readers
10. ✅ **Link Text** - Improves generic links
11. ✅ **Table Structure** - Adds headers and summaries
12. ✅ **Metadata** - Complete document properties
13. ✅ **Layer Flattening** - Enables proper tagging

## Manual Review Required

Some accessibility improvements require human judgment:

- Review auto-generated alt text for accuracy
- Verify complex table structures
- Check heading hierarchy
- Validate color contrast (4.5:1 ratio)
- Test with screen readers (NVDA, JAWS, VoiceOver)

## Command-Line Options

```
usage: pdf_remediator.py [-h] [-o OUTPUT] [--analyze-only]
                          [--title TITLE] [--author AUTHOR]
                          [--subject SUBJECT] [--keywords KEYWORDS]
                          [--language LANGUAGE] [--flatten | --no-flatten]
                          [--report-format {text,json}]
                          [--report-file REPORT_FILE]
                          input

positional arguments:
  input                 Input PDF file

optional arguments:
  -h, --help            Show help message
  -o OUTPUT             Output PDF file
  --analyze-only        Only analyze, do not remediate
  --title TITLE         Document title
  --author AUTHOR       Document author
  --subject SUBJECT     Document subject
  --keywords KEYWORDS   Document keywords
  --language LANGUAGE   Document language (default: en-US)
  --flatten             Flatten PDF layers (default: True)
  --no-flatten          Skip flattening PDF layers
  --report-format       Report format (text or json)
  --report-file         Save report to file
```

## Python API

```python
from pdf_remediator import EnhancedPDFRemediator

# Initialize
remediator = EnhancedPDFRemediator(
    input_path="input.pdf",
    output_path="output.pdf"
)

# Load and analyze
remediator.load_pdf()
issues = remediator.analyze()

# Remediate
options = {
    'title': 'My Document',
    'author': 'Author Name',
    'language': 'en-US',
    'flatten': True
}
remediator.remediate(options)

# Save
remediator.save()
report = remediator.generate_report(format='json')
remediator.close()
```

## How It Works

### Intelligent Image Classification

```python
# Automatic decorative detection
if image.width < 20 or image.height < 20:
    → Decorative (empty alt text)
elif aspect_ratio > 20 or aspect_ratio < 0.05:
    → Decorative (lines, borders)
elif area < 400 pixels:
    → Decorative (small icons)
else:
    → Descriptive (contextual alt text)
```

### Alt Text Generation

- **Wide images** (ratio > 2): "Diagram or illustration"
- **Tall images** (ratio < 0.5): "Vertical graphic"
- **Large images** (>400x400): "Figure or photograph"
- **Medium images**: "Graphic element"

### Link Improvement

Detects and fixes generic link text:
- "click here" → "Link to [domain]"
- "read more" → Descriptive URL-based text
- "here" → Contextual description

## Limitations

### Current Capabilities

- ✅ Automated structure tagging
- ✅ Basic alt text generation
- ✅ Reading order optimization
- ✅ Metadata management
- ✅ Layer flattening

### Requires Manual Tools

For complex documents, use professional tools:

- **Adobe Acrobat Pro DC** - Full tagging editor
- **CommonLook PDF** - Advanced remediation
- **Foxit PhantomPDF** - Table editor
- **PAC 3** - Accessibility validation

### Use Cases Requiring Manual Review

- Complex multi-column layouts
- Mathematical formulas (MathML)
- Scanned documents (OCR first)
- Forms with complex validation
- Embedded multimedia

## Testing

Test your remediated PDFs with:

- **Screen Readers**: NVDA, JAWS, VoiceOver, TalkBack
- **Validation Tools**: PAC 3, Adobe Accessibility Checker
- **Manual Review**: Reading order, alt text accuracy
- **Color Contrast**: WebAIM Contrast Checker

## Troubleshooting

### Issue: pikepdf not found

```bash
pip install pikepdf
```

### Issue: Xcode license (macOS)

```bash
sudo xcodebuild -license
```

### Issue: Permission denied

```bash
chmod +x pdf_remediator.py
```

### Issue: Images not tagged correctly

Review decorative detection thresholds in `ImageInfo.determine_if_decorative()`

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- OCR integration for scanned PDFs
- Machine learning for better alt text
- Automatic heading detection from fonts
- Form field auto-labeling
- Color contrast checking
- Batch processing capabilities

## Version History

### v2.4 - OCR Detection (Current - January 2025)
- **NEW**: Automatic detection of graphically-rendered PDFs
- **NEW**: CID-encoded font detection in content streams
- **NEW**: Large background image detection (>1500px)
- **NEW**: Prominent warning message with OCR recommendations
- **ENHANCED**: Image classification marks full-page backgrounds as decorative
- **ENHANCED**: Critical accessibility issue added for OCR-required PDFs
- See [OCR_DETECTION_GUIDE.md](OCR_DETECTION_GUIDE.md) for details

### v2.3 - Tag Correction (January 2025)
- **NEW**: Automatic tag type validation and correction
- **NEW**: Detects and fixes incorrectly placed structure tags (e.g., Image tagged as Table)
- **NEW**: Heading hierarchy correction (fixes skipped levels, ensures H1 start)
- **NEW**: Structure element type mismatch detection
- **NEW**: In-place tag type correction preserving content
- **ENHANCED**: More robust structure tree validation
- **ENHANCED**: Better error detection and reporting
- See [TAG_CORRECTION_GUIDE.md](TAG_CORRECTION_GUIDE.md) for details

### v2.2 - Tag-Aware Remediation (January 2025)
- **NEW**: Intelligent tag detection for images, tables, headings, and reading order
- **NEW**: Quality validation for existing alt-text
- **NEW**: Automatic skip of properly tagged content
- **ENHANCED**: Prevents duplicate tag creation on already-tagged PDFs
- **ENHANCED**: Preserves high-quality manual tagging work
- **ENHANCED**: Faster processing of already-tagged PDFs (skips what's done)
- See [TAG_DETECTION_GUIDE.md](TAG_DETECTION_GUIDE.md) for details

### v2.1 - Artifact Marking (October 2025)
- **NEW**: Artifact marking for unmarked content
- **NEW**: Ensures all content is either tagged or marked as decorative
- **ENHANCED**: WCAG 1.3.1 compliance with artifact detection
- **ENHANCED**: Reporting includes artifacts_marked statistic
- Intelligent image classification
- Automatic alt text generation
- Complete structure tagging
- Table structure with summaries
- Link description improvements
- Reading order optimization
- PDF layer flattening
- Enhanced reporting

### v2.0 - Enhanced
- Intelligent image classification
- Automatic alt text generation
- Complete structure tagging
- Table structure with summaries
- Link description improvements
- Reading order optimization
- PDF layer flattening
- Enhanced reporting

### v1.0 - Basic
- Document title and language
- Basic structure tree
- Simple image detection
- Basic metadata

## Resources

### WCAG Guidelines
- [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [PDF Techniques](https://www.w3.org/WAI/WCAG22/Techniques/#pdf)

### PDF Accessibility
- [PDF/UA Standard](https://www.pdfa.org/pdf-ua-universal-accessibility/)
- [WebAIM PDF Guide](https://webaim.org/techniques/acrobat/)

### Testing Tools
- [PAC 3](https://www.access-for-all.ch/en/pdf-lab/pdf-accessibility-checker-pac.html)
- [NVDA Screen Reader](https://www.nvaccess.org/)
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)

## Support

### Getting Help

1. Check the [documentation](docs/)
2. Review [examples](examples/)
3. Search [issues](https://github.com/adasheasu/pdfremediator/issues)
4. Create a new issue with details

### Professional Support

For production-level accessibility compliance:
- Hire certified accessibility professionals
- Use enterprise accessibility tools
- Conduct professional audits
- Get third-party validation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [pikepdf](https://github.com/pikepdf/pikepdf)
- WCAG guidelines by [W3C](https://www.w3.org/WAI/)
- Inspired by the need for accessible digital content

## Citation

If you use this tool in your research or projects, please cite:

```bibtex
@software{pdf_remediator,
  title = {PDF Remediator: WCAG 2.2 AA Compliance Tool},
  author = {Adashe ASU},
  year = {2025},
  url = {https://github.com/adasheasu/pdfremediator}
}
```

## Disclaimer

This tool provides automated accessibility improvements. Always:
- Review outputs for accuracy
- Test with screen readers
- Validate with accessibility checkers
- Consider professional review for critical documents
- Comply with legal accessibility requirements

## Contact

- **Issues**: [GitHub Issues](https://github.com/adasheasu/pdfremediator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adasheasu/pdfremediator/discussions)

---

**Made with ❤️ for accessibility**

*Last Updated: January 2025*
