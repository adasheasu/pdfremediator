# Examples

Example scripts demonstrating how to use PDF Remediator.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

Simplest usage example showing:
- Loading a PDF
- Analyzing issues
- Remediating with basic options
- Viewing statistics

**Usage**:
```bash
python basic_usage.py
```

---

### 2. Batch Processing (`batch_processing.py`)

Process multiple PDFs in a directory:
- Batch remediation
- Error handling
- Progress tracking
- Summary report

**Usage**:
```bash
# Process all PDFs in input_pdfs/ directory
python batch_processing.py
```

**Configuration**:
Edit the script to change:
- Input directory
- Output directory
- Remediation options

---

### 3. Custom Alt Text (`custom_alt_text.py`)

Add custom alternative text to images:
- Analyze images first
- Apply custom descriptions
- Mark decorative images
- Full remediation

**Usage**:
```bash
python custom_alt_text.py
```

**Customization**:
Edit the `custom_alt_text` dictionary:
```python
custom_alt_text = {
    '/Im1': 'Your custom description',
    '/Im2': 'Another description',
}
```

---

## Running Examples

### Prerequisites

Ensure PDF Remediator is installed:
```bash
pip install -r requirements.txt
```

### Prepare Sample PDFs

1. **For basic_usage.py**:
   - Place your PDF as `input.pdf` in the examples directory
   - Or edit the script to change the path

2. **For batch_processing.py**:
   - Create `input_pdfs/` directory
   - Place multiple PDFs in that directory
   - Or edit the script to change paths

3. **For custom_alt_text.py**:
   - Use a PDF with images
   - Analyze images first to get their names
   - Edit custom_alt_text dictionary accordingly

---

## Example Output

### Basic Usage Output

```
Initializing PDF Remediator...
Loading: input.pdf

Analyzing PDF for accessibility issues...
Found 4 issues

Remediating PDF...

Saving: output_remediated.pdf

=== Remediation Complete ===
Images tagged: 3
  Decorative: 1
  Descriptive: 2
Tables tagged: 1
Links fixed: 2
Issues fixed: 4/4
```

### Batch Processing Output

```
Found 5 PDF files
============================================================

[1/5] Processing: document1.pdf
  Found 3 issues
  ✓ Success: 3 issues fixed

[2/5] Processing: document2.pdf
  Found 5 issues
  ✓ Success: 5 issues fixed

...

============================================================
BATCH PROCESSING SUMMARY
============================================================

Total files: 5
Successful: 4
Failed: 1

✓ Successful:
  - document1.pdf
    Issues fixed: 3/3
  - document2.pdf
    Issues fixed: 5/5
  ...

✗ Failed:
  - corrupted.pdf
    Error: PDF file is corrupted
```

---

## Customization Tips

### Change Language

```python
options = {
    'title': 'Documento',
    'language': 'es-ES'  # Spanish
}
```

### Skip Flattening

```python
options = {
    'flatten': False  # Keep PDF layers
}
```

### Add More Metadata

```python
options = {
    'title': 'Annual Report 2024',
    'author': 'Finance Department',
    'subject': 'Financial Analysis',
    'keywords': 'finance, report, revenue',
    'language': 'en-US'
}
```

### Generate JSON Report

```python
report = remediator.generate_report(format='json')

import json
with open('report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

---

## Next Steps

After trying these examples:

1. Read [Usage Guide](../docs/USAGE.md)
2. Review [API Reference](../docs/API.md)
3. Check [Enhanced Features](../docs/ENHANCED_FEATURES.md)
4. Adapt examples for your use case

---

## Troubleshooting

### "File not found" Error

- Verify PDF path is correct
- Use absolute paths if needed
- Check file permissions

### "ModuleNotFoundError"

```bash
# Install dependencies
pip install -r requirements.txt

# Or install directly
pip install pikepdf
```

### "PDF cannot be opened"

- Check PDF is not corrupted
- Remove password protection first
- Ensure file is actually a PDF

---

## Support

For questions or issues:
- Review [documentation](../docs/)
- Check [GitHub Issues](https://github.com/adasheasu/pdfremediator/issues)
- Read [USAGE.md](../docs/USAGE.md)

---

**Last Updated**: October 2025
