# PDF Remediation Tool

A comprehensive web-based tool that converts PDF documents to HTML with **style preservation**, remediates them for WCAG 2.2 AA accessibility compliance, and generates **properly tagged, accessible PDFs**.

## ✨ Key Features

### Style Preservation
- **Smart Heading Detection**: Analyzes font size, weight, and formatting to identify document structure
- **Font Size Analysis**: Preserves relative sizing and hierarchy from original PDF
- **Layout Preservation**: Maintains paragraph structure and text flow
- **Table Structure**: Extracts and preserves complex table layouts

### Accessibility (WCAG 2.2 AA Compliance)
The tool automatically applies comprehensive accessibility standards including:
  - **Proper semantic HTML5 structure** with `<main>`, `<header>`, etc.
  - **Intelligent heading hierarchy** (H1-H6) with automatic level fixing
  - **Accessible tables** with captions, scope attributes, and ARIA roles
  - **ARIA landmarks** for screen reader navigation
  - **Skip navigation links** for keyboard users
  - **Sufficient color contrast** (meets WCAG 2.2 AA ratios)
  - **Keyboard accessibility** throughout
  - **External link handling** with security attributes
  - **Focus management** with visible indicators
- **Tagged PDF Generation**: Creates properly structured, accessible PDFs using ReportLab
- **Beautiful Web Interface**: Drag-and-drop file upload with real-time progress tracking
- **Dual Format Download**: Get both accessible HTML and tagged PDF versions

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Navigate to the project directory:
```bash
cd pdf_remediation_tool
```

2. Install required dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

1. Start the web server:
```bash
python3 app.py
```

2. Open your web browser and go to:
```
http://localhost:5000
```

3. Upload a PDF document using the web interface

4. Wait for processing to complete

5. Download the remediated HTML and/or PDF files

## How It Works

### 1. PDF to HTML Conversion with Style Preservation
- **Character-Level Analysis**: Extracts individual characters with font, size, and position data
- **Smart Heading Detection**: Uses multiple criteria:
  - Font size relative to document average
  - Bold/italic formatting
  - Text length and capitalization patterns
  - Punctuation analysis
- **Automatic Heading Levels**: Assigns H1-H6 based on font size ratios
- **Table Extraction**: Preserves table structure with headers and data cells
- **Paragraph Formation**: Groups text intelligently while maintaining flow

### 2. WCAG 2.2 AA Accessibility Remediation
The tool applies comprehensive accessibility standards:

- **Document Structure**:
  - Proper HTML5 semantic structure with `<main role="main">`
  - Language declaration (`lang="en"`)
  - Unique IDs for navigation targets

- **Heading Hierarchy**:
  - Ensures document starts with H1
  - Fixes skipped levels (e.g., H1 → H3 becomes H1 → H2)
  - Maintains logical structure throughout

- **Table Accessibility**:
  - Descriptive captions for every table
  - `scope` attributes on all header cells (`<th>`)
  - `role="table"` for ARIA support
  - Proper `<thead>` and `<tbody>` structure
  - Visual styling for better readability

- **Link Accessibility**:
  - Meaningful link text required
  - External links include descriptive titles
  - Security attributes (`rel="noopener noreferrer"`)
  - Visible focus indicators (3px outline)

- **Keyboard Navigation**:
  - Skip-to-content link (visible on focus)
  - Tab order follows logical reading order
  - Focus indicators on all interactive elements

- **Visual Accessibility**:
  - High contrast text colors (>12:1 ratio)
  - Professional styling with clear typography
  - Hover states for better usability
  - Responsive design for all screen sizes

- **Form Accessibility**:
  - Labels associated with all form controls
  - ARIA labels for unlabeled fields
  - Proper input types and attributes

- **Images**:
  - Alt text on all images
  - Decorative images marked appropriately

### 3. Tagged PDF Generation
- **ReportLab Integration**: Creates structured, accessible PDFs
- **Semantic Tags**: Headings (H1-H6), paragraphs, and tables properly tagged
- **Visual Hierarchy**: Maintains heading styles and proper spacing
- **Table Formatting**: Professional table design with headers and alternating rows
- **Document Metadata**: Includes title and author information
- **Fallback Support**: Uses xhtml2pdf if ReportLab encounters issues

## File Structure

```
pdf_remediation_tool/
├── app.py                  # Flask web application
├── pdf_processor.py        # PDF processing and remediation logic
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/
│   └── index.html         # Web interface
├── uploads/               # Temporary upload directory (auto-created)
└── outputs/               # Processed files directory (auto-created)
```

## Accessibility Standards Implemented

This tool implements WCAG 2.2 Level AA standards including:

- **Perceivable**:
  - Text alternatives (alt text)
  - Adaptable content structure
  - Distinguishable content (color contrast)

- **Operable**:
  - Keyboard accessible
  - Navigable structure
  - Clear focus indicators

- **Understandable**:
  - Readable text
  - Predictable behavior
  - Clear language declaration

- **Robust**:
  - Valid HTML
  - Compatible with assistive technologies

## Heading Detection Algorithm

The tool uses an intelligent scoring system to identify headings:

**Criteria (1 point each):**
- ✓ Font size 10%+ larger than document average
- ✓ Bold text formatting
- ✓ Short text (< 100 characters) AND title case
- ✓ ALL CAPS with multiple words
- ✓ No sentence-ending punctuation (period, comma, semicolon)

**Threshold:** Score ≥ 2 points = Identified as heading

**Level Assignment:**
- Font ≥ 2.0x average → H1
- Font ≥ 1.5x average → H2
- Font ≥ 1.3x average → H3
- Font ≥ 1.2x average → H4
- Font ≥ 1.1x average → H5
- Font < 1.1x average → H6

## Limitations & Notes

- **Image Alt Text**: Currently uses placeholder text. Consider integrating OCR or AI services for production use
- **Complex Layouts**: Multi-column or highly stylized PDFs may require manual review
- **Font Families**: Standard fonts used in output (Arial, Helvetica)
- **Colors**: Currently extracts structure but not original text colors
- **Processing Time**: Large PDFs (100+ pages) may take several minutes
- **Image Extraction**: Images are not currently extracted from PDFs (planned enhancement)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

This tool is provided as-is for educational and accessibility purposes.

## Enhancement Documentation

See **ENHANCEMENTS.md** for detailed information about:
- Style preservation techniques
- Tagged PDF generation
- Heading detection algorithm
- Accessibility improvements
- Future enhancement opportunities

## Testing Accessibility

### Screen Reader Testing
Test with popular screen readers:
- **macOS**: VoiceOver (Cmd + F5)
- **Windows**: NVDA (free) or JAWS
- **ChromeVox** (Chrome extension)

### Keyboard Navigation Testing
- **Tab**: Move between interactive elements
- **Shift + Tab**: Move backwards
- **Enter/Space**: Activate links/buttons
- **H key** (screen readers): Navigate by headings

### Browser Developer Tools
Use accessibility inspectors:
- Chrome DevTools → Lighthouse (Accessibility audit)
- Firefox Developer Tools → Accessibility Inspector
- Edge DevTools → Accessibility tab

## Support

For issues or questions:
- Check **README.md** (this file) for usage instructions
- See **ENHANCEMENTS.md** for technical details
- Review **QUICKSTART.md** for quick setup

## Contributing

This tool is open for improvements. Suggested enhancements:
- OCR integration for image alt text
- Font family preservation
- Color extraction
- Multi-language support
- Batch processing
- Advanced layout algorithms
