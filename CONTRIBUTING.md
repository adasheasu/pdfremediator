# Contributing to PDF Remediator

Thank you for your interest in contributing to PDF Remediator! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race or ethnicity
- Age
- Religion
- Nationality

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or inflammatory remarks
- Personal attacks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. Check the [GitHub Issues](https://github.com/adasheasu/pdfremediator/issues) to avoid duplicates
2. Verify the bug with the latest version

When creating a bug report, include:
- **Clear title and description**
- **Steps to reproduce**
- **Expected vs. actual behavior**
- **PDF characteristics** (pages, size, complexity)
- **System information**:
  - Operating system and version
  - Python version
  - pikepdf version
- **Error messages** (complete traceback)
- **Sample PDF** (if possible, or description)

**Example bug report**:
```markdown
**Title**: Reading order incorrect for multi-column layout

**Description**:
PDFs with two-column layouts have incorrect reading order after remediation.

**Steps to Reproduce**:
1. Use PDF with 2-column layout
2. Run: python pdf_remediator.py document.pdf
3. Open in NVDA screen reader
4. Reading order jumps between columns incorrectly

**Expected**: Sequential reading (column 1, then column 2)
**Actual**: Reading alternates between columns

**System**:
- macOS 14.0
- Python 3.9.6
- pikepdf 9.11.0

**Sample PDF**: [link or description]
```

---

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub Issues. Include:
- **Use case**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches
- **WCAG relevance**: Which criteria does this address?
- **Priority**: High/Medium/Low
- **Implementation notes**: Technical considerations

**Example enhancement**:
```markdown
**Title**: Add OCR integration for scanned PDFs

**Use Case**:
Users need to remediate scanned PDFs that lack text layer.

**Proposed Solution**:
Integrate Tesseract OCR to add text layer before remediation.

**Alternatives**:
- External OCR, then remediate
- Document requirement for pre-OCR

**WCAG**: 1.1.1 Non-text Content

**Priority**: High (common use case)

**Implementation**:
- Optional dependency (tesseract-ocr)
- New --ocr flag for command-line
- API method: remediator.apply_ocr()
```

---

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
6. **Push to your fork**
7. **Submit a Pull Request**

---

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- pikepdf 8.0.0 or higher

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/your-username/pdfremediator.git
cd pdfremediator

# Add upstream remote
git remote add upstream https://github.com/adasheasu/pdfremediator.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pdf_remediator

# Run specific test
pytest tests/test_images.py
```

### Code Formatting

```bash
# Format code with black
black pdf_remediator.py

# Check with flake8
flake8 pdf_remediator.py
```

---

## Pull Request Process

### Before Submitting

1. **Update documentation** for any new features
2. **Add tests** for new functionality
3. **Run all tests** and ensure they pass
4. **Format code** with black
5. **Update CHANGELOG.md** with your changes
6. **Rebase on latest main**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Pull Request Template

```markdown
## Description
[Clear description of changes]

## Related Issue
Fixes #[issue number]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests for changes
- [ ] Tested with sample PDFs
- [ ] Verified WCAG compliance

## Checklist
- [ ] Code follows project style
- [ ] Self-reviewed code
- [ ] Commented complex sections
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests
- [ ] All tests pass

## Screenshots/Examples
[If applicable, add screenshots or example output]
```

### Review Process

1. **Automated checks** run on PR submission
2. **Code review** by maintainers
3. **Requested changes** (if needed)
4. **Approval and merge** by maintainers

---

## Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) with these specifics:

**Naming**:
```python
# Classes: PascalCase
class ImageInfo:
    pass

# Functions/methods: snake_case
def analyze_images():
    pass

# Constants: UPPER_CASE
MAX_IMAGE_SIZE = 1000

# Private: _leading_underscore
def _internal_method():
    pass
```

**Docstrings**:
```python
def remediate(self, options: Dict[str, Any]) -> None:
    """
    Remediate PDF for accessibility.

    Parameters:
        options (dict): Remediation options
            - title (str): Document title
            - language (str): Document language

    Raises:
        ValueError: If options are invalid

    Example:
        >>> remediator.remediate({'title': 'Document'})
    """
```

**Type Hints**:
```python
from typing import List, Dict, Optional

def analyze_images(self) -> List[ImageInfo]:
    """Return list of detected images."""
    pass

def get_metadata(self) -> Dict[str, str]:
    """Return document metadata."""
    pass

def find_image(self, name: str) -> Optional[ImageInfo]:
    """Return image info or None."""
    pass
```

### Code Organization

```python
# 1. Imports (stdlib, third-party, local)
import os
from typing import List, Dict
from dataclasses import dataclass

import pikepdf

from .utils import helper_function

# 2. Constants
DEFAULT_LANGUAGE = 'en-US'
MAX_ALT_TEXT_LENGTH = 250

# 3. Data classes
@dataclass
class ImageInfo:
    name: str
    width: int

# 4. Main classes
class EnhancedPDFRemediator:
    def __init__(self):
        pass

# 5. Helper functions
def parse_image_name(name: str) -> str:
    pass
```

### Error Handling

```python
# Specific exceptions
try:
    self.pdf = pikepdf.open(self.input_path)
except FileNotFoundError:
    raise FileNotFoundError(f"PDF not found: {self.input_path}")
except pikepdf.PasswordError:
    raise ValueError("PDF is password-protected")

# Cleanup in finally
try:
    # processing
    pass
finally:
    if self.pdf:
        self.pdf.close()
```

---

## Testing Guidelines

### Test Structure

```python
import pytest
from pdf_remediator import EnhancedPDFRemediator, ImageInfo

class TestImageAnalysis:
    """Tests for image analysis functionality."""

    def test_decorative_detection_size(self):
        """Test decorative detection based on size."""
        img = ImageInfo(name='/Im1', width=10, height=10, page_number=1)
        assert img.determine_if_decorative() == True

    def test_descriptive_detection(self):
        """Test descriptive image detection."""
        img = ImageInfo(name='/Im1', width=800, height=600, page_number=1)
        assert img.determine_if_decorative() == False

    def test_alt_text_generation(self):
        """Test alt text generation for various image types."""
        # Wide image
        img = ImageInfo(name='/Im1', width=1000, height=300, page_number=1)
        img.is_decorative = False
        assert "Diagram or illustration" in img.generate_alt_text()
```

### Test Coverage

Aim for:
- **>80% code coverage** overall
- **100% for critical paths**:
  - Image tagging
  - Structure creation
  - Reading order
  - Metadata handling

### Sample PDFs for Testing

Create test PDFs in `tests/fixtures/`:
- `simple_text.pdf` - Basic text document
- `with_images.pdf` - Document with multiple images
- `with_tables.pdf` - Document with tables
- `layered.pdf` - PDF with layers
- `multi_column.pdf` - Complex layout

---

## Documentation

### Code Comments

```python
# Good: Explains why, not what
# Flatten layers to enable proper tagging (layered PDFs can't be tagged)
if options.get('flatten', True):
    self.flatten_layers()

# Not needed: Obvious from code
# Set title to title variable
self.title = title
```

### Docstring Requirements

All public methods need docstrings with:
- Brief description
- Parameters with types
- Return value and type
- Raises (exceptions)
- Example (for complex methods)

### Documentation Updates

When adding features, update:
- `README.md` - Main overview
- `docs/USAGE.md` - Usage examples
- `docs/API.md` - API reference
- `docs/ENHANCED_FEATURES.md` - Feature documentation
- `CHANGELOG.md` - Version history

---

## Areas for Contribution

### High Priority

1. **OCR Integration**
   - Add Tesseract OCR support
   - Process scanned PDFs
   - Language detection

2. **Machine Learning Alt Text**
   - Image classification
   - Context-aware descriptions
   - Training on accessible PDFs

3. **Advanced Table Detection**
   - Content stream parsing
   - Complex table structures
   - Nested tables

4. **Heading Detection**
   - Font size analysis
   - Style pattern recognition
   - Hierarchy inference

### Medium Priority

5. **Form Field Labeling**
   - Automatic label detection
   - Field type identification
   - Validation hints

6. **Color Contrast Checking**
   - Extract colors
   - Calculate ratios
   - Suggest fixes

7. **Batch Processing UI**
   - Web interface
   - Progress tracking
   - Report generation

8. **Math Accessibility**
   - MathML generation
   - Equation tagging
   - Formula descriptions

### Low Priority

9. **Template System**
   - Reusable configurations
   - Organization presets
   - Custom rules

10. **Multi-language Support**
    - UI localization
    - Documentation translations
    - Examples in multiple languages

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Examples

```
feat(images): Add machine learning alt text generation

Integrate TensorFlow model for intelligent alt text based on
image content classification.

Closes #42
```

```
fix(reading-order): Fix multi-column layout detection

Improved algorithm for detecting reading order in multi-column
layouts. Now correctly handles 2-column and 3-column PDFs.

Fixes #56
```

---

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Creating a Release

1. Update version in `pdf_remediator.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v2.1.0 -m "Release v2.1.0"`
4. Push tag: `git push origin v2.1.0`
5. Create GitHub release with notes

---

## Getting Help

### Resources

- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)
- **Issues**: [GitHub Issues](https://github.com/adasheasu/pdfremediator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adasheasu/pdfremediator/discussions)

### Questions

- Check [existing issues](https://github.com/adasheasu/pdfremediator/issues)
- Review [documentation](docs/)
- Ask in [GitHub Discussions](https://github.com/adasheasu/pdfremediator/discussions)

---

## Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Acknowledged in documentation

Thank you for contributing to PDF accessibility!

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Last Updated**: October 2025
