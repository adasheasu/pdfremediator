#!/usr/bin/env python3
"""
PDF Remediation Tool
Converts PDF to HTML, remediates for WCAG 2.2 AA compliance, and converts back to PDF
"""

from flask import Flask, render_template, request, send_file, jsonify, Response
import os
from werkzeug.utils import secure_filename
import uuid
from pdf_processor import PDFProcessor
from accessibility_checker import AccessibilityChecker
from report_generator import ReportGenerator
import shutil
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

processor = PDFProcessor()
checker = AccessibilityChecker()
report_gen = ReportGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_folder, exist_ok=True)

        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(session_folder, filename)
        file.save(input_path)

        # Process the PDF
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_folder, exist_ok=True)

        result = processor.process_pdf(input_path, output_folder)

        # Run accessibility check on remediated HTML
        html_path = os.path.join(output_folder, result['html_file'])
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Pass OCR warning if detected
        accessibility_report = checker.check_accessibility(html_content, processor.ocr_warning)

        # Save report data
        report_path = os.path.join(output_folder, 'accessibility_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(accessibility_report, f, indent=2)

        # Generate HTML report
        html_report = report_gen.generate_html_report(accessibility_report)
        html_report_path = os.path.join(output_folder, 'accessibility_report.html')
        with open(html_report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

        # Generate text report for download
        text_report = report_gen.generate_text_report(accessibility_report)
        text_report_path = os.path.join(output_folder, 'accessibility_report.txt')
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write(text_report)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'html_file': result['html_file'],
            'pdf_file': result['pdf_file'],
            'original_name': filename,
            'accessibility_report': accessibility_report,
            'has_issues': accessibility_report['issues_count'] > 0 or accessibility_report['warnings_count'] > 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    try:
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)

        # Find the actual files (they use original filename + _remediated)
        if file_type == 'html':
            # Find HTML file
            html_files = [f for f in os.listdir(output_folder) if f.endswith('_remediated.html')]
            if not html_files:
                return jsonify({'error': 'HTML file not found'}), 404
            file_path = os.path.join(output_folder, html_files[0])
            mimetype = 'text/html'
            download_name = html_files[0]
        elif file_type == 'pdf':
            # Find PDF file
            pdf_files = [f for f in os.listdir(output_folder) if f.endswith('_remediated.pdf')]
            if not pdf_files:
                return jsonify({'error': 'PDF file not found'}), 404
            file_path = os.path.join(output_folder, pdf_files[0])
            mimetype = 'application/pdf'
            download_name = pdf_files[0]
        elif file_type == 'report_txt':
            file_path = os.path.join(output_folder, 'accessibility_report.txt')
            mimetype = 'text/plain'
            download_name = 'accessibility_report.txt'
        else:
            return jsonify({'error': 'Invalid file type'}), 400

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(file_path, mimetype=mimetype, as_attachment=True, download_name=download_name)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<session_id>')
def view_report(session_id):
    try:
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        report_path = os.path.join(output_folder, 'accessibility_report.html')

        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404

        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return Response(html_content, mimetype='text/html')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/remediate/<session_id>')
def interactive_remediate(session_id):
    """Show interactive remediation page"""
    try:
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        report_path = os.path.join(output_folder, 'accessibility_report.json')

        if not os.path.exists(report_path):
            return jsonify({'error': 'Session not found'}), 404

        return render_template('remediate.html', session_id=session_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/issues/<session_id>')
def get_issues(session_id):
    """Get list of accessibility issues for interactive remediation"""
    try:
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        report_path = os.path.join(output_folder, 'accessibility_report.json')

        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404

        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        # Convert report issues to interactive format
        issues = []
        issue_id = 0

        for issue in report.get('issues', []):
            issues.append({
                'id': issue_id,
                'type': issue.get('type', 'unknown'),
                'title': issue['title'],
                'description': issue['description'],
                'remediation': issue['remediation'],
                'severity': 'critical',
                'guidelines': [issue['guideline']],
                'element_preview': issue.get('element', '')
            })
            issue_id += 1

        for warning in report.get('warnings', []):
            issues.append({
                'id': issue_id,
                'type': warning.get('type', 'unknown'),
                'title': warning['title'],
                'description': warning['description'],
                'remediation': warning['remediation'],
                'severity': 'warning',
                'guidelines': [warning['guideline']],
                'element_preview': warning.get('element', '')
            })
            issue_id += 1

        return jsonify({
            'success': True,
            'issues': issues,
            'total': len(issues)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fix-issue/<session_id>', methods=['POST'])
def fix_issue(session_id):
    """Auto-fix a specific accessibility issue"""
    try:
        data = request.json
        issue_type = data.get('issue_type')

        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)

        # Find the actual HTML file (uses original filename + _remediated)
        html_files = [f for f in os.listdir(output_folder) if f.endswith('_remediated.html')]
        if not html_files:
            return jsonify({'error': 'HTML file not found'}), 404

        html_path = os.path.join(output_folder, html_files[0])

        # Read current HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Apply specific fix based on issue type
        fixed_html = processor.apply_specific_fix(html_content, issue_type)

        # Save updated HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(fixed_html)

        # Regenerate PDF with fixed HTML using browser rendering
        pdf_files = [f for f in os.listdir(output_folder) if f.endswith('_remediated.pdf')]
        if pdf_files:
            pdf_path = os.path.join(output_folder, pdf_files[0])
            processor.html_to_pdf_with_browser(fixed_html, pdf_path)

        # Re-run accessibility check
        accessibility_report = checker.check_accessibility(fixed_html)

        # Save updated report
        report_path = os.path.join(output_folder, 'accessibility_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(accessibility_report, f, indent=2)

        return jsonify({
            'success': True,
            'message': 'Issue fixed successfully',
            'new_compliance_score': accessibility_report['compliance_score']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup/<session_id>', methods=['POST'])
def cleanup(session_id):
    try:
        # Clean up session files
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)

        if os.path.exists(upload_folder):
            shutil.rmtree(upload_folder)
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
