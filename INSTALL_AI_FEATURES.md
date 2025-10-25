# Installing AI Alt-Text Features - Complete Setup Guide

## Overview

This guide provides step-by-step instructions for installing and configuring the AI-powered alt-text generation features for PDF Remediator.

---

## Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.7 or higher installed
- ✅ pip (Python package manager)
- ✅ PDF Remediator installed
- ✅ Internet connection (for AI API calls)

---

## Installation Steps

### Step 1: Install Base Dependencies

These are required for PDF Remediator to work:

```bash
cd /Users/alejandradashe/pdfremediator_github

# Install core dependencies
pip install pikepdf Pillow

# Or install from requirements file
pip install -r requirements.txt
```

### Step 2: Install AI Libraries

Choose which AI provider(s) you want to use:

#### Option A: Anthropic Claude (Recommended)

```bash
pip install anthropic
```

**Why?** Best quality, excellent WCAG understanding, accurate decorative detection
**Cost**: ~$18 per 1000 images

#### Option B: OpenAI GPT-4

```bash
pip install openai
```

**Why?** Great balance of quality and cost, familiar API
**Cost**: ~$12.50 per 1000 images

#### Option C: Google Cloud Vision

```bash
pip install google-cloud-vision
```

**Why?** Lowest cost, best OCR, good for high-volume
**Cost**: ~$1.50 per 1000 images

#### Option D: Azure Computer Vision

```bash
pip install azure-cognitiveservices-vision-computervision msrest
```

**Why?** Good for Microsoft ecosystem integration
**Cost**: ~$1 per 1000 images

#### Option E: Install All (Recommended for Flexibility)

```bash
pip install anthropic openai google-cloud-vision azure-cognitiveservices-vision-computervision msrest
```

---

### Step 3: Get API Keys

#### For Anthropic Claude (Recommended)

1. **Sign up** at https://console.anthropic.com/
2. **Navigate** to Settings → API Keys
3. **Create** a new API key
4. **Copy** the key (starts with `sk-ant-api03-`)

#### For OpenAI GPT-4

1. **Sign up** at https://platform.openai.com/
2. **Navigate** to API Keys section
3. **Create** a new secret key
4. **Copy** the key (starts with `sk-`)

#### For Google Cloud Vision

1. **Create project** at https://console.cloud.google.com/
2. **Enable** Cloud Vision API
3. **Create service account**:
   - Go to IAM & Admin → Service Accounts
   - Create Service Account
   - Grant "Cloud Vision AI" role
   - Create JSON key
4. **Download** the JSON key file

#### For Azure Computer Vision

1. **Create resource** at https://portal.azure.com/
2. **Search** for "Computer Vision"
3. **Create** a new Computer Vision resource
4. **Copy** the Key and Endpoint from the resource

---

### Step 4: Configure API Keys

Choose **one** of these configuration methods:

#### Method A: Environment Variables (Simplest)

Add to your `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`:

```bash
# Anthropic Claude (recommended)
export ANTHROPIC_API_KEY='sk-ant-api03-YOUR_KEY_HERE'

# Or OpenAI GPT-4
export OPENAI_API_KEY='sk-YOUR_KEY_HERE'

# Or Google Cloud Vision
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account.json'

# Or Azure Computer Vision
export AZURE_VISION_KEY='your-azure-key'
export AZURE_VISION_ENDPOINT='https://your-resource.cognitiveservices.azure.com/'
```

Then reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

#### Method B: Configuration File (Recommended for Production)

Create `~/.pdf_remediator/ai_config.json`:

```bash
mkdir -p ~/.pdf_remediator
cat > ~/.pdf_remediator/ai_config.json << 'EOF'
{
  "ai_alt_text": {
    "enabled": true,
    "provider": "claude",
    "fallback_provider": "openai",
    "api_keys": {
      "anthropic": "sk-ant-api03-YOUR_KEY_HERE",
      "openai": "sk-YOUR_KEY_HERE"
    },
    "options": {
      "max_tokens": 300,
      "temperature": 0.3,
      "use_heuristic_first": true,
      "max_alt_text_length": 150
    },
    "cost_limit": {
      "max_cost_per_document": 5.0,
      "warn_threshold": 1.0
    }
  }
}
EOF
```

**Important**: Set proper permissions:
```bash
chmod 600 ~/.pdf_remediator/ai_config.json
```

#### Method C: Per-Project Configuration

Create `ai_config.json` in your project directory:

