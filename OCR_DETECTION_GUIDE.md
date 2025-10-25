# OCR Detection - Graphically-Rendered PDF Detection

## Overview

Version 2.4 introduces automatic detection of graphically-rendered PDFs that require Optical Character Recognition (OCR) before remediation. This feature warns users when their PDF contains rendered graphics instead of searchable text.

## The Problem

Some PDFs are created by rendering text as graphics or vector paths rather than embedding searchable text. These PDFs:

- **Look** like they have text, but it's actually graphics
- Cannot be properly tagged for accessibility
- Text cannot be extracted or searched
- Screen readers cannot read the content
- Remediation tools can only add structural elements, not text tags

## Detection Method

The tool automatically checks for two indicators:

### 1. CID-Encoded Fonts

**What it is**: Custom Character ID encoding where characters are represented as numeric codes (`\x00\x02\x03\x04`) rather than readable text.

**Why it matters**: CID encoding is common in graphically-rendered PDFs where text is drawn as vector paths.

**Detection logic**:
```python
# Looks for sequences of low-byte values (< 32) in content streams
# Example: \x00\x02\x03\x04\x05\x06\x07\x08 indicates CID encoding
if hex_sequences > 10:  # Multiple occurrences
    has_cid_font = True
```

### 2. Large Background Images

**What it is**: Full-page or near-full-page images (>1500 pixels in either dimension)

**Why it matters**: These images typically indicate the entire page was rendered as a graphic

**Detection logic**:
```python
if image.width > 1500 or image.height > 1500:
    large_image_detected = True
```

### Combined Detection

OCR warning is triggered when:
- Both CID fonts AND large images are present (even 1 page each), OR
- 2+ pages have CID fonts, OR
- 2+ pages have large background images

```python
if (cid_pages > 0 and large_image_pages > 0) or cid_pages >= 2 or large_image_pages >= 2:
    warn_requires_ocr()
```

---

## Warning Message

When detected, users see this prominent warning:

```
======================================================================
⚠️  WARNING: PDF REQUIRES OCR
======================================================================
This PDF appears to be graphically-rendered:
  • Pages with CID-encoded fonts: 1/3
  • Pages with large background images: 1/3

This tool can mark structural elements but CANNOT extract text content
from graphically-rendered PDFs.

RECOMMENDATION:
  1. Use OCR software to convert this PDF to searchable text:
     - Adobe Acrobat Pro: Tools → Enhance Scans → Recognize Text
     - Tesseract OCR: tesseract input.pdf output pdf
     - ABBYY FineReader
     - Online services: ocr.space, Adobe online OCR

  2. Re-run this remediation tool on the OCR'd version

The current remediation will proceed but may produce limited results.
======================================================================
```

---

## OCR Workflow

### Step 1: Detect

Run the remediator to see if OCR is needed:

```bash
python3 pdf_remediator.py input.pdf --analyze-only
```

If you see the OCR warning, proceed to Step 2.

### Step 2: OCR

Choose an OCR method:

#### Option A: Adobe Acrobat Pro (Recommended)
```
1. Open PDF in Adobe Acrobat Pro
2. Tools → Enhance Scans → Recognize Text
3. Select "In This File"
4. Click "Recognize Text"
5. Save as new file
```

#### Option B: Tesseract OCR (Free, Open Source)
```bash
# Install Tesseract
# macOS:
brew install tesseract

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# Run OCR
tesseract input.pdf output pdf

# This creates output.pdf with searchable text
```

#### Option C: ABBYY FineReader (Professional)
```
1. Open PDF in ABBYY FineReader
2. Click "Recognize" or "Convert to Searchable PDF"
3. Review and save
```

#### Option D: Online Services
- **ocr.space**: Free API, 25,000 requests/month
- **Adobe Online OCR**: Free with Adobe account
- **Google Drive**: Upload → Right-click → Open with Google Docs

### Step 3: Remediate

Run the remediator on the OCR'd PDF:

```bash
python3 pdf_remediator.py output_ocr.pdf
```

Now the tool can properly extract and tag text content!

---

## Example: ChatGPT PDF

### Original Problem

**File**: `ChatGPT is Dumber Than You Think.pdf`

**Issue**: Entire pages tagged as single images, content appears empty

**Investigation Results**:
```
Page 1: 1952x1098 pixel image (full page background)
Page 2: Text shows as: \x00\x02\x03\x04\x05\x06\x07\x08 (CID encoding)
Page 3: Vector paths, no searchable text
```

### Detection Output

```bash
python3 pdf_remediator.py "ChatGPT is Dumber Than You Think.pdf" --analyze-only
```

