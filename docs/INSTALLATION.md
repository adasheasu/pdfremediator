# Installation Guide

Complete installation instructions for PDF Remediator on Windows, macOS, and Linux.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Platform-Specific Installation](#platform-specific-installation)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Linux](#linux)
- [Virtual Environment Setup](#virtual-environment-setup)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting](#troubleshooting)
- [Updating](#updating)
- [Uninstalling](#uninstalling)

---

## System Requirements

### Minimum Requirements

- **Python**: 3.7 or higher
- **pip**: Latest version recommended
- **Disk Space**: 50 MB minimum
- **RAM**: 512 MB minimum

### Recommended

- **Python**: 3.9 or higher
- **pip**: 23.0 or higher
- **Disk Space**: 500 MB (for processing large PDFs)
- **RAM**: 2 GB or higher

### Dependencies

- **pikepdf**: 8.0.0 or higher (automatically installed)
- **qpdf**: Backend library (usually installed with pikepdf)

---

## Quick Installation

For most users, the quick installation method works:

```bash
# Clone the repository
git clone https://github.com/adasheasu/pdfremediator.git
cd pdfremediator

# Install dependencies
pip install -r requirements.txt

# Verify installation
python pdf_remediator.py --help
```

---

## Platform-Specific Installation

### macOS

#### Prerequisites

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3** (if not already installed):
   ```bash
   brew install python3
   ```

3. **Verify Python installation**:
   ```bash
   python3 --version
   # Should show Python 3.7 or higher
   ```

#### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/adasheasu/pdfremediator.git
   cd pdfremediator
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Make script executable** (optional):
   ```bash
   chmod +x pdf_remediator.py
   ```

4. **Verify installation**:
   ```bash
   python3 pdf_remediator.py --help
   ```

#### Xcode Command Line Tools (if needed)

If you encounter build errors, you may need Xcode Command Line Tools:

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Accept license if prompted
sudo xcodebuild -license accept
```

---

### Windows

#### Prerequisites

1. **Install Python 3**:
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation:
     ```cmd
     python --version
     ```

2. **Install Git** (optional, for cloning):
   - Download from [git-scm.com](https://git-scm.com/download/win)

#### Installation Steps

##### Option 1: Using Git

```cmd
# Clone the repository
git clone https://github.com/adasheasu/pdfremediator.git
cd pdfremediator

# Install dependencies
pip install -r requirements.txt

# Verify installation
python pdf_remediator.py --help
```

##### Option 2: Download ZIP

1. Download ZIP from GitHub repository
2. Extract to desired location
3. Open Command Prompt in extracted folder
4. Run:
   ```cmd
   pip install -r requirements.txt
   python pdf_remediator.py --help
   ```

#### PowerShell Users

If using PowerShell, replace `python` with `python.exe`:

```powershell
python.exe pdf_remediator.py --help
```

---

### Linux

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip git

# Clone repository
git clone https://github.com/adasheasu/pdfremediator.git
cd pdfremediator

# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python3 pdf_remediator.py --help
```

#### Fedora/RHEL/CentOS

```bash
# Install Python 3 and pip
sudo dnf install python3 python3-pip git

# Clone repository
git clone https://github.com/adasheasu/pdfremediator.git
cd pdfremediator

# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python3 pdf_remediator.py --help
```

#### Arch Linux

```bash
# Install Python and Git
sudo pacman -S python python-pip git

# Clone repository
git clone https://github.com/adasheasu/pdfremediator.git
cd pdfremediator

# Install dependencies
pip install -r requirements.txt

# Verify installation
python pdf_remediator.py --help
```

---

## Virtual Environment Setup

Using a virtual environment is recommended to avoid dependency conflicts.

### Create Virtual Environment

#### macOS/Linux

```bash
# Navigate to repository
cd pdfremediator

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

#### Windows (Command Prompt)

```cmd
# Navigate to repository
cd pdfremediator

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

#### Windows (PowerShell)

```powershell
# Navigate to repository
cd pdfremediator

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### Using Virtual Environment

Always activate the virtual environment before using the tool:

```bash
# macOS/Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

---

## Verifying Installation

### Test Basic Functionality

```bash
# Display help
python pdf_remediator.py --help

# Check version (shows Python version)
python --version

# Verify pikepdf
python -c "import pikepdf; print(f'pikepdf version: {pikepdf.__version__}')"
```

### Expected Output

```
usage: pdf_remediator.py [-h] [-o OUTPUT] [--analyze-only]
                          [--title TITLE] [--author AUTHOR]
                          [--subject SUBJECT] [--keywords KEYWORDS]
                          [--language LANGUAGE] [--flatten | --no-flatten]
                          [--report-format {text,json}]
                          [--report-file REPORT_FILE]
                          input
...
```

### Test with Sample PDF

If you have a test PDF:

```bash
# Analyze only (no changes)
python pdf_remediator.py test.pdf --analyze-only

# Full remediation
python pdf_remediator.py test.pdf -o output.pdf
```

---

## Troubleshooting

### Issue: "python: command not found"

**Solution**:
- macOS/Linux: Use `python3` instead of `python`
- Windows: Add Python to PATH during installation

### Issue: "pip: command not found"

**Solution**:
- macOS/Linux: Use `pip3` instead of `pip`
- Windows: Reinstall Python with "Add to PATH" option

### Issue: "Permission denied"

**Solution** (macOS/Linux):
```bash
# Make script executable
chmod +x pdf_remediator.py

# Or use python3 explicitly
python3 pdf_remediator.py input.pdf
```

### Issue: "ModuleNotFoundError: No module named 'pikepdf'"

**Solution**:
```bash
# Install pikepdf directly
pip install pikepdf

# Or reinstall from requirements
pip install -r requirements.txt
```

### Issue: pikepdf build errors on macOS

**Solution**:
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Accept Xcode license
sudo xcodebuild -license accept

# Reinstall pikepdf
pip install --upgrade pikepdf
```

### Issue: pikepdf build errors on Linux

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc gcc-c++ python3-devel

# Then reinstall
pip install pikepdf
```

### Issue: "Cannot open PDF file"

**Causes**:
- File path is incorrect
- File is corrupted
- File is password-protected
- Insufficient permissions

**Solution**:
```bash
# Check file exists
ls -l path/to/file.pdf

# Check file permissions
chmod 644 path/to/file.pdf

# Try absolute path
python pdf_remediator.py /full/path/to/file.pdf
```

### Issue: Virtual environment activation fails (Windows PowerShell)

**Solution**:
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\Activate.ps1
```

### Issue: SSL certificate errors

**Solution**:
```bash
# Upgrade pip
pip install --upgrade pip

# Upgrade certifi
pip install --upgrade certifi

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Updating

### Update from Git

```bash
# Navigate to repository
cd pdfremediator

# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Update Dependencies Only

```bash
# Update all dependencies
pip install --upgrade pikepdf

# Or update from requirements
pip install --upgrade -r requirements.txt
```

### Check for Updates

```bash
# Check current pikepdf version
pip show pikepdf

# Check available updates
pip list --outdated
```

---

## Uninstalling

### Remove Dependencies

```bash
# Uninstall pikepdf
pip uninstall pikepdf

# Or uninstall all requirements
pip uninstall -r requirements.txt -y
```

### Remove Repository

```bash
# Delete repository directory
rm -rf pdfremediator

# Or on Windows
rmdir /s /q pdfremediator
```

### Remove Virtual Environment

```bash
# Deactivate if active
deactivate

# Remove virtual environment directory
rm -rf venv

# Or on Windows
rmdir /s /q venv
```

---

## Advanced Configuration

### Custom Installation Location

```bash
# Install to custom location
pip install --target=/custom/path pikepdf

# Set PYTHONPATH
export PYTHONPATH="/custom/path:$PYTHONPATH"
```

### User Installation (No sudo)

```bash
# Install for current user only
pip install --user -r requirements.txt

# Script location
~/.local/bin/pdf_remediator.py
```

### Offline Installation

```bash
# Download dependencies (on machine with internet)
pip download -r requirements.txt -d packages/

# Install offline (on target machine)
pip install --no-index --find-links=packages/ -r requirements.txt
```

---

## System-Wide Installation (Not Recommended)

For system-wide installation (requires administrator/root):

### macOS/Linux

```bash
# Install system-wide
sudo pip3 install -r requirements.txt

# Copy script to system location
sudo cp pdf_remediator.py /usr/local/bin/

# Make executable
sudo chmod +x /usr/local/bin/pdf_remediator.py
```

### Windows

```cmd
# Run as Administrator
pip install -r requirements.txt

# Add to PATH
setx PATH "%PATH%;C:\path\to\pdfremediator"
```

**Note**: Virtual environment installation is preferred for better dependency management.

---

## Docker Installation (Alternative)

For containerized deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_remediator.py .

ENTRYPOINT ["python", "pdf_remediator.py"]
```

Build and run:

```bash
# Build image
docker build -t pdf-remediator .

# Run container
docker run -v $(pwd):/data pdf-remediator /data/input.pdf
```

---

## Support

If you encounter installation issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Verify [System Requirements](#system-requirements)
3. Review [GitHub Issues](https://github.com/adasheasu/pdfremediator/issues)
4. Create new issue with:
   - Operating system and version
   - Python version
   - Complete error message
   - Installation steps attempted

---

## Next Steps

After successful installation:

1. Read [Usage Guide](USAGE.md)
2. Review [Enhanced Features](ENHANCED_FEATURES.md)
3. Check [API Reference](API.md)
4. Try example workflows

---

**Installation Guide Version**: 2.0
**Last Updated**: October 2025
**Supported Platforms**: Windows, macOS, Linux
