"""
WCAG 2.2 AA Accessibility Checker
Validates HTML documents and generates detailed compliance reports
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime


class AccessibilityChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed_checks = []
        self.wcag_guidelines = {
            '1.1.1': 'Non-text Content (Level A)',
            '1.3.1': 'Info and Relationships (Level A)',
            '1.3.2': 'Meaningful Sequence (Level A)',
            '1.4.3': 'Contrast (Minimum) (Level AA)',
            '2.1.1': 'Keyboard (Level A)',
            '2.4.1': 'Bypass Blocks (Level A)',
            '2.4.2': 'Page Titled (Level A)',
            '2.4.4': 'Link Purpose (In Context) (Level A)',
            '2.4.6': 'Headings and Labels (Level AA)',
            '3.1.1': 'Language of Page (Level A)',
            '3.1.2': 'Language of Parts (Level AA)',
            '4.1.2': 'Name, Role, Value (Level A)',
        }

        # Help resource links
        self.help_resources = {
            'adobe_headings': 'https://helpx.adobe.com/acrobat/using/editing-document-structure-content-tags.html#add_headings_to_a_pdf',
            'adobe_tags': 'https://helpx.adobe.com/acrobat/using/editing-document-structure-content-tags.html',
            'adobe_alt_text': 'https://helpx.adobe.com/acrobat/using/editing-document-structure-content-tags.html#add_alternate_text_and_supplementary_information',
            'adobe_tables': 'https://helpx.adobe.com/acrobat/using/editing-document-structure-content-tags.html#edit_table_tags',
            'adobe_reading_order': 'https://helpx.adobe.com/acrobat/using/touch-reading-order-tool-pdfs.html'
        }

    def check_accessibility(self, html_content, ocr_warning=None):
        """Run all WCAG 2.2 AA accessibility checks"""
        soup = BeautifulSoup(html_content, 'html5lib')

        # Reset issues
        self.issues = []
        self.warnings = []
        self.passed_checks = []

        # Add OCR warning if provided
        if ocr_warning:
            self.add_ocr_warning(ocr_warning)

        # Run checks
        self.check_document_title(soup)
        self.check_language(soup)
        self.check_heading_hierarchy(soup)
        self.check_images(soup)
        self.check_links(soup)
        self.check_tables(soup)
        self.check_forms(soup)
        self.check_skip_navigation(soup)
        self.check_aria_landmarks(soup)
        self.check_color_contrast(soup)
        self.check_semantic_structure(soup)

        # Generate report
        return self.generate_report()

    def add_ocr_warning(self, warning_message):
        """Add OCR detection warning to the report"""
        self.add_issue(
            'N/A',
            'OCR Detection Warning',
            warning_message,
            f'''Consider using OCR (Optical Character Recognition) tools to extract text from this PDF before remediation for best results. Scanned or graphically-rendered PDFs cannot be properly remediated without text content.
            <br><br><strong>📚 Learn How to Fix:</strong><br>
            • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
            'warning',
            'ocr_needed'
        )

    def add_issue(self, guideline, title, description, remediation, severity='error', issue_type='unknown'):
        """Add an accessibility issue"""
        issue = {
            'guideline': guideline,
            'guideline_name': self.wcag_guidelines.get(guideline, 'Unknown'),
            'title': title,
            'description': description,
            'remediation': remediation,
            'severity': severity,
            'level': 'AA' if guideline in ['1.4.3', '2.4.6', '3.1.2'] else 'A',
            'type': issue_type
        }

        if severity == 'error':
            self.issues.append(issue)
        else:
            self.warnings.append(issue)

    def add_passed_check(self, guideline, title):
        """Add a passed accessibility check"""
        self.passed_checks.append({
            'guideline': guideline,
            'guideline_name': self.wcag_guidelines.get(guideline, 'Unknown'),
            'title': title
        })

    def check_document_title(self, soup):
        """Check if document has a title (WCAG 2.4.2)"""
        title = soup.find('title')

        if not title or not title.get_text(strip=True):
            self.add_issue(
                '2.4.2',
                'Missing or Empty Page Title',
                'The document does not have a title or the title is empty.',
                f'''Add a descriptive &lt;title&gt; element in the &lt;head&gt; section that describes the page content.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'error',
                'missing_title'
            )
        else:
            title_text = title.get_text(strip=True)
            if len(title_text) < 3:
                self.add_issue(
                    '2.4.2',
                    'Page Title Too Short',
                    f'The page title "{title_text}" is too short to be meaningful.',
                    f'''Use a descriptive title that clearly identifies the page content (e.g., "Annual Report 2024" instead of "Document").
                    <br><br><strong>📚 Learn How to Fix:</strong><br>
                    • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                    'warning'
                )
            else:
                self.add_passed_check('2.4.2', 'Page has a meaningful title')

    def check_language(self, soup):
        """Check if document has language attribute (WCAG 3.1.1)"""
        html_tag = soup.find('html')

        if not html_tag or not html_tag.get('lang'):
            self.add_issue(
                '3.1.1',
                'Missing Language Declaration',
                'The HTML element does not have a lang attribute.',
                f'''Add a lang attribute to the &lt;html&gt; element (e.g., &lt;html lang="en"&gt; for English).
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'error',
                'missing_lang'
            )
        else:
            lang = html_tag.get('lang')
            if len(lang) < 2:
                self.add_issue(
                    '3.1.1',
                    'Invalid Language Code',
                    f'The lang attribute "{lang}" is not a valid language code.',
                    f'''Use a valid ISO 639-1 language code (e.g., "en" for English, "es" for Spanish).
                    <br><br><strong>📚 Learn How to Fix:</strong><br>
                    • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                    'error'
                )
            else:
                self.add_passed_check('3.1.1', f'Document language declared as "{lang}"')

    def check_heading_hierarchy(self, soup):
        """Check heading hierarchy (WCAG 2.4.6, 1.3.1)"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        if not headings:
            self.add_issue(
                '2.4.6',
                'No Headings Found',
                'The document does not contain any headings.',
                f'''Add headings (h1-h6) to structure your content hierarchically. Start with an h1 for the main title.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_headings']}" target="_blank">Adobe Acrobat: Add Headings to PDF</a><br>''',
                'error',
                'missing_headings'
            )
            return

        # Check if first heading is h1
        first_heading = headings[0]
        if first_heading.name != 'h1':
            self.add_issue(
                '2.4.6',
                'First Heading is Not H1',
                f'The first heading is {first_heading.name.upper()}, not H1.',
                f'''Ensure the first heading in your document is an h1 element.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_headings']}" target="_blank">Adobe Acrobat: Add Headings to PDF</a><br>''',
                'error',
                'wrong_first_heading'
            )

        # Check for skipped levels
        last_level = 0
        skipped_levels = []

        for heading in headings:
            current_level = int(heading.name[1])

            if last_level > 0 and current_level > last_level + 1:
                skipped_levels.append(f'h{last_level} to h{current_level}')

            last_level = current_level

        if skipped_levels:
            self.add_issue(
                '1.3.1',
                'Skipped Heading Levels',
                f'Heading levels are skipped: {", ".join(set(skipped_levels))}',
                f'''Do not skip heading levels. After h1, use h2; after h2, use h3, etc.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_headings']}" target="_blank">Adobe Acrobat: Add Headings to PDF</a><br>''',
                'error',
                'skipped_heading_levels'
            )
        else:
            self.add_passed_check('2.4.6', 'Heading hierarchy is logical (no skipped levels)')

        # Check for empty headings
        empty_headings = [h for h in headings if not h.get_text(strip=True)]
        if empty_headings:
            self.add_issue(
                '2.4.6',
                'Empty Headings Found',
                f'Found {len(empty_headings)} empty heading(s).',
                f'''Ensure all headings contain descriptive text.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_headings']}" target="_blank">Adobe Acrobat: Add Headings to PDF</a><br>''',
                'error'
            )
        else:
            self.add_passed_check('2.4.6', 'All headings contain text')

    def check_images(self, soup):
        """Check images have alt text (WCAG 1.1.1)"""
        images = soup.find_all('img')

        if not images:
            self.add_passed_check('1.1.1', 'No images found')
            return

        missing_alt = []
        empty_alt = []

        for img in images:
            if not img.has_attr('alt'):
                missing_alt.append(img.get('src', 'unknown'))
            elif not img['alt'].strip():
                # Empty alt is okay for decorative images
                pass

        if missing_alt:
            self.add_issue(
                '1.1.1',
                'Images Missing Alt Text',
                f'{len(missing_alt)} image(s) do not have alt attributes.',
                f'''Add alt attributes to all images. Use descriptive text for meaningful images, or alt="" for decorative images.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_alt_text']}" target="_blank">Adobe Acrobat: Add Alternative Text</a><br>''',
                'error',
                'missing_alt_text'
            )
        else:
            self.add_passed_check('1.1.1', f'All {len(images)} images have alt attributes')

    def check_links(self, soup):
        """Check links are accessible (WCAG 2.4.4)"""
        links = soup.find_all('a')

        if not links:
            self.add_passed_check('2.4.4', 'No links found')
            return

        issues_found = []

        for link in links:
            link_text = link.get_text(strip=True)
            href = link.get('href', '')

            # Check for empty link text
            if not link_text:
                issues_found.append(f'Empty link: {href[:50]}')

            # Check for generic link text
            generic_texts = ['click here', 'read more', 'more', 'link', 'here']
            if link_text.lower() in generic_texts:
                issues_found.append(f'Generic link text: "{link_text}"')

            # Check external links have security attributes
            if href.startswith('http'):
                if not link.get('rel') or 'noopener' not in link.get('rel', []):
                    issues_found.append(f'External link missing security attributes: {link_text[:50]}')

        if issues_found:
            self.add_issue(
                '2.4.4',
                'Link Accessibility Issues',
                f'Found {len(issues_found)} link issue(s).',
                f'''Ensure links have descriptive text. Avoid generic phrases like "click here". Add rel="noopener noreferrer" to external links.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'warning'
            )
        else:
            self.add_passed_check('2.4.4', f'All {len(links)} links have descriptive text')

    def check_tables(self, soup):
        """Check tables are accessible (WCAG 1.3.1)"""
        tables = soup.find_all('table')

        if not tables:
            self.add_passed_check('1.3.1', 'No tables found')
            return

        issues_found = []

        for i, table in enumerate(tables, 1):
            # Check for caption
            if not table.find('caption'):
                issues_found.append(f'Table {i} missing caption')

            # Check for headers
            headers = table.find_all('th')
            if not headers:
                issues_found.append(f'Table {i} has no header cells (th)')
            else:
                # Check headers have scope
                for th in headers:
                    if not th.get('scope'):
                        issues_found.append(f'Table {i} header missing scope attribute')
                        break

            # Check for role
            if not table.get('role'):
                issues_found.append(f'Table {i} missing role="table"')

        if issues_found:
            self.add_issue(
                '1.3.1',
                'Table Accessibility Issues',
                f'Found issues in {len(set(issues_found))} table(s).',
                f'''Add captions to tables, use &lt;th&gt; elements for headers with scope attributes, and add role="table" for ARIA support.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tables']}" target="_blank">Adobe Acrobat: Edit Table Tags</a><br>''',
                'error',
                'table_accessibility'
            )
        else:
            self.add_passed_check('1.3.1', f'All {len(tables)} tables are properly structured')

    def check_forms(self, soup):
        """Check form accessibility (WCAG 4.1.2)"""
        inputs = soup.find_all(['input', 'select', 'textarea'])

        if not inputs:
            self.add_passed_check('4.1.2', 'No form elements found')
            return

        unlabeled = []

        for input_elem in inputs:
            elem_id = input_elem.get('id')
            has_label = False

            # Check for label element
            if elem_id:
                label = soup.find('label', attrs={'for': elem_id})
                if label:
                    has_label = True

            # Check for parent label
            if not has_label:
                parent_label = input_elem.find_parent('label')
                if parent_label:
                    has_label = True

            # Check for aria-label
            if not has_label and input_elem.get('aria-label'):
                has_label = True

            if not has_label:
                unlabeled.append(input_elem.name)

        if unlabeled:
            self.add_issue(
                '4.1.2',
                'Form Elements Missing Labels',
                f'{len(unlabeled)} form element(s) do not have associated labels.',
                f'''Associate labels with form controls using &lt;label for="id"&gt; or wrap inputs in &lt;label&gt; tags. Alternatively, use aria-label attributes.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'error'
            )
        else:
            self.add_passed_check('4.1.2', f'All {len(inputs)} form elements have labels')

    def check_skip_navigation(self, soup):
        """Check for skip navigation link (WCAG 2.4.1)"""
        skip_links = soup.find_all('a', href=re.compile(r'#.*content'))

        if not skip_links:
            self.add_issue(
                '2.4.1',
                'Missing Skip Navigation Link',
                'No skip navigation link found.',
                f'''Add a "Skip to main content" link at the beginning of the page that links to the main content area.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'error'
            )
        else:
            self.add_passed_check('2.4.1', 'Skip navigation link present')

    def check_aria_landmarks(self, soup):
        """Check for ARIA landmarks (WCAG 1.3.1)"""
        main_element = soup.find('main')

        if not main_element:
            self.add_issue(
                '1.3.1',
                'Missing Main Landmark',
                'No &lt;main&gt; element found.',
                f'''Wrap the main content in a &lt;main&gt; element.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'error'
            )
        else:
            if not main_element.get('role'):
                self.add_issue(
                    '1.3.1',
                    'Main Element Missing Role',
                    'The &lt;main&gt; element does not have role="main".',
                    f'''Add role="main" to the &lt;main&gt; element.
                    <br><br><strong>📚 Learn How to Fix:</strong><br>
                    • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                    'warning'
                )
            else:
                self.add_passed_check('1.3.1', 'Main landmark properly defined')

    def check_color_contrast(self, soup):
        """Check color contrast in CSS (WCAG 1.4.3)"""
        # This is a simplified check - full contrast checking requires rendering
        style_tag = soup.find('style')

        if style_tag:
            style_content = style_tag.string
            if style_content:
                # Check for common low-contrast patterns
                low_contrast_patterns = [
                    ('color: #999', 'background'),
                    ('color: #ccc', 'background'),
                    ('color: gray', 'background')
                ]

                issues_found = []
                for pattern, context in low_contrast_patterns:
                    if pattern in style_content.lower():
                        issues_found.append(pattern)

                if issues_found:
                    self.add_issue(
                        '1.4.3',
                        'Potential Color Contrast Issues',
                        'Found potential low-contrast color combinations in CSS.',
                        f'''Ensure text has a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text. Use a contrast checker tool.
                        <br><br><strong>📚 Learn How to Fix:</strong><br>
                        • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                        'warning'
                    )
                else:
                    self.add_passed_check('1.4.3', 'No obvious color contrast issues detected')
        else:
            self.add_passed_check('1.4.3', 'No inline styles to check')

    def check_semantic_structure(self, soup):
        """Check for semantic HTML structure (WCAG 1.3.1)"""
        body = soup.find('body')

        if not body:
            self.add_issue(
                '1.3.1',
                'Missing Body Element',
                'No &lt;body&gt; element found.',
                f'''Ensure the document has a proper HTML structure with &lt;body&gt; element.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'error'
            )
            return

        # Check for proper use of semantic elements
        semantic_elements = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
        found_elements = [elem for elem in semantic_elements if soup.find(elem)]

        if len(found_elements) < 2:
            self.add_issue(
                '1.3.1',
                'Limited Semantic Structure',
                'The document uses few or no semantic HTML5 elements.',
                f'''Use semantic HTML5 elements like &lt;header&gt;, &lt;nav&gt;, &lt;main&gt;, &lt;article&gt;, &lt;section&gt;, &lt;aside&gt;, and &lt;footer&gt; to structure your content.
                <br><br><strong>📚 Learn How to Fix:</strong><br>
                • <a href="{self.help_resources['adobe_tags']}" target="_blank">Adobe Acrobat: Document Structure and Tags</a><br>''',
                'warning'
            )
        else:
            self.add_passed_check('1.3.1', f'Document uses semantic HTML5 elements: {", ".join(found_elements)}')

    def generate_report(self):
        """Generate accessibility report"""
        total_checks = len(self.issues) + len(self.warnings) + len(self.passed_checks)
        passed_count = len(self.passed_checks)
        issues_count = len(self.issues)
        warnings_count = len(self.warnings)

        # Calculate compliance score
        if total_checks > 0:
            compliance_score = int((passed_count / total_checks) * 100)
        else:
            compliance_score = 0

        # Determine pass/fail status
        passes_wcag = issues_count == 0

        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'compliance_score': compliance_score,
            'passes_wcag': passes_wcag,
            'total_checks': total_checks,
            'passed_count': passed_count,
            'issues_count': issues_count,
            'warnings_count': warnings_count,
            'issues': self.issues,
            'warnings': self.warnings,
            'passed_checks': self.passed_checks,
            'summary': self.generate_summary(passes_wcag, compliance_score)
        }

        return report

    def generate_summary(self, passes_wcag, compliance_score):
        """Generate executive summary"""
        if passes_wcag:
            return {
                'status': 'pass',
                'message': 'Congratulations! Your document meets WCAG 2.2 Level AA requirements.',
                'recommendation': 'Continue to maintain accessibility standards in future updates.'
            }
        elif compliance_score >= 80:
            return {
                'status': 'near_pass',
                'message': 'Your document is close to meeting WCAG 2.2 Level AA requirements.',
                'recommendation': 'Address the critical issues listed below to achieve full compliance.'
            }
        elif compliance_score >= 50:
            return {
                'status': 'needs_work',
                'message': 'Your document has significant accessibility issues that need attention.',
                'recommendation': 'Review and address all critical issues to improve accessibility.'
            }
        else:
            return {
                'status': 'fail',
                'message': 'Your document does not meet WCAG 2.2 Level AA requirements.',
                'recommendation': 'Significant remediation work is required. Start with critical issues first.'
            }
