# AI Alt-Text Generation - Quick Start

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install anthropic pikepdf Pillow
```

### Step 2: Set API Key

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-YOUR-KEY-HERE'
```

Get your key at: https://console.anthropic.com/settings/keys

### Step 3: Test with Demo

```bash
# Test on a sample PDF
python examples/ai_alt_text_demo.py your_document.pdf
```

### Step 4: Use with PDF Remediator

```bash
# Remediate with AI alt-text
python pdf_remediator.py input.pdf --use-ai-alt-text
```

That's it! 🎉

---

## 📊 What You'll See

```
Loading PDF: input.pdf
Analyzing PDF (10 pages)...
Found 15 images

🤖 AI alt-text generation enabled
  ✓ Using provider: claude

Tagging images...
  ✓ Image 1 (Page 1): Decorative border element
  ✓ Image 2 (Page 1): "Bar chart showing 25% revenue growth in Q3 2024"
  ✓ Image 3 (Page 2): "Company logo with tagline 'Innovation Starts Here'"
  ... (12 more images)

AI Alt-Text Summary:
  Images processed: 15
  Decorative: 4
  Descriptive: 11
  Total cost: $0.27
  Average: $0.018/image

Saving remediated PDF: input_remediated.pdf
✓ PDF saved successfully

Done!
```

---

## 📚 Full Documentation

- **Complete Guide**: [docs/AI_ALT_TEXT_GUIDE.md](docs/AI_ALT_TEXT_GUIDE.md)
- **API Comparison**: [docs/AI_VISION_API_COMPARISON.md](docs/AI_VISION_API_COMPARISON.md)
- **Integration Details**: [pdf_remediator_ai_integration.py](pdf_remediator_ai_integration.py)

---

## 🔑 API Key Setup

### Anthropic Claude (Recommended)
```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```
**Cost**: ~$18 per 1000 images | **Quality**: Excellent

### OpenAI GPT-4
```bash
export OPENAI_API_KEY='sk-...'
```
**Cost**: ~$12.50 per 1000 images | **Quality**: Very Good

### Google Cloud Vision
```bash
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account.json'
```
**Cost**: ~$1.50 per 1000 images | **Quality**: Good

---

## 🎯 Key Features

✅ **Automatic decorative vs. descriptive detection**
- AI analyzes image content and context
- More accurate than size-based heuristics

✅ **Context-aware descriptions**
- Uses surrounding page text
- Understands document purpose
- WCAG 2.2 AA compliant

✅ **Cost optimization**
- Caching prevents reprocessing
- Heuristic pre-filtering
- Typical cost: $0.15-0.50 per document

✅ **Multiple providers**
- Anthropic Claude (best quality)
- OpenAI GPT-4 (great balance)
- Google Vision (high volume)
- Azure Vision (Microsoft ecosystem)

---

## 💡 Examples

### Financial Report
```bash
python pdf_remediator.py quarterly_report.pdf --use-ai-alt-text
```
**AI generates**:
- "Line graph showing quarterly revenue growth from Q1 2023 to Q3 2024"
- "Pie chart depicting market share: North America 45%, Europe 30%, Asia 25%"

### Academic Paper
```bash
python pdf_remediator.py research.pdf --use-ai-alt-text
```
**AI generates**:
- "Neural network architecture diagram with 5 convolutional layers"
- "Scatter plot comparing model accuracy vs training time"

### User Manual
```bash
python pdf_remediator.py manual.pdf --use-ai-alt-text
```
**AI generates**:
- "Screenshot of settings menu with WiFi options highlighted"
- "Step-by-step installation diagram with numbered arrows"

---

## ⚙️ Configuration (Optional)

Create `~/.pdf_remediator/ai_config.json`:

```json
{
  "ai_alt_text": {
    "enabled": true,
    "provider": "claude",
    "api_keys": {
      "anthropic": "sk-ant-api03-..."
    },
    "cost_limit": {
      "max_cost_per_document": 2.0
    }
  }
}
```

---

## 🐛 Troubleshooting

### "No API keys found"
```bash
# Make sure to export the key
export ANTHROPIC_API_KEY='your-key'

# Verify it's set
echo $ANTHROPIC_API_KEY
```

### "Module not found: anthropic"
```bash
pip install anthropic
```

### "Rate limit exceeded"
Wait 60 seconds and try again, or use a different provider.

### Cost too high?
```bash
# Use Google Vision for volume
pip install google-cloud-vision
export GOOGLE_APPLICATION_CREDENTIALS='service-account.json'
python pdf_remediator.py input.pdf --use-ai-alt-text --ai-provider google
```

---

## 📞 Get Help

- 📖 **Full Guide**: [docs/AI_ALT_TEXT_GUIDE.md](docs/AI_ALT_TEXT_GUIDE.md)
- 🧪 **Try Demo**: `python examples/ai_alt_text_demo.py your.pdf`
- 🐛 **Report Issues**: GitHub Issues
- 💬 **Questions**: Check documentation or create an issue

---

## 🎓 Learn More

### Cost Examples

| Document Type | Images | Cost |
|---------------|--------|------|
| Small report (10 pages) | 15 | $0.27 |
| Medium document (20 pages) | 25 | $0.45 |
| Large manual (50 pages) | 60 | $1.08 |

### Quality Comparison

| Provider | Quality | Cost | Speed |
|----------|---------|------|-------|
| Claude | ⭐⭐⭐⭐⭐ | $18/1k | Fast |
| OpenAI | ⭐⭐⭐⭐ | $12/1k | Fast |
| Google | ⭐⭐⭐ | $1.50/1k | Very Fast |
| Azure | ⭐⭐⭐ | $1/1k | Fast |

---

**Ready to get started?**

```bash
# Install
pip install anthropic pikepdf Pillow

# Set key
export ANTHROPIC_API_KEY='your-key'

# Run demo
python examples/ai_alt_text_demo.py test.pdf

# Use it
python pdf_remediator.py input.pdf --use-ai-alt-text
```

🚀 **That's it! Happy remediating!**