**Result**:
```
⚠️  WARNING: PDF REQUIRES OCR
This PDF appears to be graphically-rendered:
  • Pages with CID-encoded fonts: 1/3
  • Pages with large background images: 1/3
```

### Solution

After OCR with Tesseract:
```bash
tesseract "ChatGPT is Dumber Than You Think.pdf" chatgpt_ocr pdf
python3 pdf_remediator.py chatgpt_ocr.pdf
```

**Result**: Proper text extraction, headings detected, paragraphs tagged correctly ✅

---

## Technical Implementation

### Code Location

**File**: `pdf_remediator.py`
**Method**: `_check_ocr_requirement()` (lines 2130-2216)
**Called from**: `analyze()` method (line 1879)

### Detection Algorithm

```python
def _check_ocr_requirement(self) -> List[AccessibilityIssue]:
    """
    Detect if PDF is graphically-rendered and requires OCR.

    Checks:
    1. CID-encoded fonts (hex sequences in content streams)
    2. Large background images (>1500px)

    Returns:
        List of issues (with OCR warning if detected)
    """
    cid_pages = 0
    large_image_pages = 0
    pages_checked = min(3, len(self.pdf.pages))  # Check first 3 pages

    for page_num, page in enumerate(self.pdf.pages[:pages_checked], 1):
        # Check for CID encoding
        if '/Contents' in page:
            content_bytes = page.Contents.read_bytes()
            hex_sequences = 0

            # Look for sequences of low bytes (< 32)
            for i in range(len(content_bytes) - 10):
                if (content_bytes[i] < 32 and content_bytes[i+1] < 32 and
                    content_bytes[i+2] < 32 and content_bytes[i+3] < 32):
                    hex_sequences += 1
                    if hex_sequences > 10:
                        cid_pages += 1
                        break

        # Check for large images
        if '/Resources' in page and '/XObject' in page.Resources:
            for name, obj in page.Resources.XObject.items():
                if obj.Subtype == '/Image':
                    width = int(obj.get('/Width', 0))
                    height = int(obj.get('/Height', 0))
                    if width > 1500 or height > 1500:
                        large_image_pages += 1
                        break

    # Trigger warning if both indicators present, or 2+ pages with either
    if (cid_pages > 0 and large_image_pages > 0) or cid_pages >= 2 or large_image_pages >= 2:
        return [create_ocr_warning()]

    return []
```

### Image Detection Update

**File**: `pdf_remediator.py`
**Method**: `ImageInfo.determine_if_decorative()` (lines 64-87)

```python
def determine_if_decorative(self) -> bool:
    """
    Determine if image is likely decorative.
    Updated to mark very large images as decorative (full-page backgrounds).
    """
    # Very small images
    if self.width < 20 or self.height < 20:
        return True

    # Very thin images (lines, borders)
    aspect_ratio = self.width / self.height if self.height > 0 else 0
    if aspect_ratio > 20 or aspect_ratio < 0.05:
        return True

    # Very small area
    if self.width * self.height < 400:
        return True

    # NEW: Very large images (full-page backgrounds)
    if self.width > 1500 or self.height > 1500:
        return True

    return False
```

---

## False Positives

### When Detection Might Be Wrong

**Scenario**: PDF with legitimately large images (infographics, diagrams)

**Example**:
- Engineering drawing with 2000x3000 pixel technical diagram
- Medical imaging PDF with high-resolution scans
- Architectural blueprint with large floor plan

**Solution**: If OCR warning appears but text IS searchable:
```bash
# Test if text is searchable
pdftotext input.pdf - | head -20

# If you see actual text (not gibberish), you can ignore the warning
```

### Adjusting Thresholds

If you get frequent false positives, adjust detection thresholds in `pdf_remediator.py`:

```python
# Line 2167: Increase size threshold for large images
if self.width > 2000 or self.height > 2000:  # Was 1500

# Line 2160: Require more hex sequences for CID detection
if hex_sequences > 20:  # Was 10

# Line 2189: Require more pages to trigger warning
if (cid_pages > 1 and large_image_pages > 1) or cid_pages >= 3 or large_image_pages >= 3:
```

---

## Statistics and Reporting

### Analysis Report

OCR detection adds a new critical issue to the report:

```
REMAINING ISSUES (Manual Review Required)
----------------------------------------------------------------------
[CRITICAL] Document Structure
  PDF appears to be graphically-rendered (detected 1 pages with CID fonts,
  1 pages with large background images). Text content cannot be properly
  extracted or tagged without OCR. Consider using OCR software
  (Adobe Acrobat Pro, Tesseract, ABBYY FineReader) to convert this PDF
  to searchable text before remediation.
  WCAG: 1.3.1 Info and Relationships
```

