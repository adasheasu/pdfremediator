# Usage Guide

Comprehensive guide for using PDF Remediator to create WCAG 2.2 AA compliant PDFs.

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Command-Line Options](#command-line-options)
- [Common Workflows](#common-workflows)
- [Advanced Features](#advanced-features)
- [Python API](#python-api)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Simplest Usage

```bash
# Remediate a PDF with default settings
python pdf_remediator.py input.pdf
```

This creates `input_remediated.pdf` with:
- Document title set
- Language set to en-US
- Complete tagging structure
- Images analyzed and tagged
- Reading order optimized
- Layers flattened (if present)

### With Custom Output

```bash
# Specify output filename
python pdf_remediator.py input.pdf -o output.pdf
```

### With Metadata

```bash
# Add complete metadata
python pdf_remediator.py input.pdf \
  --title "Annual Report 2024" \
  --author "Jane Doe" \
  --subject "Financial Analysis" \
  --keywords "finance, report, 2024"
```

---

## Basic Usage

### Analyze Before Remediating

```bash
# Check what issues exist (no changes made)
python pdf_remediator.py input.pdf --analyze-only
```

**Output shows**:
- Images requiring alt text
- Decorative vs. descriptive image count
- Tables needing structure
- Links needing improvement
- Missing metadata
- Layer information

### Complete Remediation

```bash
# Full remediation with all features
python pdf_remediator.py input.pdf \
  -o output.pdf \
  --title "Document Title" \
  --author "Author Name" \
  --language "en-US"
```

### Generate Report

```bash
# Save text report
python pdf_remediator.py input.pdf \
  --report-file report.txt

# Save JSON report
python pdf_remediator.py input.pdf \
  --report-format json \
  --report-file report.json
```

---

## Command-Line Options

### Positional Arguments

```
input                 Input PDF file path (required)
```

### Optional Arguments

#### General Options

```
-h, --help           Show help message and exit
-o OUTPUT            Output PDF file path
                     Default: input_remediated.pdf
```

#### Analysis Options

```
--analyze-only       Analyze PDF without making changes
                     Useful for checking issues before remediation
```

#### Metadata Options

```
--title TITLE        Set document title
                     Example: "Annual Report 2024"

--author AUTHOR      Set document author
                     Example: "Jane Doe"

--subject SUBJECT    Set document subject
                     Example: "Financial Analysis"

--keywords KEYWORDS  Set document keywords (comma-separated)
                     Example: "finance, report, 2024"

--language LANGUAGE  Set document language (ISO 639 format)
                     Default: en-US
                     Examples: es-ES, fr-FR, de-DE, ja-JP
```

#### Processing Options

```
--flatten            Flatten PDF layers (default)
                     Enables proper tagging of layered PDFs

--no-flatten         Skip flattening PDF layers
                     Use if layers should be preserved
```

#### Reporting Options

```
--report-format {text,json}
                     Report format
                     text: Human-readable (default)
                     json: Machine-readable

--report-file FILE   Save report to file
                     Text or JSON format based on --report-format
```

---

## Common Workflows

### Workflow 1: Quick Remediation

For simple PDFs that just need basic accessibility:

```bash
python pdf_remediator.py document.pdf
```

**Result**:
- ✓ Document titled
- ✓ Language set
- ✓ Images tagged
- ✓ Structure enabled
- ✓ Reading order optimized

---

### Workflow 2: Complete Remediation

For documents requiring full metadata and compliance:

```bash
python pdf_remediator.py document.pdf \
  -o remediated_document.pdf \
  --title "Process Mapping Certificate" \
  --author "Training Department" \
  --subject "Professional Certification" \
  --keywords "process mapping, certificate, training" \
  --language "en-US"
```

**Result**:
- ✓ Complete metadata
- ✓ All images analyzed
- ✓ Decorative images identified
- ✓ Alt text added
- ✓ Reading order set
- ✓ Layers flattened
- ✓ WCAG 2.2 AA compliant

---

### Workflow 3: Analysis First, Then Remediate

Check issues before making changes:

```bash
# Step 1: Analyze
python pdf_remediator.py document.pdf --analyze-only

# Review output, then proceed

# Step 2: Remediate with findings in mind
python pdf_remediator.py document.pdf \
  --title "Document Title" \
  --author "Author Name"
```

---

### Workflow 4: Preserve Layers

For documents where layers are intentional:

```bash
python pdf_remediator.py document.pdf \
  --no-flatten \
  --title "Layered Design Document"
```

**Note**: Layered PDFs may have limited accessibility features.

---

### Workflow 5: Batch Processing

Process multiple PDFs:

```bash
#!/bin/bash
# batch_remediate.sh

for pdf in *.pdf; do
  echo "Processing: $pdf"
  python pdf_remediator.py "$pdf" \
    -o "remediated_${pdf}" \
    --title "$(basename "$pdf" .pdf)" \
    --language "en-US"
done
```

Run:
```bash
chmod +x batch_remediate.sh
./batch_remediate.sh
```

---

### Workflow 6: Generate Reports for Audit

Create detailed reports for compliance documentation:

```bash
# Generate text report
python pdf_remediator.py document.pdf \
  -o output.pdf \
  --report-file compliance_report.txt

# Generate JSON report for processing
python pdf_remediator.py document.pdf \
  -o output.pdf \
  --report-format json \
  --report-file compliance_report.json
```

---

## Advanced Features

### 1. Image Tagging

**Automatic decorative detection**:

The tool automatically identifies decorative images based on:
- Size < 20x20 pixels
- Extreme aspect ratios (>20:1 or <0.05:1)
- Total area < 400 pixels

**Example analysis output**:
```
Images Tagged:           5
  - Decorative:          2 (marked as Artifact)
  - Descriptive:         3 (alt text added)
```

**Manual override** (via Python API):
```python
# Mark specific image as decorative
remediator.mark_image_decorative('/Im1')

# Add custom alt text
remediator.add_alt_text('/Im2', 'Company logo with tagline')
```

---

### 2. Table Structure

**Automatic table detection** (when possible):

```bash
python pdf_remediator.py document.pdf
```

**Features**:
- Header row detection
- Header column identification
- Table summary generation
- Proper TH/TD tagging

**Example**:
```
Tables Tagged:           2
  - Table 1: 5 rows × 3 columns with headers
  - Table 2: 10 rows × 4 columns with headers
```

---

### 3. Link Improvement

**Detects and fixes generic link text**:

Before:
- "click here"
- "read more"
- "here"

After:
- "Link to training portal"
- "Link to course materials"
- Descriptive URL-based text

**Example**:
```
Links Fixed:             8
  - Generic text replaced with descriptive alternatives
```

---

### 4. Reading Order

**Automatic optimization**:

The tool sets:
- StructParents index for each page
- Tab order to follow structure (/S)
- Logical content flow

**Verification**:
```bash
# Test with screen reader after remediation
# NVDA (Windows), JAWS (Windows), VoiceOver (Mac)
```

---

### 5. Language Settings

**Supported language codes**:

```bash
# English (US)
--language en-US

# Spanish (Spain)
--language es-ES

# French (France)
--language fr-FR

# German
--language de-DE

# Japanese
--language ja-JP

# Chinese (Simplified)
--language zh-CN
```

**Important**: Set correct language for screen reader pronunciation.

---

## Python API

### Basic Usage

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

# Print issues
for issue in issues:
    print(f"{issue.severity}: {issue.description}")

# Remediate
options = {
    'title': 'My Document',
    'author': 'John Doe',
    'language': 'en-US',
    'flatten': True
}
remediator.remediate(options)

# Save
remediator.save()
remediator.close()
```

### Advanced API Usage

#### Image Analysis

```python
# Analyze all images
images = remediator.analyze_images()

for img in images:
    print(f"Image: {img.name}")
    print(f"  Size: {img.width}x{img.height}")
    print(f"  Decorative: {img.is_decorative}")
    print(f"  Alt text: {img.alt_text}")
    print()
```

#### Custom Alt Text

```python
# Add custom alt text
alt_text_map = {
    '/Im1': 'Company logo showing mountain peak',
    '/Im2': 'Process flow diagram: planning to execution',
    '/Im3': 'Bar chart showing quarterly revenue'
}

for img_name, alt_text in alt_text_map.items():
    remediator.add_alt_text(img_name, alt_text)
```

#### Link Analysis

```python
# Analyze links
links = remediator.analyze_links()

for link in links:
    if not link.is_descriptive:
        print(f"Non-descriptive link: {link.text}")
        print(f"  URL: {link.url}")
        print(f"  Suggested: {link.improved_text}")
```

#### Table Detection

```python
# Analyze tables
tables = remediator.analyze_tables()

for table in tables:
    print(f"Table: {table.page_number}")
    print(f"  Rows: {table.rows}")
    print(f"  Columns: {table.cols}")
    print(f"  Has headers: {table.has_headers}")
    print(f"  Summary: {table.summary}")
```

#### Generate Report

```python
# Generate text report
report_text = remediator.generate_report(format='text')
print(report_text)

# Generate JSON report
report_json = remediator.generate_report(format='json')
import json
print(json.dumps(report_json, indent=2))

# Save report to file
with open('report.txt', 'w') as f:
    f.write(report_text)
```

---

## Best Practices

### 1. Always Analyze First

```bash
# Check issues before modifying
python pdf_remediator.py document.pdf --analyze-only
```

**Benefits**:
- Understand document complexity
- Identify manual review needs
- Plan remediation approach

---

### 2. Provide Complete Metadata

```bash
# Always include at minimum:
python pdf_remediator.py document.pdf \
  --title "Descriptive Title" \
  --author "Author Name" \
  --language "en-US"
```

**Why**:
- Improves discoverability
- Helps screen readers
- Meets WCAG 2.4.2 (Page Titled)

---

### 3. Review Auto-Generated Alt Text

After remediation:

1. Open PDF in Adobe Acrobat Pro
2. Navigate to Accessibility → Reading Order
3. Review each image's alt text
4. Edit if needed for accuracy

**Or use Python API**:
```python
# Review and customize
images = remediator.analyze_images()
for img in images:
    if not img.is_decorative:
        # Customize alt text
        remediator.add_alt_text(img.name, 'Better description')
```

---

### 4. Test with Screen Readers

After remediation, test with:

- **NVDA** (Windows): Free, open-source
- **JAWS** (Windows): Industry standard
- **VoiceOver** (Mac): Built-in
- **TalkBack** (Android): Built-in

**Basic test**:
1. Open remediated PDF
2. Navigate with screen reader
3. Verify:
   - Document title announced
   - Images have alt text
   - Reading order is logical
   - Links are descriptive

---

### 5. Verify Color Contrast

The tool doesn't check color contrast. Manually verify:

- **Text**: 4.5:1 minimum (WCAG AA)
- **Large text**: 3:1 minimum (WCAG AA)
- **Graphics**: 3:1 minimum (WCAG AA)

**Tools**:
- WebAIM Contrast Checker
- Colour Contrast Analyser (CCA)
- Adobe Acrobat Accessibility Checker

---

### 6. Keep Original Files

```bash
# Always keep originals
cp original.pdf backup/original.pdf

# Then remediate
python pdf_remediator.py original.pdf -o remediated.pdf
```

---

### 7. Version Control

For important documents:

```bash
# Create versions directory
mkdir versions

# Save each version
python pdf_remediator.py document.pdf \
  -o versions/document_v1.pdf

# After edits
python pdf_remediator.py document.pdf \
  -o versions/document_v2.pdf
```

---

## Examples

### Example 1: Certificate

```bash
python pdf_remediator.py certificate.pdf \
  --title "Process Mapping Certificate" \
  --author "Training Department" \
  --subject "Professional Certification" \
  --keywords "process mapping, certificate, training"
```

**Features**:
- Logo detected as descriptive image
- Alt text: "Certificate logo and credential badge"
- Reading order optimized
- Metadata complete

---

### Example 2: Course Guide

```bash
python pdf_remediator.py course_guide.pdf \
  --title "Course Development Guide" \
  --author "Academic Affairs" \
  --subject "Instructional Design" \
  --keywords "course development, teaching, curriculum"
```

**Features**:
- Multiple images tagged
- Process diagrams identified
- Decorative separators marked
- Reading order follows document structure

---

### Example 3: Financial Report

```bash
python pdf_remediator.py report.pdf \
  --title "Q4 Financial Report 2024" \
  --author "Finance Department" \
  --subject "Quarterly Results" \
  --keywords "finance, quarterly, revenue, expenses" \
  --report-file compliance_report.txt
```

**Features**:
- Tables with headers tagged
- Charts identified
- Complete audit trail
- Compliance report generated

---

### Example 4: Multilingual Document

```bash
# Spanish document
python pdf_remediator.py documento.pdf \
  --title "Informe Anual 2024" \
  --author "Departamento de Finanzas" \
  --language "es-ES"

# French document
python pdf_remediator.py document.pdf \
  --title "Rapport Annuel 2024" \
  --author "Département des Finances" \
  --language "fr-FR"
```

---

### Example 5: Scanned Document (OCR First)

```bash
# First, OCR with external tool (e.g., Adobe Acrobat, Tesseract)
# Then remediate:

python pdf_remediator.py scanned_ocr.pdf \
  --title "Historical Document" \
  --no-flatten
```

**Note**: Always OCR before remediating scanned PDFs.

---

## Troubleshooting

### Issue: "Cannot open PDF file"

**Causes**:
- Incorrect file path
- Corrupted PDF
- Password-protected PDF

**Solutions**:
```bash
# Check file exists
ls -l document.pdf

# Try absolute path
python pdf_remediator.py /full/path/to/document.pdf

# Remove password (using qpdf)
qpdf --decrypt --password=PASSWORD input.pdf output.pdf
```

---

### Issue: "Images not tagged correctly"

**Causes**:
- Complex PDF structure
- Non-standard image encoding

**Solutions**:
```bash
# Analyze first
python pdf_remediator.py document.pdf --analyze-only

# Skip flattening if needed
python pdf_remediator.py document.pdf --no-flatten

# Manual review in Adobe Acrobat Pro
```

---

### Issue: "Reading order incorrect"

**Causes**:
- Multi-column layout
- Complex page structure

**Solutions**:
1. Remediate with tool
2. Open in Adobe Acrobat Pro
3. Use Reading Order tool to adjust
4. Save

**Or use Python API**:
```python
# Custom reading order
remediator.set_reading_order(custom_order)
```

---

### Issue: "Links not improved"

**Causes**:
- Links don't have proper annotations
- External tool created links

**Solutions**:
```bash
# Check link structure
python pdf_remediator.py document.pdf --analyze-only

# Review "Links" section in report
```

**Manual fix**:
1. Open in Adobe Acrobat Pro
2. Edit link properties
3. Add descriptive text

---

### Issue: "Layers removed important content"

**Solution**:
```bash
# Don't flatten
python pdf_remediator.py document.pdf --no-flatten
```

**Note**: Layered PDFs have limited accessibility. Consider flattening manually in Adobe Acrobat first.

---

### Issue: "Language not set correctly"

**Solution**:
```bash
# Specify correct language code
python pdf_remediator.py document.pdf --language es-ES

# Check ISO 639 language codes
# en-US, es-ES, fr-FR, de-DE, ja-JP, etc.
```

---

## Getting Help

### Documentation

1. Read [Installation Guide](INSTALLATION.md)
2. Review [Enhanced Features](ENHANCED_FEATURES.md)
3. Check [API Reference](API.md)

### Support

1. Search [GitHub Issues](https://github.com/adasheasu/pdfremediator/issues)
2. Create new issue with:
   - PDF characteristics (pages, size, complexity)
   - Command used
   - Error message (if any)
   - Expected vs. actual behavior

### Testing Resources

- **PAC 3**: https://www.access-for-all.ch/en/pdf-lab/pdf-accessibility-checker-pac.html
- **WCAG 2.2**: https://www.w3.org/WAI/WCAG22/quickref/
- **WebAIM PDF**: https://webaim.org/techniques/acrobat/

---

## Next Steps

After mastering basic usage:

1. Explore [Enhanced Features](ENHANCED_FEATURES.md)
2. Learn [Python API](API.md)
3. Review WCAG 2.2 guidelines
4. Practice with sample PDFs
5. Test with screen readers

---

**Usage Guide Version**: 2.0
**Last Updated**: October 2025
**Compliance Level**: WCAG 2.2 Level AA
