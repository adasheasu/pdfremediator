"""
Accessibility Report Generator
Creates HTML and downloadable reports for WCAG 2.2 AA compliance
"""

from datetime import datetime
import json


class ReportGenerator:
    def generate_html_report(self, report_data):
        """Generate user-friendly HTML accessibility report"""

        status_info = self.get_status_info(report_data)

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WCAG 2.2 AA Accessibility Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}

        .header {{
            background: {status_info['color']};
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .status-badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 1.1em;
            margin-top: 10px;
        }}

        .header .compliance-score {{
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }}

        .content {{
            padding: 40px;
        }}

        .summary-box {{
            background: #f8f9fa;
            border-left: 5px solid {status_info['color']};
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
        }}

        .summary-box h2 {{
            color: {status_info['color']};
            margin-bottom: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
        }}

        .stat-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}

        .stat-card.error {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }}

        .stat-card.warning {{
            background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        }}

        .stat-card .number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .stat-card .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .section {{
            margin: 40px 0;
        }}

        .section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #e0e0e0;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .issue-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-left: 5px solid #eb3349;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}

        .issue-card.warning {{
            border-left-color: #f2994a;
        }}

        .issue-card .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}

        .issue-card .issue-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
        }}

        .issue-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .issue-badge.error {{
            background: #ffebee;
            color: #c62828;
        }}

        .issue-badge.warning {{
            background: #fff3e0;
            color: #e65100;
        }}

        .issue-badge.level {{
            background: #e3f2fd;
            color: #1565c0;
            margin-left: 10px;
        }}

        .issue-description {{
            color: #666;
            margin: 10px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }}

        .remediation-box {{
            background: #e8f5e9;
            border-left: 3px solid #4caf50;
            padding: 15px;
            margin-top: 15px;
            border-radius: 6px;
        }}

        .remediation-box h4 {{
            color: #2e7d32;
            margin-bottom: 8px;
        }}

        .remediation-box p {{
            color: #1b5e20;
        }}

        .guideline-tag {{
            display: inline-block;
            background: #f5f5f5;
            color: #666;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            margin-right: 5px;
            font-family: 'Courier New', monospace;
        }}

        .task-list {{
            background: #fff8e1;
            border-left: 5px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }}

        .task-list h3 {{
            color: #f57c00;
            margin-bottom: 15px;
        }}

        .task-item {{
            padding: 12px;
            background: white;
            border-radius: 6px;
            margin-bottom: 10px;
            display: flex;
            align-items: start;
        }}

        .task-checkbox {{
            width: 20px;
            height: 20px;
            border: 2px solid #ffc107;
            border-radius: 4px;
            margin-right: 15px;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        .passed-list {{
            background: #f1f8f4;
            padding: 20px;
            border-radius: 8px;
        }}

        .passed-list h3 {{
            color: #2e7d32;
            margin-bottom: 15px;
        }}

        .passed-item {{
            padding: 10px;
            background: white;
            border-left: 3px solid #4caf50;
            margin-bottom: 8px;
            border-radius: 4px;
        }}

        .action-buttons {{
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 40px 0;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}

        .btn-secondary {{
            background: #2c3e50;
            color: white;
        }}

        .btn-secondary:hover {{
            background: #34495e;
            transform: translateY(-2px);
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            .action-buttons {{
                display: none;
            }}

            .issue-card {{
                page-break-inside: avoid;
            }}
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 WCAG 2.2 AA Accessibility Report</h1>
            <div class="status-badge">{status_info['status_text']}</div>
            <div class="compliance-score">{report_data['compliance_score']}%</div>
            <p>Compliance Score</p>
        </div>

        <div class="content">
            <div class="summary-box">
                <h2>{report_data['summary']['message']}</h2>
                <p>{report_data['summary']['recommendation']}</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card success">
                    <div class="number">{report_data['passed_count']}</div>
                    <div class="label">Checks Passed</div>
                </div>
                <div class="stat-card error">
                    <div class="number">{report_data['issues_count']}</div>
                    <div class="label">Critical Issues</div>
                </div>
                <div class="stat-card warning">
                    <div class="number">{report_data['warnings_count']}</div>
                    <div class="label">Warnings</div>
                </div>
                <div class="stat-card">
                    <div class="number">{report_data['total_checks']}</div>
                    <div class="label">Total Checks</div>
                </div>
            </div>

            {self.generate_task_list_html(report_data)}

            {self.generate_issues_html(report_data['issues'], 'Critical Issues', 'error')}

            {self.generate_issues_html(report_data['warnings'], 'Warnings', 'warning')}

            {self.generate_passed_checks_html(report_data['passed_checks'])}

            <div class="action-buttons">
                <a href="/" class="btn btn-primary">Process Another Document</a>
                <button onclick="window.print()" class="btn btn-secondary">Print Report</button>
            </div>
        </div>

        <div class="footer">
            <p>Generated: {report_data['timestamp']}</p>
            <p>WCAG 2.2 Level AA Accessibility Report | PDF Remediation Tool</p>
        </div>
    </div>

    <script>
        // Add checkbox functionality for task list
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {{
            checkbox.addEventListener('click', function() {{
                this.style.background = this.style.background ? '' : '#4caf50';
                this.innerHTML = this.innerHTML ? '' : '✓';
                this.style.color = 'white';
                this.style.textAlign = 'center';
                this.style.lineHeight = '20px';
            }});
        }});
    </script>
</body>
</html>'''

        return html

    def get_status_info(self, report_data):
        """Get status information for styling"""
        status = report_data['summary']['status']

        status_map = {
            'pass': {
                'color': '#4caf50',
                'status_text': '✅ WCAG 2.2 AA Compliant'
            },
            'near_pass': {
                'color': '#ff9800',
                'status_text': '⚠️ Near Compliance - Minor Issues'
            },
            'needs_work': {
                'color': '#ff5722',
                'status_text': '❌ Needs Significant Work'
            },
            'fail': {
                'color': '#f44336',
                'status_text': '❌ Not Compliant'
            }
        }

        return status_map.get(status, status_map['fail'])

    def generate_task_list_html(self, report_data):
        """Generate remediation task list"""
        if not report_data['issues'] and not report_data['warnings']:
            return ''

        tasks = []

        # Add critical issues first
        for issue in report_data['issues']:
            tasks.append({
                'priority': 'high',
                'task': issue['title'],
                'action': issue['remediation']
            })

        # Add warnings
        for warning in report_data['warnings']:
            tasks.append({
                'priority': 'medium',
                'task': warning['title'],
                'action': warning['remediation']
            })

        html = '''
        <div class="task-list">
            <h3>🎯 Remediation Task List</h3>
            <p style="margin-bottom: 15px;">Complete these tasks to improve accessibility compliance:</p>
        '''

        for i, task in enumerate(tasks, 1):
            priority_emoji = '🔴' if task['priority'] == 'high' else '🟡'
            html += f'''
            <div class="task-item">
                <div class="task-checkbox"></div>
                <div>
                    <strong>{priority_emoji} Task {i}: {task['task']}</strong>
                    <p style="margin-top: 5px; color: #666;">{task['action']}</p>
                </div>
            </div>
            '''

        html += '</div>'
        return html

    def generate_issues_html(self, issues, title, severity):
        """Generate HTML for issues section"""
        if not issues:
            return ''

        html = f'''
        <div class="section">
            <h2>{title} ({len(issues)})</h2>
        '''

        for issue in issues:
            html += f'''
            <div class="issue-card {severity}">
                <div class="issue-header">
                    <div>
                        <div class="issue-title">{issue['title']}</div>
                        <div style="margin-top: 8px;">
                            <span class="guideline-tag">WCAG {issue['guideline']}</span>
                            <span class="issue-badge level">Level {issue['level']}</span>
                            <span class="issue-badge {severity}">{severity.upper()}</span>
                        </div>
                    </div>
                </div>

                <div class="issue-description">
                    <strong>Issue:</strong> {issue['description']}
                </div>

                <div class="remediation-box">
                    <h4>✅ How to Fix:</h4>
                    <p>{issue['remediation']}</p>
                </div>

                <p style="margin-top: 10px; color: #999; font-size: 0.9em;">
                    <em>{issue['guideline_name']}</em>
                </p>
            </div>
            '''

        html += '</div>'
        return html

    def generate_passed_checks_html(self, passed_checks):
        """Generate HTML for passed checks"""
        if not passed_checks:
            return ''

        html = '''
        <div class="section">
            <h2>✅ Passed Checks</h2>
            <div class="passed-list">
                <h3>The following accessibility checks passed:</h3>
        '''

        for check in passed_checks:
            html += f'''
            <div class="passed-item">
                <span class="guideline-tag">WCAG {check['guideline']}</span>
                <strong>{check['title']}</strong>
            </div>
            '''

        html += '''
            </div>
        </div>
        '''

        return html

    def generate_text_report(self, report_data):
        """Generate plain text report for download"""
        text = f'''WCAG 2.2 AA ACCESSIBILITY REPORT
=====================================

Generated: {report_data['timestamp']}
Compliance Score: {report_data['compliance_score']}%
Status: {report_data['summary']['message']}

SUMMARY
-------
{report_data['summary']['recommendation']}

STATISTICS
----------
Total Checks: {report_data['total_checks']}
Passed: {report_data['passed_count']}
Critical Issues: {report_data['issues_count']}
Warnings: {report_data['warnings_count']}

'''

        if report_data['issues']:
            text += f'''CRITICAL ISSUES ({len(report_data['issues'])})
================

'''
            for i, issue in enumerate(report_data['issues'], 1):
                text += f'''{i}. {issue['title']}
   WCAG Guideline: {issue['guideline']} - {issue['guideline_name']}
   Level: {issue['level']}

   Issue: {issue['description']}

   How to Fix: {issue['remediation']}

'''

        if report_data['warnings']:
            text += f'''WARNINGS ({len(report_data['warnings'])})
=========

'''
            for i, warning in enumerate(report_data['warnings'], 1):
                text += f'''{i}. {warning['title']}
   WCAG Guideline: {warning['guideline']} - {warning['guideline_name']}

   Issue: {warning['description']}

   Recommendation: {warning['remediation']}

'''

        if report_data['passed_checks']:
            text += f'''PASSED CHECKS ({len(report_data['passed_checks'])})
=============

'''
            for check in report_data['passed_checks']:
                text += f"✓ {check['title']} (WCAG {check['guideline']})\n"

        text += '''
---
Report generated by PDF Remediation Tool
'''

        return text