### Issue Categorization

- **Category**: Document Structure
- **Severity**: Critical (blocks proper remediation)
- **WCAG Criterion**: 1.3.1 Info and Relationships
- **Remediated**: False (requires external OCR tool)

---

## Best Practices

### 1. Check Early

Always run `--analyze-only` first:
```bash
python3 pdf_remediator.py input.pdf --analyze-only
```

If OCR warning appears, do OCR before full remediation.

### 2. Verify Text Extraction

Before OCR, confirm text is not extractable:
```bash
# Try to extract text
pdftotext input.pdf - | head -50

# If output is gibberish or empty, OCR is needed
```

### 3. Choose Right OCR Tool

| Tool | Best For | Accuracy | Speed | Cost |
|------|----------|----------|-------|------|
| **Adobe Acrobat Pro** | Highest accuracy | Excellent | Fast | $$$ |
| **ABBYY FineReader** | Complex layouts | Excellent | Medium | $$$ |
| **Tesseract OCR** | Simple text | Good | Fast | Free |
| **Google Drive** | Quick testing | Good | Medium | Free |

### 4. Review OCR Output

After OCR, review for:
- Spelling errors (common in OCR)
- Formatting issues (tables, lists)
- Missing or garbled text
- Incorrect character recognition

### 5. Re-run Remediation

After OCR, run full remediation:
```bash
python3 pdf_remediator.py input_ocr.pdf --no-flatten
```

Note: Use `--no-flatten` after OCR to preserve text structure.

---

## Troubleshooting

### Issue 1: Warning Appears But Text Seems Fine

**Check**:
```bash
pdftotext input.pdf - | wc -l
# If > 10 lines of readable text, may be false positive
```

**Solution**: Ignore warning if text extraction works

---

### Issue 2: OCR Doesn't Improve Results

**Possible causes**:
- PDF has password protection
- PDF has DRM restrictions
- Images are too low resolution
- Text is stylized/artistic fonts

**Solutions**:
- Remove password: `qpdf --decrypt input.pdf output.pdf`
- Increase OCR resolution
- Use professional OCR service

---

### Issue 3: Large File Size After OCR

**Cause**: OCR adds text layer on top of images

**Solution**: Compress after OCR
```bash
# Using Ghostscript
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output_compressed.pdf input_ocr.pdf
```

---

## Version History

### v2.4 - OCR Detection (Current - January 2025)

**NEW Features**:
- Automatic detection of CID-encoded fonts
- Large background image detection (>1500px)
- Combined heuristics for graphically-rendered PDFs
- Prominent warning message with OCR recommendations
- Integration with analysis workflow

**Updated Features**:
- `ImageInfo.determine_if_decorative()` - Marks large images as decorative
- `analyze()` - Calls OCR detection before finalizing report
- Report includes OCR warning as critical issue

**Files Modified**:
1. `pdf_remediator.py` - Added `_check_ocr_requirement()` method
2. `pdf_remediator.py` - Updated `determine_if_decorative()` logic
3. `OCR_DETECTION_GUIDE.md` - This documentation (new file)

---

## Resources

### OCR Software

- **Adobe Acrobat Pro**: https://www.adobe.com/acrobat.html
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract
- **ABBYY FineReader**: https://www.abbyy.com/finereader/
- **ocr.space API**: https://ocr.space/ocrapi

### Python OCR Libraries

```python
# pytesseract (Tesseract wrapper)
pip install pytesseract
from PIL import Image
import pytesseract

# OCRmyPDF (adds text layer to PDFs)
pip install ocrmypdf
ocrmypdf input.pdf output.pdf

# pdf2image + pytesseract
pip install pdf2image pytesseract
from pdf2image import convert_from_path
pages = convert_from_path('input.pdf')
text = pytesseract.image_to_string(pages[0])
```

### Testing Tools

```bash
# Check if PDF has searchable text
pdftotext input.pdf - | head -20

# Extract text from specific pages
pdftotext -f 1 -l 3 input.pdf -

# View PDF structure
pdfinfo input.pdf
pdftk input.pdf dump_data
```

---

## Summary

### Problem
Graphically-rendered PDFs cannot be properly remediated because text content is stored as graphics, not searchable text.

### Solution
v2.4 automatically detects these PDFs and warns users to run OCR before remediation.

### Workflow
1. **Analyze** → Detect OCR requirement
2. **OCR** → Convert to searchable text
3. **Remediate** → Properly tag text content

### Result
Users are guided to the correct workflow, preventing incomplete remediation and ensuring proper accessibility.

---

**Documentation Version**: 2.4
**Last Updated**: January 25, 2025
**Author**: PDF Remediator Development Team
