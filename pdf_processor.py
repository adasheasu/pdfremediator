"""
PDF Processing and Remediation Module
Handles PDF to HTML conversion with style preservation, accessibility remediation,
and tagged PDF generation with WCAG 2.2 AA compliance
"""

import os
import pdfplumber
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import re
from collections import Counter
from playwright.sync_api import sync_playwright
import tempfile


class PDFProcessor:
    def __init__(self):
        self.default_font_size = 12
        self.heading_threshold = 14  # Font sizes >= this are considered headings
        self.ocr_warning = None  # Store OCR detection results

    def detect_ocr_needed(self, pdf_path):
        """
        Detect if PDF is graphically-rendered and needs OCR.

        Checks for:
        - Large images with minimal text (indicates scanned PDF)
        - Very little text content overall
        - Pages with no extractable text

        Returns:
            Tuple of (needs_ocr: bool, reason: str)
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_without_text = 0
                total_text_length = 0
                has_large_images = False

                for page_num, page in enumerate(pdf.pages, 1):
                    # Check for text content
                    text = page.extract_text()
                    if not text or len(text.strip()) < 10:
                        pages_without_text += 1
                    else:
                        total_text_length += len(text.strip())

                    # Check for large images
                    if hasattr(page, 'images'):
                        for img in page.images:
                            width = img.get('width', 0)
                            height = img.get('height', 0)
                            if width > 1500 or height > 1500:
                                has_large_images = True
                                print(f"  Page {page_num}: Found large image ({width}x{height})")

                # Determine if OCR is needed
                reasons = []

                # More than 50% of pages have no text
                if pages_without_text > total_pages * 0.5:
                    reasons.append(f"{pages_without_text}/{total_pages} pages have no extractable text")

                # Very little total text (less than 100 chars per page average)
                avg_text_per_page = total_text_length / total_pages if total_pages > 0 else 0
                if avg_text_per_page < 100:
                    reasons.append("Minimal text content detected")

                # Has large background images
                if has_large_images:
                    reasons.append("Large background images found")

                if reasons:
                    reason = "This PDF may require OCR processing: " + ", ".join(reasons)
                    return True, reason

                return False, ""

        except Exception as e:
            print(f"Warning: Error during OCR detection: {e}")
            return False, ""

    def process_pdf(self, input_pdf_path, output_folder):
        """Main processing pipeline"""
        # Step 0: Check if PDF needs OCR
        needs_ocr, ocr_reason = self.detect_ocr_needed(input_pdf_path)
        if needs_ocr:
            self.ocr_warning = ocr_reason
            print(f"\n⚠️  WARNING: {ocr_reason}")
            print("    Consider using OCR tools before remediation for best results.\n")

        # Extract original filename (without extension)
        original_filename = os.path.splitext(os.path.basename(input_pdf_path))[0]

        # Step 1: Convert PDF to HTML with style preservation
        html_content, extracted_styles = self.pdf_to_html_with_styles(input_pdf_path)

        # Step 2: Remediate HTML for WCAG 2.2 AA compliance
        remediated_html = self.remediate_html(html_content)

        # Step 3: Save HTML file with original filename
        html_filename = f'{original_filename}_remediated.html'
        html_output_path = os.path.join(output_folder, html_filename)
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write(remediated_html)

        # Step 4: Convert HTML to tagged PDF with accessibility structure using browser rendering
        pdf_filename = f'{original_filename}_remediated.pdf'
        pdf_output_path = os.path.join(output_folder, pdf_filename)
        self.html_to_pdf_with_browser(remediated_html, pdf_output_path)

        return {
            'html_file': html_filename,
            'pdf_file': pdf_filename
        }

    def pdf_to_html_with_styles(self, pdf_path):
        """Convert PDF to HTML with exact visual replica of design"""
        pages_html = []
        extracted_styles = {
            'fonts': set(),
            'colors': set(),
            'sizes': []
        }

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Get page dimensions
                page_width = page.width
                page_height = page.height

                # Extract text with detailed character information
                chars = page.chars

                if chars:
                    # Analyze font sizes for statistics
                    font_sizes = [char.get('size', self.default_font_size) for char in chars]
                    extracted_styles['sizes'].extend(font_sizes)

                    # Create page with exact positioning
                    page_html = self.create_page_with_exact_layout(chars, page_width, page_height, page_num)
                    pages_html.append(page_html)

                # Extract tables with positioning and improved text extraction
                # Configure table settings with better word spacing detection
                table_settings = {
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "text_x_tolerance": 3,  # Increased tolerance for better word detection
                    "text_y_tolerance": 3,
                    "intersection_tolerance": 3
                }
                tables = page.extract_tables(table_settings=table_settings)
                if tables:
                    for table_idx, table in enumerate(tables):
                        if table:
                            # Try to get table position
                            try:
                                table_bbox = page.find_tables()[table_idx].bbox
                                table_html = self.table_to_html_with_position(table, table_bbox)
                                pages_html.append(table_html)
                            except:
                                pages_html.append(self.table_to_html_with_style(table))

        # Determine font size statistics
        if extracted_styles['sizes']:
            avg_size = sum(extracted_styles['sizes']) / len(extracted_styles['sizes'])
            self.default_font_size = avg_size

        # Create HTML structure with exact layout preservation
        html_content = self.create_exact_replica_html('\n'.join(pages_html), extracted_styles)
        return html_content, extracted_styles

    def create_page_with_exact_layout(self, chars, page_width, page_height, page_num):
        """Create a page with exact positioning matching PDF layout"""
        if not chars:
            return f'<div class="pdf-page" data-page="{page_num}" style="width: {page_width}pt; height: {page_height}pt;"></div>'

        # Group characters by line (y-coordinate)
        lines = {}
        for char in chars:
            y = round(char['top'], 1)
            if y not in lines:
                lines[y] = []
            lines[y].append(char)

        # Sort lines by vertical position
        sorted_lines = sorted(lines.items(), key=lambda x: x[0])

        # Build HTML for each line with exact positioning
        page_html = f'<div class="pdf-page" data-page="{page_num}" style="width: {page_width}pt; height: {page_height}pt; position: relative;">\n'

        for y, line_chars in sorted_lines:
            # Sort characters by horizontal position
            line_chars.sort(key=lambda c: c['x0'])

            if not line_chars:
                continue

            # Get line position
            x_start = line_chars[0]['x0']

            # Group consecutive characters with similar styles on this line
            styled_html = self.group_chars_by_style(line_chars)

            if styled_html.strip():
                # Create absolutely positioned line
                page_html += f'    <div style="position: absolute; left: {x_start}pt; top: {y}pt; white-space: nowrap;">{styled_html}</div>\n'

        page_html += '</div>\n'
        return page_html

    def table_to_html_with_position(self, table, bbox):
        """Convert table to HTML with exact positioning"""
        x0, top, x1, bottom = bbox
        width = x1 - x0
        height = bottom - top

        table_html = self.table_to_html_with_style(table)

        # Wrap in positioned div
        return f'<div style="position: absolute; left: {x0}pt; top: {top}pt; width: {width}pt;">\n{table_html}\n</div>\n'

    def extract_text_blocks_with_style(self, chars):
        """Group characters into styled text blocks"""
        if not chars:
            return []

        blocks = []
        lines = {}

        # Group characters by vertical position (y-coordinate)
        for char in chars:
            y = round(char['top'])
            if y not in lines:
                lines[y] = []
            lines[y].append(char)

        # Sort lines by vertical position
        sorted_lines = sorted(lines.items(), key=lambda x: x[0])

        current_paragraph = []
        current_paragraph_chars = []

        for y, line_chars in sorted_lines:
            # Sort characters in line by horizontal position
            line_chars.sort(key=lambda c: c['x0'])

            # Extract text and style info
            line_text = ''.join(c.get('text', '') for c in line_chars)

            if not line_text.strip():
                # Empty line - end current paragraph
                if current_paragraph_chars:
                    blocks.append(self.create_styled_paragraph(current_paragraph_chars))
                    current_paragraph = []
                    current_paragraph_chars = []
                continue

            # Analyze line style
            avg_size = sum(c.get('size', self.default_font_size) for c in line_chars) / len(line_chars)
            is_bold = any(c.get('fontname', '').lower().find('bold') != -1 for c in line_chars)

            # Determine if this is a heading based on size and characteristics
            if self.is_heading_line(line_text, avg_size, is_bold):
                # Flush current paragraph
                if current_paragraph_chars:
                    blocks.append(self.create_styled_paragraph(current_paragraph_chars))
                    current_paragraph = []
                    current_paragraph_chars = []

                # Add as heading with preserved styles
                heading_level = self.determine_heading_level(avg_size)
                styled_heading = self.create_styled_heading(line_chars, heading_level)
                blocks.append(styled_heading)
            else:
                # Add to current paragraph
                current_paragraph_chars.extend(line_chars)
                # Add space between lines
                if current_paragraph_chars:
                    current_paragraph_chars.append({'text': ' ', 'size': self.default_font_size, 'fontname': ''})

        # Flush remaining paragraph
        if current_paragraph_chars:
            blocks.append(self.create_styled_paragraph(current_paragraph_chars))

        return blocks

    def is_heading_line(self, text, font_size, is_bold):
        """Determine if a line should be treated as a heading"""
        # Criteria for headings:
        # 1. Larger font size
        # 2. Bold text
        # 3. Shorter text (< 100 chars)
        # 4. Title case or all caps
        # 5. No ending punctuation (except question mark)

        text = text.strip()

        if len(text) == 0:
            return False

        # Check font size
        is_larger = font_size > self.default_font_size * 1.1

        # Check length
        is_short = len(text) < 100

        # Check capitalization
        is_title_case = self.is_title_case(text)
        is_all_caps = text.isupper() and len(text.split()) > 1

        # Check ending
        has_heading_ending = not text.endswith(('.', ',', ';', ':')) or text.endswith('?')

        # Heading if meets multiple criteria
        score = sum([is_larger, is_bold, is_short and is_title_case, is_all_caps, has_heading_ending])

        return score >= 2

    def determine_heading_level(self, font_size):
        """Determine heading level (1-6) based on font size"""
        size_ratio = font_size / self.default_font_size

        if size_ratio >= 2.0:
            return 1
        elif size_ratio >= 1.5:
            return 2
        elif size_ratio >= 1.3:
            return 3
        elif size_ratio >= 1.2:
            return 4
        elif size_ratio >= 1.1:
            return 5
        else:
            return 6

    def create_styled_paragraph(self, chars):
        """Create a paragraph with inline styles preserved"""
        if not chars:
            return '<p></p>'

        styled_spans = self.group_chars_by_style(chars)
        return f'<p>{styled_spans}</p>'

    def create_styled_heading(self, chars, level):
        """Create a heading with inline styles preserved"""
        if not chars:
            return f'<h{level}></h{level}>'

        styled_spans = self.group_chars_by_style(chars)
        return f'<h{level}>{styled_spans}</h{level}>'

    def group_chars_by_style(self, chars):
        """Group consecutive characters with similar styles and create styled spans"""
        if not chars:
            return ''

        result = []
        current_group = []
        current_style = None
        prev_char = None

        for char in chars:
            char_text = char.get('text', '')
            if not char_text:
                continue

            # Extract style information
            font_name = char.get('fontname', '')
            font_size = char.get('size', self.default_font_size)

            # Determine if bold or italic
            is_bold = 'bold' in font_name.lower()
            is_italic = 'italic' in font_name.lower() or 'oblique' in font_name.lower()

            # Get color (if available)
            color = None
            if 'stroking_color' in char and char['stroking_color']:
                color = char['stroking_color']
            elif 'non_stroking_color' in char and char['non_stroking_color']:
                color = char['non_stroking_color']

            # Create style dict
            style = {
                'bold': is_bold,
                'italic': is_italic,
                'size': round(font_size, 1),
                'font': self.extract_font_family(font_name),
                'color': color
            }

            # Check if we need to insert a space (detect gap between characters)
            should_add_space = False
            if prev_char and current_group:
                # Calculate gap between previous and current character
                prev_x1 = prev_char.get('x1', 0)
                curr_x0 = char.get('x0', 0)
                gap = curr_x0 - prev_x1

                # If gap is larger than 20% of character width, insert space
                char_width = char.get('width', font_size * 0.5)
                if gap > char_width * 0.2:
                    should_add_space = True

            # Check if style changed
            if current_style is None or current_style != style:
                # Save previous group
                if current_group and current_style:
                    result.append(self.create_styled_span(current_group, current_style))

                # Start new group
                current_group = [char_text]
                current_style = style
            else:
                # Add space if needed, then add character
                if should_add_space:
                    current_group.append(' ')
                current_group.append(char_text)

            prev_char = char

        # Add final group
        if current_group and current_style:
            result.append(self.create_styled_span(current_group, current_style))

        return ''.join(result)

    def extract_font_family(self, font_name):
        """Extract readable font family name from PDF font name"""
        if not font_name:
            return 'Arial'

        # Remove prefix (e.g., "ABCDEF+")
        font_name = re.sub(r'^[A-Z]{6}\+', '', font_name)

        # Map common PDF fonts to web-safe fonts
        font_map = {
            'times': 'Times New Roman, serif',
            'arial': 'Arial, sans-serif',
            'helvetica': 'Helvetica, Arial, sans-serif',
            'courier': 'Courier New, monospace',
            'calibri': 'Calibri, sans-serif',
            'verdana': 'Verdana, sans-serif',
            'georgia': 'Georgia, serif'
        }

        font_lower = font_name.lower()
        for key, value in font_map.items():
            if key in font_lower:
                return value

        # Default to sans-serif
        return 'Arial, sans-serif'

    def create_styled_span(self, chars, style):
        """Create a styled span element"""
        text = ''.join(chars)
        text_escaped = self.escape_html(text)

        # Build inline CSS
        css_parts = []

        if style.get('font'):
            css_parts.append(f"font-family: {style['font']}")

        if style.get('size') and abs(style['size'] - self.default_font_size) > 0.5:
            css_parts.append(f"font-size: {style['size']}pt")

        if style.get('bold'):
            css_parts.append("font-weight: bold")

        if style.get('italic'):
            css_parts.append("font-style: italic")

        if style.get('color') and isinstance(style['color'], (list, tuple)):
            # Convert RGB color to hex
            try:
                if len(style['color']) >= 3:
                    r, g, b = [int(c * 255) for c in style['color'][:3]]
                    # Only apply if not black (default text color)
                    if not (r < 50 and g < 50 and b < 50):
                        css_parts.append(f"color: rgb({r}, {g}, {b})")
            except:
                pass

        if css_parts:
            style_attr = '; '.join(css_parts)
            return f'<span style="{style_attr}">{text_escaped}</span>'
        else:
            return text_escaped

    def text_to_html_with_style(self, text, chars):
        """Convert text to HTML preserving inline styles"""
        # This method is now replaced by create_styled_paragraph
        return f'<p>{self.escape_html(text)}</p>'

    def is_title_case(self, text):
        """Check if text is in title case"""
        words = text.split()
        if len(words) == 0:
            return False
        # Allow for articles and short words to be lowercase
        capitalized = sum(1 for i, word in enumerate(words)
                         if word and (word[0].isupper() or (i > 0 and len(word) <= 3)))
        return capitalized / len(words) > 0.6

    def escape_html(self, text):
        """Escape HTML special characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))

    def fix_word_spacing(self, text):
        """Fix missing spaces in text by detecting word boundaries"""
        if not text:
            return text

        # Dictionary of common concatenated phrases and their corrected forms
        replacements = {
            'Startdate': 'Start date',
            'Lastdaytoenroll': 'Last day to enroll',
            'Enrollmentfeerefunddeadline': 'Enrollment fee refund deadline',
            'Coursesclose': 'Courses close',
            'Importantdates': 'Important dates',
            # Case variations
            'startdate': 'start date',
            'lastdaytoenroll': 'last day to enroll',
            'enrollmentfeerefunddeadline': 'enrollment fee refund deadline',
            'coursesclose': 'courses close',
            'importantdates': 'important dates',
        }

        # Apply dictionary replacements
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Add space before uppercase letters that follow lowercase letters
        # e.g., "FallA" -> "Fall A"
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

        # Add space before numbers that follow letters
        # e.g., "August19" -> "August 19"
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)

        # Add space after commas between numbers (for dates)
        # e.g., "19,2025" -> "19, 2025"
        text = re.sub(r'(\d),(\d)', r'\1, \2', text)

        return text

    def table_to_html_with_style(self, table):
        """Convert table data to accessible HTML table with styling"""
        if not table or len(table) == 0:
            return ''

        html_parts = ['<table>']

        # First row as header
        if table[0]:
            html_parts.append('<thead><tr>')
            for cell in table[0]:
                cell_text = str(cell) if cell else ''
                cell_text = self.fix_word_spacing(cell_text)  # Fix word spacing
                html_parts.append(f'<th scope="col">{self.escape_html(cell_text)}</th>')
            html_parts.append('</tr></thead>')

        # Remaining rows as body
        html_parts.append('<tbody>')
        for row in table[1:]:
            html_parts.append('<tr>')
            for cell in row:
                cell_text = str(cell) if cell else ''
                cell_text = self.fix_word_spacing(cell_text)  # Fix word spacing
                html_parts.append(f'<td>{self.escape_html(cell_text)}</td>')
            html_parts.append('</tr>')
        html_parts.append('</tbody>')
        html_parts.append('</table>')

        return '\n'.join(html_parts)

    def create_exact_replica_html(self, body_content, extracted_styles):
        """Create complete HTML document with exact PDF layout"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remediated Document</title>
    <style>
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background-color: #f0f0f0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}

        /* PDF Page container - exact replica */
        .pdf-page {{
            background-color: #ffffff;
            margin: 20px auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}

        /* Preserve exact positioning */
        .pdf-page > div {{
            line-height: 1.0;
        }}

        /* Table styles - accessibility compliant */
        table {{
            border-collapse: collapse;
            background-color: #ffffff;
        }}
        th, td {{
            border: 1px solid #cccccc;
            padding: 8px 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #2c3e50;
            color: #ffffff;
            font-weight: 700;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        /* Link accessibility */
        a {{
            color: #0066cc;
            text-decoration: underline;
        }}
        a:hover {{
            color: #0052a3;
        }}
        a:focus {{
            outline: 3px solid #0066cc;
            outline-offset: 2px;
            background-color: #ffffcc;
        }}

        /* Skip navigation for accessibility */
        .skip-link {{
            position: absolute;
            top: -40px;
            left: 0;
            background: #000000;
            color: #ffffff;
            padding: 8px;
            text-decoration: none;
            z-index: 100;
            font-weight: bold;
        }}
        .skip-link:focus {{
            top: 0;
        }}

        /* Image accessibility */
        img {{
            max-width: 100%;
            height: auto;
        }}

        /* Ensure spans display inline */
        span {{
            display: inline;
        }}

        /* Print styles */
        @media print {{
            body {{
                background-color: #ffffff;
                padding: 0;
            }}
            .pdf-page {{
                box-shadow: none;
                margin: 0;
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <main id="main-content">
        {body_content}
    </main>
</body>
</html>'''

    def create_html_structure_with_styles(self, body_content, extracted_styles):
        """Create complete HTML document with preserved styles (legacy method)"""
        return self.create_exact_replica_html(body_content, extracted_styles)

    def remediate_html(self, html_content):
        """Apply WCAG 2.2 AA accessibility remediations while preserving exact layout"""
        soup = BeautifulSoup(html_content, 'html5lib')

        # Add language attribute if missing
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            html_tag['lang'] = 'en'

        # Ensure document title
        if not soup.find('title'):
            head = soup.find('head')
            if head:
                title = soup.new_tag('title')
                title.string = 'Remediated Document'
                head.append(title)

        # Add alt text to images (preserving layout)
        self.add_alt_text_to_images(soup)

        # Ensure tables have proper headers and captions (preserving position)
        self.remediate_tables(soup)

        # Fix links (preserving layout)
        self.remediate_links(soup)

        # Ensure form elements have labels (if any, preserving position)
        self.remediate_forms(soup)

        # Ensure main landmark has id (skip navigation already in template)
        main = soup.find('main')
        if main and not main.get('id'):
            main['id'] = 'main-content'

        # Use html formatter to avoid self-closing tags
        html_output = soup.decode(formatter='html')

        # Remove self-closing slashes from void elements (HTML5 compliance)
        void_elements = ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                        'link', 'meta', 'param', 'source', 'track', 'wbr']
        for element in void_elements:
            # Replace <element .../> with <element ...>
            html_output = re.sub(rf'<{element}([^>]*?)\s*/>', rf'<{element}\1>', html_output, flags=re.IGNORECASE)

        return html_output

    def ensure_document_structure(self, soup):
        """Ensure proper HTML5 document structure"""
        # Ensure there's a main element
        if not soup.find('main'):
            body = soup.find('body')
            if body:
                # Wrap body content in main
                main = soup.new_tag('main', attrs={'id': 'main-content'})
                for child in list(body.children):
                    main.append(child.extract())
                body.append(main)

    def fix_heading_hierarchy(self, soup):
        """Ensure headings follow proper hierarchy (no skipped levels)"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        if not headings:
            # Add a default h1 if no headings exist
            main = soup.find('main')
            if main:
                h1 = soup.new_tag('h1')
                h1.string = 'Document'
                main.insert(0, h1)
            return

        # Ensure first heading is h1
        first_heading = headings[0]
        if first_heading.name != 'h1':
            # Check if we should convert first heading to h1 or add a new h1
            main = soup.find('main')
            if main and len(first_heading.get_text(strip=True)) < 100:
                # Convert first heading to h1
                first_heading.name = 'h1'
            else:
                # Add a document title h1
                if main:
                    h1 = soup.new_tag('h1')
                    h1.string = 'Document'
                    main.insert(0, h1)

        # Fix heading hierarchy - no skipped levels
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        last_level = 1

        for heading in headings:
            current_level = int(heading.name[1])

            # If we skip levels (e.g., h1 to h3), adjust
            if current_level > last_level + 1:
                # Adjust to proper level
                heading.name = f'h{last_level + 1}'
                current_level = last_level + 1

            last_level = current_level

    def add_alt_text_to_images(self, soup):
        """Add alt text to images"""
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                # Add descriptive alt text placeholder
                img['alt'] = 'Document image'
                # Add role if decorative
                # img['role'] = 'presentation'  # Uncomment if image is decorative

    def remediate_tables(self, soup):
        """Ensure tables are accessible with proper WCAG 2.2 AA structure"""
        tables = soup.find_all('table')
        for i, table in enumerate(tables, 1):
            # Add accessible name if missing (caption or aria-label)
            if not table.find('caption'):
                # Try to generate a meaningful caption from table headers
                meaningful_caption = self.generate_table_caption(table, i)

                if meaningful_caption:
                    # Add as visible caption only if it's descriptive
                    caption = soup.new_tag('caption')
                    caption.string = meaningful_caption
                    table.insert(0, caption)
                else:
                    # Use aria-label for accessibility without visible caption
                    if not table.get('aria-label'):
                        table['aria-label'] = f'Data table {i}'

            # Ensure th elements have scope
            headers = table.find_all('th')
            for th in headers:
                if not th.get('scope'):
                    # Determine if it's a column or row header
                    parent = th.parent
                    if parent.parent and parent.parent.name == 'thead':
                        th['scope'] = 'col'
                    else:
                        th['scope'] = 'row'

    def generate_table_caption(self, table, table_num):
        """Generate a meaningful caption based on table content, or return None for generic tables"""
        # Try to extract headers to understand table purpose
        thead = table.find('thead')
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all('th')]

            # If headers contain meaningful information, use them
            if headers and len(headers) > 0:
                # Check if headers suggest a specific type of data
                header_text = ' '.join(headers).lower()

                # Look for keywords that suggest meaningful content
                keywords = {
                    'date': 'Schedule',
                    'term': 'Academic Calendar',
                    'semester': 'Academic Calendar',
                    'course': 'Course Information',
                    'student': 'Student Data',
                    'grade': 'Grade Information',
                    'schedule': 'Schedule',
                    'event': 'Events',
                    'deadline': 'Important Dates',
                    'price': 'Pricing',
                    'cost': 'Costs',
                    'name': 'Directory'
                }

                for keyword, caption in keywords.items():
                    if keyword in header_text:
                        return caption

        # If we can't generate a meaningful caption, return None
        # This will use aria-label instead of a visible caption
        return None

    def remediate_links(self, soup):
        """Ensure links are accessible"""
        links = soup.find_all('a')
        for link in links:
            # Ensure links have meaningful text
            link_text = link.get_text(strip=True)
            if not link_text:
                href = link.get('href', '')
                if href:
                    link.string = href
                else:
                    link.string = 'Link'
                link_text = link.get_text(strip=True)

            # Add title attribute for additional context if needed
            href = link.get('href', '')
            if href.startswith('http'):
                if not link.get('title'):
                    link['title'] = f"External link: {link_text}"
                # Add target and rel for external links
                if not link.get('target'):
                    link['target'] = '_blank'
                if not link.get('rel'):
                    link['rel'] = ['noopener', 'noreferrer']

    def remediate_forms(self, soup):
        """Ensure form elements have proper labels"""
        inputs = soup.find_all(['input', 'select', 'textarea'])
        for input_elem in inputs:
            # Ensure input has an ID
            if not input_elem.get('id'):
                continue

            # Check if there's a label
            label = soup.find('label', attrs={'for': input_elem['id']})
            if not label:
                # Check if input is wrapped in a label
                parent_label = input_elem.find_parent('label')
                if not parent_label:
                    # Add aria-label if no label exists
                    if not input_elem.get('aria-label'):
                        input_type = input_elem.get('type', input_elem.name)
                        input_elem['aria-label'] = f'{input_type.capitalize()} field'

    def add_skip_navigation(self, soup):
        """Add skip navigation link for keyboard users"""
        body = soup.find('body')
        if body:
            # Check if skip link already exists
            if not soup.find('a', attrs={'class': 'skip-link'}):
                skip_link = soup.new_tag('a', attrs={
                    'href': '#main-content',
                    'class': 'skip-link'
                })
                skip_link.string = 'Skip to main content'
                body.insert(0, skip_link)

                # Ensure main has the corresponding ID
                main = soup.find('main')
                if main and not main.get('id'):
                    main['id'] = 'main-content'

    def add_aria_landmarks(self, soup):
        """Add ARIA landmarks for better navigation"""
        # Main landmark
        main = soup.find('main')
        if main and not main.get('role'):
            main['role'] = 'main'

    def html_to_pdf_with_browser(self, html_content, output_path):
        """
        Convert HTML to PDF using Playwright browser rendering.
        This method produces PDFs that closely match browser print output
        and maintain excellent accessibility.
        """
        # Detect page orientation from HTML
        orientation, page_info = self.detect_page_orientation(html_content)

        print(f"📄 Page Info: {page_info['width_inches']:.1f}\" × {page_info['height_inches']:.1f}\" ({orientation})")
        print(f"📄 Total pages: {page_info['num_pages']}")

        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_html:
            tmp_html.write(html_content)
            tmp_html_path = tmp_html.name

        try:
            # Use Playwright to render HTML and save as PDF
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()

                # Load the HTML file
                page.goto(f'file://{tmp_html_path}')

                # Wait for page to be fully rendered
                page.wait_for_load_state('networkidle')

                # Determine PDF format based on orientation
                pdf_format = 'Letter' if orientation == 'portrait' else 'Ledger' if orientation == 'landscape' else 'Letter'

                # Generate PDF with browser rendering
                page.pdf(
                    path=output_path,
                    format=pdf_format if orientation in ['portrait', 'landscape'] else None,
                    landscape=(orientation == 'landscape'),
                    print_background=True,
                    prefer_css_page_size=True,  # Respect CSS page size if specified
                    tagged=True  # Enable PDF tagging for accessibility
                )

                browser.close()

            print(f"✅ PDF generated successfully using browser rendering")
            return True

        except Exception as e:
            print(f"❌ Error generating PDF with browser: {e}")
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_html_path):
                os.unlink(tmp_html_path)

    def detect_page_orientation(self, html_content):
        """
        Detect page orientation (portrait or landscape) from HTML content.
        Returns orientation and page information.
        """
        soup = BeautifulSoup(html_content, 'html5lib')

        # Find all pdf-page divs to get dimensions
        pdf_pages = soup.find_all('div', class_='pdf-page')

        if pdf_pages:
            # Get dimensions from first page
            first_page = pdf_pages[0]
            style = first_page.get('style', '')

            # Extract width and height from style attribute
            width_match = re.search(r'width:\s*(\d+(?:\.\d+)?)pt', style)
            height_match = re.search(r'height:\s*(\d+(?:\.\d+)?)pt', style)

            if width_match and height_match:
                width_pt = float(width_match.group(1))
                height_pt = float(height_match.group(1))

                # Convert points to inches (72 points = 1 inch)
                width_inches = width_pt / 72
                height_inches = height_pt / 72

                # Determine orientation
                if width_pt > height_pt:
                    orientation = 'landscape'
                elif height_pt > width_pt:
                    orientation = 'portrait'
                else:
                    orientation = 'square'

                page_info = {
                    'width_pt': width_pt,
                    'height_pt': height_pt,
                    'width_inches': width_inches,
                    'height_inches': height_inches,
                    'num_pages': len(pdf_pages)
                }

                return orientation, page_info

        # Default to portrait Letter size if no page info found
        return 'portrait', {
            'width_pt': 612,
            'height_pt': 792,
            'width_inches': 8.5,
            'height_inches': 11,
            'num_pages': 1
        }

    def html_to_tagged_pdf(self, html_content, output_path):
        """Convert remediated HTML to properly tagged PDF with accessibility structure"""
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html5lib')

        # Create PDF with ReportLab
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
            title="Remediated Document",
            author="PDF Remediation Tool"
        )

        # Define styles with proper tagging
        styles = getSampleStyleSheet()

        # Create custom styles for headings
        for i in range(1, 7):
            style_name = f'Heading{i}'
            if style_name not in styles:
                base_size = 24 - (i * 2)
                styles.add(ParagraphStyle(
                    name=style_name,
                    parent=styles['Heading1'],
                    fontSize=base_size,
                    textColor=HexColor('#2c3e50'),
                    spaceAfter=12,
                    spaceBefore=12 if i == 1 else 6,
                    keepWithNext=1,
                    fontName='Helvetica-Bold'
                ))

        # Update body text style
        styles['BodyText'].fontSize = 12
        styles['BodyText'].leading = 16
        styles['BodyText'].textColor = HexColor('#333333')
        styles['BodyText'].alignment = 4  # Justified

        # Build content
        story = []

        # Extract main content
        main = soup.find('main')
        if main:
            # First try to find semantic elements
            content_elements = main.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'table'], recursive=False)

            # If no semantic elements found, extract from positioned divs
            if not content_elements:
                content_elements = self.convert_positioned_divs_to_semantic(main, soup)

            for element in content_elements:
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # Add heading
                    level = int(element.name[1])
                    text = element.get_text(strip=True)
                    if text:
                        story.append(Paragraph(text, styles[f'Heading{level}']))
                        story.append(Spacer(1, 0.1 * inch))

                elif element.name == 'p':
                    # Add paragraph
                    text = element.get_text(strip=True)
                    if text:
                        story.append(Paragraph(text, styles['BodyText']))
                        story.append(Spacer(1, 0.15 * inch))

                elif element.name == 'table':
                    # Add table
                    table_story = self.table_to_reportlab(element, styles)
                    if table_story:
                        story.extend(table_story)
                        story.append(Spacer(1, 0.2 * inch))

        # Build PDF
        try:
            if story:
                doc.build(story)
                return True
            else:
                print("Error: No content to add to PDF")
                return False
        except Exception as e:
            print(f"Error creating PDF: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simpler PDF creation
            return self.html_to_simple_pdf(html_content, output_path)

    def convert_positioned_divs_to_semantic(self, main, soup):
        """Convert positioned div structure to semantic HTML elements for PDF generation"""
        semantic_elements = []

        # Find all pdf-page divs
        pdf_pages = main.find_all('div', class_='pdf-page')

        for pdf_page in pdf_pages:
            # Get all positioned divs (lines of text)
            positioned_divs = pdf_page.find_all('div', style=lambda value: value and 'position: absolute' in value)

            # Sort by vertical position (top value)
            def get_top_position(div):
                style = div.get('style', '')
                try:
                    # Extract top value from style
                    for part in style.split(';'):
                        if 'top:' in part:
                            return float(part.split('top:')[1].replace('pt', '').strip())
                except:
                    pass
                return 0

            positioned_divs.sort(key=get_top_position)

            # Convert each line to a paragraph
            for div in positioned_divs:
                text = div.get_text(strip=True)
                if text:
                    # Create a new paragraph element
                    p = soup.new_tag('p')
                    p.string = text
                    semantic_elements.append(p)

        # Also get tables which should already be semantic
        tables = main.find_all('table')
        semantic_elements.extend(tables)

        return semantic_elements

    def table_to_reportlab(self, table_element, styles):
        """Convert HTML table to ReportLab Table with accessibility"""
        story = []

        # Extract caption
        caption = table_element.find('caption')
        if caption:
            caption_text = caption.get_text(strip=True)
            story.append(Paragraph(f"<b>{caption_text}</b>", styles['BodyText']))
            story.append(Spacer(1, 0.1 * inch))

        # Extract table data
        data = []

        # Get headers
        thead = table_element.find('thead')
        if thead:
            header_row = []
            for th in thead.find_all('th'):
                text = th.get_text(strip=True) or ' '  # Ensure not empty
                header_row.append(Paragraph(f"<b>{text}</b>", styles['BodyText']))
            if header_row:
                data.append(header_row)

        # Get body rows
        tbody = table_element.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                row = []
                for td in tr.find_all('td'):
                    text = td.get_text(strip=True) or ' '  # Ensure not empty
                    row.append(Paragraph(text, styles['BodyText']))
                if row:
                    data.append(row)

        if data:
            # Calculate column widths based on number of columns
            num_cols = len(data[0]) if data else 0
            if num_cols > 0:
                # Available width (letter size with margins: 8.5" - 2" = 6.5")
                available_width = 6.5 * inch
                col_width = available_width / num_cols

                # Create column widths list
                col_widths = [col_width] * num_cols

                # Create table with styling and explicit column widths
                t = Table(data, colWidths=col_widths, repeatRows=1)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#8C1D40')),  # ASU Maroon
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
                ]))
                story.append(t)

        return story

    def html_to_simple_pdf(self, html_content, output_path):
        """Fallback: Simple PDF creation if ReportLab complex method fails"""
        from xhtml2pdf import pisa

        with open(output_path, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_file
            )

        return not pisa_status.err

    def apply_specific_fix(self, html_content, issue_type):
        """Apply a specific accessibility fix based on issue type"""
        soup = BeautifulSoup(html_content, 'html5lib')

        if issue_type == 'missing_title':
            # Fix: Add or update document title
            if not soup.find('title'):
                head = soup.find('head')
                if head:
                    title = soup.new_tag('title')
                    title.string = 'Remediated Document'
                    head.append(title)

        elif issue_type == 'missing_lang':
            # Fix: Add language attribute
            html_tag = soup.find('html')
            if html_tag:
                html_tag['lang'] = 'en'

        elif issue_type == 'missing_alt_text':
            # Fix: Add alt text to all images
            images = soup.find_all('img')
            for img in images:
                if not img.get('alt'):
                    # Try to get meaningful alt from src
                    src = img.get('src', '')
                    if src:
                        filename = src.split('/')[-1].split('.')[0]
                        img['alt'] = filename.replace('_', ' ').replace('-', ' ').title()
                    else:
                        img['alt'] = 'Image'

        elif issue_type == 'missing_table_headers':
            # Fix: Add headers to tables
            self.remediate_tables(soup)

        elif issue_type == 'missing_table_caption':
            # Fix: Add captions to tables
            tables = soup.find_all('table')
            for i, table in enumerate(tables, 1):
                if not table.find('caption'):
                    caption = soup.new_tag('caption')
                    caption.string = f'Table {i}'
                    table.insert(0, caption)

        elif issue_type == 'heading_hierarchy':
            # Fix: Fix heading hierarchy
            self.fix_heading_hierarchy(soup)

        elif issue_type == 'missing_skip_nav':
            # Fix: Add skip navigation
            self.add_skip_navigation(soup)

        elif issue_type == 'missing_landmarks':
            # Fix: Add ARIA landmarks
            self.add_aria_landmarks(soup)

        elif issue_type == 'empty_links':
            # Fix: Fix links with no text
            links = soup.find_all('a')
            for link in links:
                if not link.get_text(strip=True):
                    href = link.get('href', '')
                    if href:
                        link.string = href
                    else:
                        link.string = 'Link'

        elif issue_type == 'form_labels':
            # Fix: Add labels to form elements
            self.remediate_forms(soup)

        elif issue_type == 'color_contrast':
            # Fix: Improve color contrast (generic fix)
            # This is a placeholder - real implementation would require color analysis
            style_tag = soup.find('style')
            if style_tag:
                style_content = style_tag.string or ''
                # Add high contrast CSS
                style_content += '''
                /* High Contrast Override */
                body { color: #1a1a1a !important; }
                a { color: #0066cc !important; }
                '''
                style_tag.string = style_content

        return str(soup)