```json
{
  "ai_alt_text": {
    "enabled": true,
    "provider": "claude",
    "api_keys": {
      "anthropic": "sk-ant-api03-YOUR_KEY_HERE"
    }
  }
}
```

---

### Step 5: Verify Installation

Run the test script to verify everything is configured correctly:

```bash
cd /Users/alejandradashe/pdfremediator_github
python3 test_ai_integration.py
```

**Expected output:**
```
╔====================================================================╗
║               AI ALT-TEXT INTEGRATION TEST SUITE                   ║
╚====================================================================╝

======================================================================
MODULE IMPORT TEST
======================================================================

1. Testing ai_alt_text.py module...
   ✓ ai_alt_text module imports successfully
   ✓ AIAltTextGenerator class available
   ✓ AltTextResult dataclass available
   ✓ AltTextCache class available

2. Checking optional AI library availability...
   ✓ Anthropic Claude: Available
   ✓ OpenAI GPT-4: Available
   ...

✓ All tests completed!
```

---

### Step 6: Test with Demo

Try the interactive demo with a sample PDF:

```bash
python3 examples/ai_alt_text_demo.py /path/to/your/document.pdf
```

This will:
1. Extract all images from the PDF
2. Show you each image
3. Generate AI alt-text for each
4. Display cost per image
5. Provide summary statistics

---

### Step 7: Use with PDF Remediator

Now you can use AI alt-text generation with your PDFs:

```bash
# Basic usage
python3 pdf_remediator.py input.pdf --use-ai-alt-text

# With specific provider
python3 pdf_remediator.py input.pdf --use-ai-alt-text --ai-provider claude

# With all options
python3 pdf_remediator.py input.pdf \
  --use-ai-alt-text \
  --ai-provider claude \
  --title "Annual Report 2024" \
  --author "Finance Team"
```

---

## Verification Checklist

Use this checklist to ensure everything is working:

- [ ] Python 3.7+ installed: `python3 --version`
- [ ] pikepdf installed: `pip show pikepdf`
- [ ] At least one AI library installed: `pip show anthropic`
- [ ] API key set: `echo $ANTHROPIC_API_KEY` (should show your key)
- [ ] Test script passes: `python3 test_ai_integration.py`
- [ ] Demo runs: `python3 examples/ai_alt_text_demo.py sample.pdf`
- [ ] Can remediate with AI: `python3 pdf_remediator.py test.pdf --use-ai-alt-text`

---

## Troubleshooting

### Issue: "Module not found: anthropic"

**Solution:**
```bash
pip install anthropic
# Or
pip3 install anthropic
```

### Issue: "No API keys found"

**Solution:**
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY='sk-ant-api03-YOUR_KEY'

# Or create config file
cat > ~/.pdf_remediator/ai_config.json << EOF
{
  "ai_alt_text": {
    "api_keys": {
      "anthropic": "sk-ant-api03-YOUR_KEY"
    }
  }
}
EOF
```

### Issue: "Permission denied" on config file

**Solution:**
```bash
chmod 600 ~/.pdf_remediator/ai_config.json
```

### Issue: "API rate limit exceeded"

**Solution:**
```bash
# Wait 60 seconds and try again
# Or use a different provider
python3 pdf_remediator.py input.pdf --use-ai-alt-text --ai-provider openai
```

### Issue: "Command not found: python3"

**Solution:**
```bash
# Use python instead
python pdf_remediator.py input.pdf --use-ai-alt-text

# Or install Python 3
# macOS:
brew install python3
# Linux:
sudo apt-get install python3
```

### Issue: Import error on macOS

**Solution:**
```bash
# Accept Xcode license
sudo xcodebuild -license

# Install command line tools
xcode-select --install
```

### Issue: Google Cloud authentication error

**Solution:**
```bash
# Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS='/full/path/to/service-account.json'

