# AI Alt-Text Generation Guide

## Overview

This guide explains how to use AI-powered alt-text generation with PDF Remediator to automatically create high-quality, context-aware alternative text descriptions for images in PDF documents.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Cost Management](#cost-management)
7. [Best Practices](#best-practices)
8. [API Provider Comparison](#api-provider-comparison)
9. [Troubleshooting](#troubleshooting)
10. [Integration with Streamlit Tool](#integration-with-streamlit-tool)

---

## Features

### What AI Alt-Text Generation Provides

✅ **Automatic Decorative Detection**
- AI analyzes images to determine if they're decorative (borders, lines, backgrounds)
- More accurate than size-based heuristics alone
- Considers document context and image content

✅ **Context-Aware Descriptions**
- Uses surrounding page text to understand image purpose
- Generates descriptions that fit the document's narrative
- Follows WCAG 2.2 AA guidelines automatically

✅ **Multi-Provider Support**
- Anthropic Claude 3.5 Sonnet (recommended)
- OpenAI GPT-4o with Vision
- Google Cloud Vision AI
- Azure Computer Vision
- Automatic fallback if primary fails

✅ **Cost Optimization**
- Caching prevents re-processing same images
- Heuristic pre-filtering reduces API calls
- Cost tracking and limits
- Batch processing support

✅ **Quality Assurance**
- Confidence scores for each result
- Reasoning explanations for classifications
- Validation against WCAG criteria
- Manual review warnings for low confidence

---

## Installation

### 1. Install Core Library

```bash
# Already installed with pdf_remediator.py
pip install pikepdf
```

### 2. Install AI Libraries

Choose based on which provider you want to use:

#### For Anthropic Claude (Recommended)
```bash
pip install anthropic
```

#### For OpenAI GPT-4
```bash
pip install openai
```

#### For Google Cloud Vision
```bash
pip install google-cloud-vision
```

#### For Azure Computer Vision
```bash
pip install azure-cognitiveservices-vision-computervision msrest
```

#### Install All (Recommended)
```bash
pip install anthropic openai google-cloud-vision azure-cognitiveservices-vision-computervision msrest
```

### 3. Get API Keys

#### Anthropic Claude
1. Sign up at https://console.anthropic.com/
2. Generate API key
3. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY='sk-ant-api03-...'
   ```

#### OpenAI
1. Sign up at https://platform.openai.com/
2. Generate API key
3. Set environment variable:
   ```bash
   export OPENAI_API_KEY='sk-...'
   ```

#### Google Cloud Vision
1. Create project at https://console.cloud.google.com/
2. Enable Vision API
3. Create service account and download JSON key
4. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account.json'
   ```

#### Azure Computer Vision
1. Create resource at https://portal.azure.com/
2. Get endpoint and key
3. Set environment variables:
   ```bash
   export AZURE_VISION_KEY='your-key'
   export AZURE_VISION_ENDPOINT='https://your-resource.cognitiveservices.azure.com/'
   ```

---

## Quick Start

### Method 1: Command Line (Recommended)

```bash
# Basic usage with AI alt-text
python pdf_remediator.py input.pdf --use-ai-alt-text

# Specify provider
python pdf_remediator.py input.pdf --use-ai-alt-text --ai-provider claude

# With all options
python pdf_remediator.py input.pdf \
  --use-ai-alt-text \
  --ai-provider claude \
  --title "Annual Report 2024" \
  --author "Finance Team"
```

### Method 2: Configuration File

Create `~/.pdf_remediator/ai_config.json`:

```json
{
  "ai_alt_text": {
    "enabled": true,
    "provider": "claude",
    "fallback_provider": "openai",
    "api_keys": {
      "anthropic": "sk-ant-api03-...",
      "openai": "sk-..."
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
```

Then run:

```bash
python pdf_remediator.py input.pdf
```

### Method 3: Python API

```python
from pdf_remediator import EnhancedPDFRemediator
from ai_alt_text import AIAltTextGenerator

# Initialize with AI
remediator = EnhancedPDFRemediator("input.pdf", "output.pdf")

# Configure AI
ai_config = {
    'provider': 'claude',
    'api_keys': {
        'anthropic': 'sk-ant-...'
    }
}

remediator.ai_generator = AIAltTextGenerator(ai_config)

# Remediate
remediator.load_pdf()
remediator.analyze()
remediator.remediate()
remediator.save()

# Get cost summary
cost = remediator.ai_generator.get_cost_summary()
print(f"Total cost: ${cost['total_cost']:.2f}")
```

---

## Configuration

### Complete Configuration Reference

```json
{
  "ai_alt_text": {
    "enabled": true,
    "provider": "claude",
    "fallback_provider": "openai",

    "api_keys": {
      "anthropic": "sk-ant-api03-...",
      "openai": "sk-...",
      "google": "/path/to/service-account.json",
      "azure": {
        "key": "your-key",
        "endpoint": "https://your-resource.cognitiveservices.azure.com/"
      }
    },

    "options": {
      "max_tokens": 300,
      "temperature": 0.3,
      "use_heuristic_first": true,
      "batch_size": 10,
      "max_alt_text_length": 150,
      "context_chars": 500
    },

    "cost_limit": {
      "max_cost_per_document": 5.0,
      "warn_threshold": 1.0,
      "enabled": true
    },

    "cache": {
      "enabled": true,
      "directory": "~/.pdf_remediator/alt_text_cache",
      "ttl_days": 30
    },

    "quality": {
      "min_confidence": 0.7,
      "require_manual_review_below": 0.8,
      "validate_wcag": true
    }
  }
}
```

### Configuration Options Explained

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | false | Enable AI alt-text generation |
| `provider` | string | "claude" | Primary AI provider |
| `fallback_provider` | string | "openai" | Backup if primary fails |
| `max_tokens` | int | 300 | Max tokens for AI response |
| `temperature` | float | 0.3 | AI creativity (0-1, lower = more consistent) |
| `use_heuristic_first` | bool | true | Check size/ratio before AI |
| `batch_size` | int | 10 | Images to process in batch |
| `max_alt_text_length` | int | 150 | Max alt-text characters |
| `context_chars` | int | 500 | Characters of page context |
| `max_cost_per_document` | float | 5.0 | Stop if cost exceeds |
| `warn_threshold` | float | 1.0 | Warn when cost exceeds |
| `min_confidence` | float | 0.7 | Minimum acceptable confidence |

---

## Usage Examples

### Example 1: Basic Document with Images

```bash
# Input: report.pdf with 10 images
python pdf_remediator.py report.pdf --use-ai-alt-text

# Output:
# Analyzing PDF (5 pages)...
# Found 10 images
# 🤖 AI alt-text generation enabled
# Tagging images...
#   ✓ Image 1: Decorative (border element)
#   ✓ Image 2: "Bar chart showing 25% revenue growth Q3 2024"
#   ✓ Image 3: "Company headquarters building in downtown Seattle"
#   ... (7 more)
#
# AI Alt-Text Summary:
#   Images processed: 10
#   Decorative: 3
#   Descriptive: 7
#   Total cost: $0.15
#   Average: $0.015/image
#
# Saved: report_remediated.pdf
```

### Example 2: Financial Report with Charts

```bash
python pdf_remediator.py quarterly_report.pdf \
  --use-ai-alt-text \
  --ai-provider claude \
  --title "Q3 2024 Financial Report" \
  --author "Finance Department"

# AI will generate descriptions like:
# - "Line graph showing revenue trend from Q1 2023 to Q3 2024, indicating 15% year-over-year growth"
# - "Pie chart depicting market share distribution: North America 45%, Europe 30%, Asia 25%"
# - "Table showing quarterly earnings per share: Q1: $1.23, Q2: $1.45, Q3: $1.67"
```

### Example 3: Academic Paper with Diagrams

```bash
python pdf_remediator.py research_paper.pdf \
  --use-ai-alt-text \
  --ai-provider claude \
  --subject "Machine Learning Research"

# AI understands academic context:
# - "Architectural diagram of convolutional neural network with 5 layers"
# - "Scatter plot showing correlation between model accuracy and training time"
# - "Flowchart illustrating the data preprocessing pipeline"
```

### Example 4: Batch Processing Multiple PDFs

```python
import os
from pathlib import Path
from pdf_remediator import EnhancedPDFRemediator
from ai_alt_text import AIAltTextGenerator

# Initialize AI generator once
ai_config = {
    'provider': 'claude',
    'api_keys': {'anthropic': os.getenv('ANTHROPIC_API_KEY')}
}
ai_generator = AIAltTextGenerator(ai_config)

# Process all PDFs in directory
pdf_dir = Path("./documents")
output_dir = Path("./remediated")
output_dir.mkdir(exist_ok=True)

total_cost = 0.0

for pdf_file in pdf_dir.glob("*.pdf"):
    print(f"\nProcessing: {pdf_file.name}")

    output_file = output_dir / f"{pdf_file.stem}_remediated.pdf"

    remediator = EnhancedPDFRemediator(str(pdf_file), str(output_file))
    remediator.ai_generator = ai_generator  # Reuse generator

    remediator.load_pdf()
    remediator.analyze()
    remediator.remediate()
    remediator.save()

    # Track costs
    cost = ai_generator.get_cost_summary()
    doc_cost = cost['by_document'].get(str(pdf_file), 0.0)
    total_cost += doc_cost
    print(f"  Cost: ${doc_cost:.2f}")

print(f"\nTotal cost for all documents: ${total_cost:.2f}")
```

### Example 5: Testing with Demo Script

```bash
# Run the demo to see AI in action
python examples/ai_alt_text_demo.py sample.pdf

# Interactive demo that:
# 1. Extracts each image
# 2. Shows heuristic detection
# 3. Prompts for page context
# 4. Generates AI alt-text
# 5. Shows cost per image
# 6. Provides summary
```

---

## Cost Management

### Typical Costs

| Document Type | Images | Provider | Cost |
|---------------|--------|----------|------|
| Business Report (10 pages) | 15 images | Claude | $0.27 |
| Academic Paper (20 pages) | 25 images | Claude | $0.45 |
| Annual Report (50 pages) | 60 images | Claude | $1.08 |
| Technical Manual (100 pages) | 120 images | Claude | $2.16 |

### Cost Optimization Strategies

#### 1. Use Heuristic Pre-filtering
```json
{
  "options": {
    "use_heuristic_first": true
  }
}
```
- Checks image size/ratio first (free)
- Only sends complex images to AI
- **Saves 30-50% on average**

#### 2. Enable Caching
```json
{
  "cache": {
    "enabled": true
  }
}
```
- Caches results by image content + context
- Reprocessing same document is FREE
- **Saves 100% on repeated runs**

#### 3. Choose Cost-Effective Provider

For high-volume:
```json
{
  "provider": "google"  // $1.50/1000 images
}
```

For quality:
```json
{
  "provider": "claude"  // $18/1000 images but best results
}
```

#### 4. Set Cost Limits
```json
{
  "cost_limit": {
    "max_cost_per_document": 2.0,
    "warn_threshold": 1.0
  }
}
```

#### 5. Batch Processing
```python
# Process multiple PDFs with same AI instance
# Shares cache and cost tracking
ai_generator = AIAltTextGenerator(config)

for pdf in pdfs:
    remediator = EnhancedPDFRemediator(pdf)
    remediator.ai_generator = ai_generator  # Reuse
    remediator.remediate()
```

### Cost Tracking

```python
# Get detailed cost breakdown
cost_summary = ai_generator.get_cost_summary()

print(f"Total API calls: {cost_summary['images_processed']}")
print(f"Total cost: ${cost_summary['total_cost']:.4f}")
print(f"Average per image: ${cost_summary['total_cost']/cost_summary['images_processed']:.4f}")

# By provider
for provider, cost in cost_summary['by_provider'].items():
    print(f"  {provider}: ${cost:.4f}")

# By document
for doc, cost in cost_summary['by_document'].items():
    print(f"  {doc}: ${cost:.4f}")
```

---

## Best Practices

### 1. Start with a Test Document

```bash
# Test on small document first
python examples/ai_alt_text_demo.py small_test.pdf

# Review results before full deployment
```

### 2. Use Appropriate Provider

- **Claude**: Best for complex documents (reports, research papers)
- **OpenAI**: Good balance for business documents
- **Google**: Best for high-volume, text-heavy images
- **Azure**: Good for Microsoft ecosystem

### 3. Provide Good Context

```python
# Extract meaningful context, not just page numbers
context = extract_surrounding_text(page, image_position)

# Include:
# - Surrounding paragraphs
# - Section headings
# - Captions if present
# - Document type/purpose
```

### 4. Review Low-Confidence Results

```python
result = ai_generator.generate_alt_text(image_bytes, context)

if result.confidence < 0.8:
    print(f"⚠️ Low confidence ({result.confidence:.0%}): Manual review recommended")
    print(f"  AI suggestion: {result.alt_text}")
    print(f"  Reasoning: {result.reasoning}")
```

### 5. Validate WCAG Compliance

```python
# Check alt-text quality
from pdf_remediator import EnhancedPDFRemediator

remediator = EnhancedPDFRemediator("input.pdf")
remediator._validate_alt_text_for_content(result.alt_text)

# Checks for:
# - Not just generic "image of"
# - Minimum length
# - Actual content description
# - Not hiding annotations
```

### 6. Handle Errors Gracefully

```python
try:
    result = ai_generator.generate_alt_text(image_bytes, context)
except Exception as e:
    # Fallback to heuristic
    print(f"AI failed: {e}, using heuristic")
    result = generate_heuristic_alt_text(image_info)
```

### 7. Monitor Costs

```bash
# Set up cost alerts
export AI_COST_ALERT_EMAIL="admin@company.com"

# Enable in config
{
  "cost_limit": {
    "warn_threshold": 1.0,
    "max_cost_per_document": 5.0,
    "alert_email": "admin@company.com"
  }
}
```

---

## API Provider Comparison

See [AI_VISION_API_COMPARISON.md](AI_VISION_API_COMPARISON.md) for detailed comparison.

### Quick Comparison

| Feature | Claude | OpenAI | Google | Azure |
|---------|--------|--------|--------|-------|
| **Best For** | Quality | Balance | Volume | Microsoft |
| **Cost/1000** | $18 | $12.50 | $1.50 | $1.00 |
| **Context Awareness** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Decorative Detection** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Setup Complexity** | Low | Low | Medium | Medium |
| **WCAG Understanding** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## Troubleshooting

### Issue: "No API keys found"

**Solution:**
```bash
# Set environment variable
export ANTHROPIC_API_KEY='sk-ant-api03-...'

# Or create config file
mkdir -p ~/.pdf_remediator
cat > ~/.pdf_remediator/ai_config.json << EOF
{
  "ai_alt_text": {
    "api_keys": {
      "anthropic": "sk-ant-api03-..."
    }
  }
}
EOF
```

### Issue: "AI alt-text generation failed"

**Check:**
1. API key is valid
2. Provider library is installed (`pip install anthropic`)
3. Internet connection is working
4. API has not exceeded rate limits

### Issue: "Costs too high"

**Solutions:**
```json
{
  "options": {
    "use_heuristic_first": true,  // Enable pre-filtering
    "provider": "google"           // Use cheaper provider
  },
  "cache": {
    "enabled": true                // Enable caching
  },
  "cost_limit": {
    "max_cost_per_document": 1.0  // Set limit
  }
}
```

### Issue: "Alt-text quality is poor"

**Try:**
1. Switch to Claude (best quality)
2. Provide better page context
3. Use lower temperature (more consistent)
4. Review reasoning field to understand AI logic

```python
result = ai_generator.generate_alt_text(image, context)
print(f"Reasoning: {result.reasoning}")
```

### Issue: "Images marked decorative incorrectly"

**Solutions:**
1. Disable heuristic pre-filtering:
   ```json
   {"options": {"use_heuristic_first": false}}
   ```

2. Review AI reasoning:
   ```python
   if result.is_decorative:
       print(f"Why decorative: {result.reasoning}")
   ```

3. Manually override:
   ```python
   if result.is_decorative and manual_check_says_descriptive:
       result.is_decorative = False
       result.alt_text = "Manual description here"
   ```

---

## Integration with Streamlit Tool

The Streamlit Image Accessibility tool at https://asuo-ai-labs.streamlit.app/Image_Accessibility can be used in conjunction with this PDF Remediator AI feature.

### Workflow:

1. **Extract images** using PDF Remediator:
   ```python
   images = remediator.analyze_images()
   for img in images:
       save_image(img, f"image_{img.page_number}.png")
   ```

2. **Upload to Streamlit tool** for manual review

3. **Compare results**:
   - AI-generated alt-text from PDF Remediator
   - Human-curated alt-text from Streamlit tool
   - Use best of both

4. **Apply to PDF**:
   ```python
   # Override with Streamlit results if better
   img_info.alt_text = streamlit_result['alt_text']
   remediator.tag_images()
   ```

### API Integration (if available)

If the Streamlit tool provides an API:

```python
def use_streamlit_api(image_bytes, context):
    """Call Streamlit Image Accessibility API."""
    import requests

    response = requests.post(
        'https://asuo-ai-labs.streamlit.app/api/analyze',
        files={'image': image_bytes},
        data={'context': context}
    )

    return response.json()

# Use in generator
class StreamlitProvider:
    def generate_alt_text(self, image_bytes, context):
        result = use_streamlit_api(image_bytes, context)
        return AltTextResult(
            is_decorative=result['is_decorative'],
            alt_text=result['alt_text'],
            provider='streamlit'
        )
```

---

## Next Steps

1. **Try the demo**: `python examples/ai_alt_text_demo.py your.pdf`
2. **Configure API keys**: Set up your preferred provider
3. **Test on sample document**: Start small to evaluate quality
4. **Integrate into workflow**: Add to your PDF processing pipeline
5. **Monitor costs**: Track usage and optimize as needed

## Support

- **Documentation**: See `/docs` directory
- **Examples**: See `/examples` directory
- **Issues**: Report at GitHub repository
- **API Docs**: See provider documentation (Anthropic, OpenAI, etc.)

---

**Last Updated**: 2024-10-25
