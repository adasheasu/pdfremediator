# Quick Start Guide

## Getting Started

### 1. Navigate to the project directory
```bash
cd pdf_remediation_tool
```

### 2. Run the start script (recommended)
```bash
./start.sh
```

This will:
- Create a virtual environment (if needed)
- Install all dependencies
- Start the web server automatically

### 3. Or start manually
```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python3 app.py
```

### 4. Access the tool
Open your browser and go to:
```
http://localhost:5000
```

### 5. Use the tool
1. Upload a PDF file by dragging and dropping or clicking "Choose PDF File"
2. Wait for processing to complete
3. Download the remediated HTML and/or PDF files

## Features

The tool automatically:
- ✓ Converts PDF to structured HTML
- ✓ Adds proper document structure (headings, landmarks)
- ✓ Creates accessible tables with headers
- ✓ Ensures keyboard navigation support
- ✓ Adds skip navigation links
- ✓ Maintains sufficient color contrast
- ✓ Generates WCAG 2.2 AA compliant HTML
- ✓ Converts back to PDF format
- ✓ Allows downloading both formats

## Troubleshooting

### Port 5000 is already in use
If port 5000 is already in use, edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Virtual environment issues
Delete the `venv` folder and run `./start.sh` again:
```bash
rm -rf venv
./start.sh
```

### Dependencies not installing
Make sure you have Python 3.8+ installed:
```bash
python3 --version
```

## Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## File Cleanup

Temporary files are automatically cleaned up when you click "Process Another Document" or when sessions expire.
