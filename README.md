# PDF Remediator

Comprehensive PDF accessibility remediation tool for WCAG 2.2 Level AA compliance.

## Features

- **Intelligent Image Tagging**: Automatically distinguishes between decorative and descriptive images
- **Alt Text Generation**: Creates contextual alt text for images
- **Form Field Accessibility**: Tags form fields with proper labels and tooltips
- **Annotation Tagging**: Ensures annotations are accessible to screen readers
- **Reading Order Optimization**: Sets proper reading order for screen readers
- **PDF Layer Flattening**: Flattens layered PDFs for proper tagging
- **Metadata Management**: Sets document title, language, and metadata
- **WCAG 2.2 AA Compliance**: Comprehensive accessibility remediation

## Files

- `pdf_remediator.py` - Main enhanced PDF remediator with full WCAG 2.2 AA compliance
- `pdf_remediator_wrapper.py` - Easy-to-use wrapper for single and batch PDF remediation
- `pdf_remediator_basic.py` - Basic version of the PDF remediator
- `pdf_remediator_enhanced.py` - Enhanced version with additional features

## Installation

```bash
pip3 install pikepdf
```

## Usage

### Using the Wrapper (Recommended)

```bash
# Remediate a single PDF
python3 pdf_remediator_wrapper.py input.pdf

# Remediate with custom output directory
python3 pdf_remediator_wrapper.py input.pdf --output-dir /path/to/output

# Remediate with metadata
python3 pdf_remediator_wrapper.py input.pdf --title "My Document" --author "John Doe"

# Batch remediate all PDFs in a directory
python3 pdf_remediator_wrapper.py --batch /path/to/input/dir --output-dir /path/to/output/dir

# Analyze only (no changes)
python3 pdf_remediator_wrapper.py input.pdf --analyze-only
```

### Using the Main Script

```bash
# Full remediation
python3 pdf_remediator.py input.pdf

# Specify output filename
python3 pdf_remediator.py input.pdf -o output.pdf

# Add metadata and flatten layers
python3 pdf_remediator.py input.pdf --title "My Document" --author "John Doe" --flatten

# Generate JSON report
python3 pdf_remediator.py input.pdf --report-format json --report-file report.json
```

### Python API

```python
from pdf_remediator_wrapper import remediate_pdf

result = remediate_pdf(
    input_path="input.pdf",
    output_dir="/path/to/output",
    title="My Document",
    author="John Doe",
    language="en-US"
)

if result["success"]:
    print(f"Remediated PDF: {result['output_file']}")
    print(f"Fixed {result['issues_fixed']} issues")
else:
    print(f"Error: {result['error']}")
```

## WCAG 2.2 AA Requirements Addressed

- **1.1.1 Non-text Content**: Alt text for images (decorative vs descriptive)
- **1.3.1 Info and Relationships**: Proper document structure, headings, lists, tables
- **1.3.2 Meaningful Sequence**: Reading order
- **2.4.2 Page Titled**: Document title
- **2.4.4 Link Purpose**: Descriptive link text
- **2.4.6 Headings and Labels**: Proper heading hierarchy
- **3.1.1 Language of Page**: Document language
- **4.1.2 Name, Role, Value**: Form field labels

## Output

Each remediation generates:
- Remediated PDF with `_remediated_YYYY-MM-DD` suffix
- Text report with detailed statistics and recommendations
- Optional JSON report for automated processing

## Recommendations

After remediation:
1. Test with screen readers (NVDA, JAWS, VoiceOver)
2. Verify reading order is logical
3. Review auto-generated alt text for accuracy
4. Check table structures are semantically correct
5. Verify color contrast ratios meet WCAG 2.2 AA (4.5:1)

## License

Created for ASU accessibility compliance.

## Author

Developed by Claude Code for Alejandra Dashe
