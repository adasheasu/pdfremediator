# API Reference

Complete Python API documentation for PDF Remediator.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Classes](#classes)
  - [EnhancedPDFRemediator](#enhancedpdfremediator)
  - [ImageInfo](#imageinfo)
  - [TableInfo](#tableinfo)
  - [LinkInfo](#linkinfo)
  - [IssueInfo](#issueinfo)
- [Methods](#methods)
- [Data Structures](#data-structures)
- [Examples](#examples)
- [Error Handling](#error-handling)

---

## Installation

```python
# Import the main class
from pdf_remediator import EnhancedPDFRemediator

# Or import all classes
from pdf_remediator import (
    EnhancedPDFRemediator,
    ImageInfo,
    TableInfo,
    LinkInfo,
    IssueInfo
)
```

---

## Quick Start

```python
from pdf_remediator import EnhancedPDFRemediator

# Initialize remediator
remediator = EnhancedPDFRemediator(
    input_path="input.pdf",
    output_path="output.pdf"
)

# Load PDF
remediator.load_pdf()

# Analyze issues
issues = remediator.analyze()

# Remediate
options = {
    'title': 'Document Title',
    'author': 'Author Name',
    'language': 'en-US',
    'flatten': True
}
remediator.remediate(options)

# Save
remediator.save()
remediator.close()
```

---

## Classes

### EnhancedPDFRemediator

Main class for PDF accessibility remediation.

#### Constructor

```python
EnhancedPDFRemediator(input_path: str, output_path: str = None)
```

**Parameters**:
- `input_path` (str): Path to input PDF file
- `output_path` (str, optional): Path for output PDF. Defaults to `{input}_remediated.pdf`

**Example**:
```python
# With default output
remediator = EnhancedPDFRemediator("input.pdf")

# With custom output
remediator = EnhancedPDFRemediator("input.pdf", "output.pdf")
```

#### Attributes

```python
remediator.pdf              # pikepdf.Pdf object
remediator.input_path       # str: Input file path
remediator.output_path      # str: Output file path
remediator.images           # List[ImageInfo]: Detected images
remediator.tables           # List[TableInfo]: Detected tables
remediator.links            # List[LinkInfo]: Detected links
remediator.issues           # List[IssueInfo]: Found issues
remediator.stats            # Dict: Remediation statistics
```

---

### ImageInfo

Data class for image information.

```python
@dataclass
class ImageInfo:
    name: str           # Image identifier (e.g., '/Im1')
    width: int          # Image width in pixels
    height: int         # Image height in pixels
    page_number: int    # Page number (1-indexed)
    is_decorative: bool # Whether image is decorative
    alt_text: str       # Alternative text description
```

**Methods**:

```python
def determine_if_decorative(self) -> bool:
    """
    Determine if image is decorative based on characteristics.

    Returns:
        bool: True if decorative, False if descriptive

    Rules:
        - Size < 20x20 pixels → decorative
        - Aspect ratio > 20:1 or < 0.05:1 → decorative
        - Area < 400 pixels → decorative
        - Otherwise → descriptive
    """

def generate_alt_text(self) -> str:
    """
    Generate contextual alt text based on image characteristics.

    Returns:
        str: Generated alt text

    Logic:
        - Wide images (ratio > 2): "Diagram or illustration"
        - Tall images (ratio < 0.5): "Vertical graphic"
        - Large images (>400x400): "Figure or photograph"
        - Default: "Graphic element"
    """
```

**Example**:
```python
img = ImageInfo(
    name='/Im1',
    width=800,
    height=600,
    page_number=1,
    is_decorative=False,
    alt_text='Company logo'
)

# Check if decorative
if img.determine_if_decorative():
    print("Image is decorative")

# Generate alt text
alt = img.generate_alt_text()
print(f"Generated: {alt}")
```

---

### TableInfo

Data class for table information.

```python
@dataclass
class TableInfo:
    page_number: int        # Page number (1-indexed)
    rows: int               # Number of rows
    cols: int               # Number of columns
    has_header_row: bool    # Has header row
    has_header_col: bool    # Has header column
    summary: str            # Table summary
```

**Methods**:

```python
def generate_summary(self) -> str:
    """
    Generate table summary for accessibility.

    Returns:
        str: Table summary description

    Format:
        "Table with {rows} rows and {cols} columns with column headers"
    """
```

**Example**:
```python
table = TableInfo(
    page_number=1,
    rows=5,
    cols=3,
    has_header_row=True,
    has_header_col=False,
    summary=''
)

# Generate summary
table.summary = table.generate_summary()
print(table.summary)
# Output: "Table with 5 rows and 3 columns with column headers"
```

---

### LinkInfo

Data class for link information.

```python
@dataclass
class LinkInfo:
    text: str               # Link text
    url: str                # Target URL
    page_number: int        # Page number (1-indexed)
    is_descriptive: bool    # Whether text is descriptive
    improved_text: str      # Improved descriptive text
```

**Methods**:

```python
def is_generic(self) -> bool:
    """
    Check if link text is generic/non-descriptive.

    Returns:
        bool: True if generic, False if descriptive

    Generic phrases:
        - "click here"
        - "read more"
        - "here"
        - "link"
        - "download"
        - "more info"
    """

def generate_descriptive_text(self) -> str:
    """
    Generate descriptive link text from URL.

    Returns:
        str: Descriptive link text

    Logic:
        - Extract domain from URL
        - Remove www. prefix
        - Convert hyphens to spaces
        - Capitalize words
        - Format: "Link to {domain}"
    """
```

**Example**:
```python
link = LinkInfo(
    text='click here',
    url='https://example.com/training',
    page_number=1,
    is_descriptive=False,
    improved_text=''
)

# Check if generic
if link.is_generic():
    # Generate improved text
    link.improved_text = link.generate_descriptive_text()
    print(f"Improved: {link.improved_text}")
    # Output: "Improved: Link to example training"
```

---

### IssueInfo

Data class for accessibility issues.

```python
@dataclass
class IssueInfo:
    severity: str       # 'CRITICAL', 'MAJOR', 'MINOR'
    category: str       # Issue category
    description: str    # Issue description
    wcag_criterion: str # WCAG reference (e.g., '1.1.1')
    page_number: int    # Page number (0 for document-level)
    fixed: bool         # Whether issue was fixed
```

**Example**:
```python
issue = IssueInfo(
    severity='CRITICAL',
    category='Document Structure',
    description='Document lacks structure tree',
    wcag_criterion='1.3.1 Info and Relationships',
    page_number=0,
    fixed=True
)
```

---

## Methods

### File Operations

#### load_pdf()

```python
def load_pdf(self) -> None:
    """
    Load PDF file for processing.

    Raises:
        FileNotFoundError: If input file doesn't exist
        Exception: If PDF cannot be opened
    """
```

**Example**:
```python
remediator = EnhancedPDFRemediator("input.pdf")
try:
    remediator.load_pdf()
    print("PDF loaded successfully")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error loading PDF: {e}")
```

---

#### save()

```python
def save(self) -> None:
    """
    Save remediated PDF to output path.

    Raises:
        Exception: If save fails
    """
```

**Example**:
```python
remediator.remediate(options)
remediator.save()
print(f"Saved to: {remediator.output_path}")
```

---

#### close()

```python
def close(self) -> None:
    """
    Close PDF file and release resources.
    """
```

**Example**:
```python
remediator.close()
```

---

### Analysis Methods

#### analyze()

```python
def analyze(self) -> List[IssueInfo]:
    """
    Analyze PDF for accessibility issues.

    Returns:
        List[IssueInfo]: List of detected issues

    Checks:
        - Document structure
        - Images and alt text
        - Tables
        - Links
        - Metadata
        - Reading order
        - Language
    """
```

**Example**:
```python
issues = remediator.analyze()

# Print all issues
for issue in issues:
    print(f"[{issue.severity}] {issue.category}")
    print(f"  {issue.description}")
    print(f"  WCAG: {issue.wcag_criterion}")
    print()

# Filter by severity
critical = [i for i in issues if i.severity == 'CRITICAL']
print(f"Found {len(critical)} critical issues")
```

---

#### analyze_images()

```python
def analyze_images(self) -> List[ImageInfo]:
    """
    Analyze all images in PDF.

    Returns:
        List[ImageInfo]: List of detected images with metadata

    For each image:
        - Detects size and dimensions
        - Determines if decorative
        - Generates alt text if needed
        - Identifies page location
    """
```

**Example**:
```python
images = remediator.analyze_images()

print(f"Found {len(images)} images")
decorative = [img for img in images if img.is_decorative]
descriptive = [img for img in images if not img.is_decorative]

print(f"  Decorative: {len(decorative)}")
print(f"  Descriptive: {len(descriptive)}")

# List all descriptive images
for img in descriptive:
    print(f"\n{img.name} (Page {img.page_number})")
    print(f"  Size: {img.width}x{img.height}")
    print(f"  Alt text: {img.alt_text}")
```

---

#### analyze_tables()

```python
def analyze_tables(self) -> List[TableInfo]:
    """
    Analyze tables in PDF.

    Returns:
        List[TableInfo]: List of detected tables

    Note:
        Table detection requires content stream parsing.
        Currently detects basic table structures.
    """
```

**Example**:
```python
tables = remediator.analyze_tables()

print(f"Found {len(tables)} tables")

for i, table in enumerate(tables, 1):
    print(f"\nTable {i} (Page {table.page_number})")
    print(f"  Size: {table.rows} rows × {table.cols} columns")
    print(f"  Headers: Row={table.has_header_row}, Col={table.has_header_col}")
    print(f"  Summary: {table.summary}")
```

---

#### analyze_links()

```python
def analyze_links(self) -> List[LinkInfo]:
    """
    Analyze links in PDF.

    Returns:
        List[LinkInfo]: List of detected links

    Identifies:
        - Link text and URL
        - Generic vs. descriptive text
        - Suggested improvements
    """
```

**Example**:
```python
links = remediator.analyze_links()

print(f"Found {len(links)} links")

# Find non-descriptive links
non_descriptive = [link for link in links if not link.is_descriptive]

print(f"Non-descriptive links: {len(non_descriptive)}")

for link in non_descriptive:
    print(f"\nPage {link.page_number}:")
    print(f"  Current: '{link.text}'")
    print(f"  URL: {link.url}")
    print(f"  Suggested: '{link.improved_text}'")
```

---

### Remediation Methods

#### remediate()

```python
def remediate(self, options: Dict[str, Any]) -> None:
    """
    Remediate PDF for accessibility.

    Parameters:
        options (dict): Remediation options
            - title (str): Document title
            - author (str): Document author
            - subject (str): Document subject
            - keywords (str): Document keywords
            - language (str): Document language (default: 'en-US')
            - flatten (bool): Flatten PDF layers (default: True)

    Applies:
        - Document metadata
        - Structure tagging
        - Image alt text
        - Reading order
        - Link improvements
        - Layer flattening (if enabled)
    """
```

**Example**:
```python
options = {
    'title': 'Annual Report 2024',
    'author': 'Finance Department',
    'subject': 'Financial Analysis',
    'keywords': 'finance, report, quarterly',
    'language': 'en-US',
    'flatten': True
}

remediator.remediate(options)
```

---

#### tag_images()

```python
def tag_images(self) -> int:
    """
    Tag all images with appropriate alt text or mark as decorative.

    Returns:
        int: Number of images tagged

    For each image:
        - Decorative images: Tagged as Artifact with empty alt text
        - Descriptive images: Tagged as Figure with generated alt text
    """
```

**Example**:
```python
count = remediator.tag_images()
print(f"Tagged {count} images")

# View results
for img in remediator.images:
    status = "Decorative" if img.is_decorative else "Descriptive"
    print(f"{img.name}: {status}")
    if not img.is_decorative:
        print(f"  Alt text: {img.alt_text}")
```

---

#### tag_tables()

```python
def tag_tables(self) -> int:
    """
    Tag tables with proper structure.

    Returns:
        int: Number of tables tagged

    Adds:
        - Table element
        - TR (table row) elements
        - TH (header cell) elements
        - TD (data cell) elements
        - Table summary
    """
```

**Example**:
```python
count = remediator.tag_tables()
print(f"Tagged {count} tables")
```

---

#### improve_links()

```python
def improve_links(self) -> int:
    """
    Improve link descriptions.

    Returns:
        int: Number of links improved

    Replaces generic text with descriptive alternatives.
    """
```

**Example**:
```python
count = remediator.improve_links()
print(f"Improved {count} links")
```

---

#### set_reading_order()

```python
def set_reading_order(self) -> None:
    """
    Set logical reading order for screen readers.

    Configures:
        - StructParents index for each page
        - Tab order to follow structure (/S)
        - Content order markers
    """
```

**Example**:
```python
remediator.set_reading_order()
print("Reading order configured")
```

---

#### flatten_layers()

```python
def flatten_layers(self) -> bool:
    """
    Flatten PDF layers (optional content groups).

    Returns:
        bool: True if layers were flattened, False if none found

    Removes:
        - Optional content groups (OCG)
        - OCProperties dictionary
        - Layer visibility controls

    Note:
        Flattening is required for proper tagging of layered PDFs.
    """
```

**Example**:
```python
if remediator.flatten_layers():
    print("Layers flattened")
else:
    print("No layers found")
```

---

#### add_alt_text()

```python
def add_alt_text(self, image_name: str, alt_text: str) -> None:
    """
    Add custom alt text to specific image.

    Parameters:
        image_name (str): Image identifier (e.g., '/Im1')
        alt_text (str): Alternative text description
    """
```

**Example**:
```python
# Add custom alt text
remediator.add_alt_text('/Im1', 'Company logo with mountain peak')
remediator.add_alt_text('/Im2', 'Process flow diagram showing 5 steps')
remediator.add_alt_text('/Im3', 'Bar chart: quarterly revenue 2020-2024')
```

---

#### mark_image_decorative()

```python
def mark_image_decorative(self, image_name: str) -> None:
    """
    Mark specific image as decorative.

    Parameters:
        image_name (str): Image identifier (e.g., '/Im1')

    Result:
        Image is tagged as Artifact with empty alt text.
    """
```

**Example**:
```python
# Mark decorative images
remediator.mark_image_decorative('/Im1')  # Border
remediator.mark_image_decorative('/Im2')  # Separator line
```

---

### Reporting Methods

#### generate_report()

```python
def generate_report(self, format: str = 'text') -> Union[str, Dict]:
    """
    Generate remediation report.

    Parameters:
        format (str): Report format ('text' or 'json')

    Returns:
        str: Text report (if format='text')
        dict: JSON report (if format='json')

    Includes:
        - File information
        - Remediation statistics
        - Issues found and fixed
        - Remaining issues
        - Recommendations
    """
```

**Text Report Example**:
```python
report = remediator.generate_report(format='text')
print(report)

# Save to file
with open('report.txt', 'w') as f:
    f.write(report)
```

**JSON Report Example**:
```python
import json

report = remediator.generate_report(format='json')

# Pretty print
print(json.dumps(report, indent=2))

# Save to file
with open('report.json', 'w') as f:
    json.dump(report, f, indent=2)

# Access fields
print(f"Images tagged: {report['statistics']['images_tagged']}")
print(f"Issues fixed: {report['summary']['issues_fixed']}")
```

---

#### get_statistics()

```python
def get_statistics(self) -> Dict[str, int]:
    """
    Get remediation statistics.

    Returns:
        dict: Statistics dictionary
            - images_tagged (int)
            - images_decorative (int)
            - images_descriptive (int)
            - tables_tagged (int)
            - headings_tagged (int)
            - links_fixed (int)
            - issues_found (int)
            - issues_fixed (int)
    """
```

**Example**:
```python
stats = remediator.get_statistics()

print("Remediation Statistics:")
print(f"  Images: {stats['images_tagged']}")
print(f"    Decorative: {stats['images_decorative']}")
print(f"    Descriptive: {stats['images_descriptive']}")
print(f"  Tables: {stats['tables_tagged']}")
print(f"  Links: {stats['links_fixed']}")
print(f"  Issues fixed: {stats['issues_fixed']}/{stats['issues_found']}")
```

---

## Data Structures

### Remediation Options

```python
options = {
    'title': str,        # Document title (required)
    'author': str,       # Document author (optional)
    'subject': str,      # Document subject (optional)
    'keywords': str,     # Comma-separated keywords (optional)
    'language': str,     # ISO 639 language code (default: 'en-US')
    'flatten': bool      # Flatten PDF layers (default: True)
}
```

### Statistics Dictionary

```python
stats = {
    'images_tagged': int,       # Total images tagged
    'images_decorative': int,   # Decorative images
    'images_descriptive': int,  # Descriptive images
    'tables_tagged': int,       # Tables tagged
    'headings_tagged': int,     # Headings tagged
    'links_fixed': int,         # Links improved
    'issues_found': int,        # Total issues found
    'issues_fixed': int         # Issues remediated
}
```

### JSON Report Structure

```python
report = {
    'file_info': {
        'input_path': str,
        'output_path': str,
        'pages': int,
        'date': str
    },
    'statistics': {
        'images_tagged': int,
        'images_decorative': int,
        'images_descriptive': int,
        'tables_tagged': int,
        'headings_tagged': int,
        'links_fixed': int
    },
    'issues': [
        {
            'severity': str,
            'category': str,
            'description': str,
            'wcag_criterion': str,
            'page_number': int,
            'fixed': bool
        }
    ],
    'summary': {
        'issues_found': int,
        'issues_fixed': int,
        'issues_remaining': int,
        'wcag_compliance': float  # Percentage
    }
}
```

---

## Examples

### Example 1: Basic Workflow

```python
from pdf_remediator import EnhancedPDFRemediator

# Initialize
remediator = EnhancedPDFRemediator("input.pdf", "output.pdf")

# Load
remediator.load_pdf()

# Analyze
issues = remediator.analyze()
print(f"Found {len(issues)} issues")

# Remediate
options = {
    'title': 'My Document',
    'language': 'en-US',
    'flatten': True
}
remediator.remediate(options)

# Save and close
remediator.save()
remediator.close()

print("Remediation complete!")
```

---

### Example 2: Custom Alt Text

```python
from pdf_remediator import EnhancedPDFRemediator

remediator = EnhancedPDFRemediator("input.pdf", "output.pdf")
remediator.load_pdf()

# Analyze images
images = remediator.analyze_images()

# Review and customize
for img in images:
    if not img.is_decorative:
        print(f"{img.name}: {img.alt_text}")
        # Add custom alt text
        if img.name == '/Im1':
            remediator.add_alt_text('/Im1', 'Company logo with tagline')
        elif img.name == '/Im2':
            remediator.add_alt_text('/Im2', 'Process diagram: 5 steps')

# Tag with custom alt text
remediator.tag_images()

# Complete remediation
options = {'title': 'Document', 'language': 'en-US'}
remediator.remediate(options)
remediator.save()
remediator.close()
```

---

### Example 3: Batch Processing

```python
from pdf_remediator import EnhancedPDFRemediator
import os
import glob

def remediate_batch(directory, options):
    """Remediate all PDFs in directory."""
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))

    results = []
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")

        # Create output path
        base = os.path.basename(pdf_file)
        output = os.path.join(directory, f"remediated_{base}")

        try:
            # Remediate
            remediator = EnhancedPDFRemediator(pdf_file, output)
            remediator.load_pdf()
            remediator.remediate(options)
            remediator.save()

            # Get stats
            stats = remediator.get_statistics()
            results.append({
                'file': base,
                'status': 'success',
                'stats': stats
            })

            remediator.close()

        except Exception as e:
            results.append({
                'file': base,
                'status': 'error',
                'error': str(e)
            })

    return results

# Run batch
options = {
    'title': 'Document',
    'author': 'Department',
    'language': 'en-US'
}

results = remediate_batch('/path/to/pdfs', options)

# Print summary
for result in results:
    print(f"\n{result['file']}: {result['status']}")
    if result['status'] == 'success':
        print(f"  Images: {result['stats']['images_tagged']}")
        print(f"  Issues fixed: {result['stats']['issues_fixed']}")
```

---

### Example 4: Detailed Analysis

```python
from pdf_remediator import EnhancedPDFRemediator

remediator = EnhancedPDFRemediator("document.pdf")
remediator.load_pdf()

# Analyze all components
issues = remediator.analyze()
images = remediator.analyze_images()
tables = remediator.analyze_tables()
links = remediator.analyze_links()

# Report findings
print("=== ANALYSIS REPORT ===\n")

print(f"Issues: {len(issues)}")
for issue in issues:
    print(f"  [{issue.severity}] {issue.description}")

print(f"\nImages: {len(images)}")
decorative = sum(1 for img in images if img.is_decorative)
print(f"  Decorative: {decorative}")
print(f"  Descriptive: {len(images) - decorative}")

print(f"\nTables: {len(tables)}")
for table in tables:
    print(f"  Page {table.page_number}: {table.summary}")

print(f"\nLinks: {len(links)}")
non_descriptive = sum(1 for link in links if not link.is_descriptive)
print(f"  Non-descriptive: {non_descriptive}")

remediator.close()
```

---

## Error Handling

### Common Exceptions

```python
from pdf_remediator import EnhancedPDFRemediator

try:
    remediator = EnhancedPDFRemediator("input.pdf", "output.pdf")
    remediator.load_pdf()

    options = {'title': 'Document', 'language': 'en-US'}
    remediator.remediate(options)

    remediator.save()
    remediator.close()

except FileNotFoundError:
    print("Error: PDF file not found")

except PermissionError:
    print("Error: Permission denied")

except Exception as e:
    print(f"Error during remediation: {e}")
```

### Graceful Cleanup

```python
from pdf_remediator import EnhancedPDFRemediator

remediator = None
try:
    remediator = EnhancedPDFRemediator("input.pdf", "output.pdf")
    remediator.load_pdf()

    # ... processing ...

    remediator.save()

except Exception as e:
    print(f"Error: {e}")

finally:
    if remediator:
        remediator.close()
```

---

## See Also

- [Installation Guide](INSTALLATION.md)
- [Usage Guide](USAGE.md)
- [Enhanced Features](ENHANCED_FEATURES.md)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)

---

**API Version**: 2.0
**Last Updated**: October 2025
**Python Version**: 3.7+