# Verify file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS
```

---

## Cost Management

### Set Cost Limits

Add to your config file:

```json
{
  "ai_alt_text": {
    "cost_limit": {
      "max_cost_per_document": 2.0,
      "warn_threshold": 1.0,
      "enabled": true
    }
  }
}
```

### Enable Caching

Caching is enabled by default and saves 100% on repeated runs:

```json
{
  "ai_alt_text": {
    "cache": {
      "enabled": true,
      "directory": "~/.pdf_remediator/alt_text_cache"
    }
  }
}
```

### Clear Cache (if needed)

```bash
rm -rf ~/.pdf_remediator/alt_text_cache
```

---

## Advanced Configuration

### Use Multiple Providers with Fallback

```json
{
  "ai_alt_text": {
    "provider": "claude",
    "fallback_provider": "openai",
    "api_keys": {
      "anthropic": "sk-ant-...",
      "openai": "sk-..."
    }
  }
}
```

### Customize Alt-Text Generation

```json
{
  "ai_alt_text": {
    "options": {
      "max_tokens": 300,
      "temperature": 0.3,
      "use_heuristic_first": true,
      "max_alt_text_length": 150,
      "context_chars": 500
    }
  }
}
```

### Quality Control

```json
{
  "ai_alt_text": {
    "quality": {
      "min_confidence": 0.7,
      "require_manual_review_below": 0.8,
      "validate_wcag": true
    }
  }
}
```

---

## Updating

To update to the latest version:

```bash
cd /Users/alejandradashe/pdfremediator_github

# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade anthropic openai pikepdf

# Re-run tests
python3 test_ai_integration.py
```

---

## Uninstalling

To remove AI features (keep PDF Remediator):

```bash
# Remove AI libraries
pip uninstall anthropic openai google-cloud-vision azure-cognitiveservices-vision-computervision

# Remove config
rm -rf ~/.pdf_remediator/ai_config.json
rm -rf ~/.pdf_remediator/alt_text_cache

# Remove API key from shell config
# Edit ~/.bashrc or ~/.zshrc and remove ANTHROPIC_API_KEY line
```

To remove everything:

```bash
# Remove entire PDF Remediator
rm -rf /Users/alejandradashe/pdfremediator_github

# Remove config directory
rm -rf ~/.pdf_remediator
```

---

## Security Best Practices

### 1. Protect API Keys

```bash
# Never commit API keys to git
echo "ai_config.json" >> .gitignore
echo ".env" >> .gitignore

# Set restrictive permissions
chmod 600 ~/.pdf_remediator/ai_config.json
```

### 2. Use Environment Variables in CI/CD

For GitHub Actions, Travis, etc:

```yaml
# .github/workflows/test.yml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 3. Rotate Keys Regularly

- Change API keys every 90 days
- Revoke unused keys immediately
- Use separate keys for dev/prod

---

## Performance Optimization

### Batch Processing

Process multiple PDFs efficiently:

```python
from ai_alt_text import AIAltTextGenerator

# Initialize once, reuse for all documents
ai_generator = AIAltTextGenerator(config)

for pdf in pdfs:
    remediator = EnhancedPDFRemediator(pdf)
    remediator.ai_generator = ai_generator  # Reuse
    remediator.remediate()
```

### Parallel Processing

For large batches:

```bash
# Process multiple PDFs in parallel
find ./pdfs -name "*.pdf" -print0 | \
  xargs -0 -P 4 -I {} \
  python3 pdf_remediator.py {} --use-ai-alt-text
```

---

## Getting Help

1. **Check documentation**: See [AI_ALT_TEXT_GUIDE.md](docs/AI_ALT_TEXT_GUIDE.md)
2. **Run tests**: `python3 test_ai_integration.py`
3. **Check logs**: Look for error messages in output
4. **Try demo**: `python3 examples/ai_alt_text_demo.py sample.pdf`
5. **Create issue**: Report problems on GitHub

---

## Next Steps

After installation:

1. **Read the guide**: [AI_QUICK_START.md](AI_QUICK_START.md)
2. **Try the demo**: `python3 examples/ai_alt_text_demo.py sample.pdf`
3. **Test on real PDF**: Start with a small document
4. **Review results**: Check AI-generated alt-text quality
5. **Integrate into workflow**: Add to your PDF processing pipeline

---

## Support

- **Quick Start**: [AI_QUICK_START.md](AI_QUICK_START.md)
- **Full Guide**: [docs/AI_ALT_TEXT_GUIDE.md](docs/AI_ALT_TEXT_GUIDE.md)
- **API Comparison**: [docs/AI_VISION_API_COMPARISON.md](docs/AI_VISION_API_COMPARISON.md)
- **GitHub Issues**: https://github.com/adasheasu/pdfremediator/issues

---

**Installation Complete!** 🎉

You're now ready to use AI-powered alt-text generation for PDF accessibility remediation.

Start with: `python3 pdf_remediator.py your_document.pdf --use-ai-alt-text`

---

*Last Updated: 2025-10-25*
