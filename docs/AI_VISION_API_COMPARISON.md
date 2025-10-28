# AI Vision API Comparison for Alt-Text Generation

## Overview
This document compares different AI vision APIs suitable for generating alt-text descriptions for PDF images in the context of accessibility remediation.

---

## API Comparison Table

| Feature | OpenAI GPT-4 Vision | Anthropic Claude 3.5 Sonnet | Google Cloud Vision | Azure Computer Vision | AWS Rekognition |
|---------|---------------------|------------------------------|---------------------|----------------------|-----------------|
| **Context Awareness** | ✓✓✓ Excellent | ✓✓✓ Excellent | ✓ Basic | ✓✓ Good | ✓ Basic |
| **Decorative Detection** | ✓✓ Good with prompting | ✓✓✓ Excellent with prompting | ○ Manual | ✓ Good | ○ Manual |
| **Alt-Text Quality** | ✓✓✓ Natural, descriptive | ✓✓✓ Natural, detailed | ✓✓ Technical | ✓✓ Good | ✓ Basic labels |
| **Document Context** | ✓✓✓ Can analyze surrounding text | ✓✓✓ Excellent at document analysis | ○ Image only | ✓ Limited | ○ Image only |
| **Pricing** | $0.01/image (approx) | $0.024/image (approx) | $1.50/1000 | $1.00/1000 | $1.00/1000 |
| **Rate Limits** | 500 RPM (Tier 2) | 400 RPM | 1800 RPM | Varies | Varies |
| **Setup Complexity** | Low (API key) | Low (API key) | Medium (GCP project) | Medium (Azure account) | Medium (AWS account) |
| **Batch Processing** | ✓ Async available | ✓ Async available | ✓✓ Native batch | ✓ Batch support | ✓ Batch support |
| **OCR Capability** | ✓✓ Good | ✓✓✓ Excellent | ✓✓✓ Best-in-class | ✓✓ Good | ✓ Basic |
| **WCAG Compliance** | ✓✓ With proper prompting | ✓✓✓ Excellent understanding | ✓ Needs guidance | ✓✓ Good | ✓ Basic |

---

## Detailed API Analysis

### 1. OpenAI GPT-4 Vision (gpt-4-vision-preview / gpt-4o)

**Strengths:**
- Excellent at understanding context and generating natural language descriptions
- Can analyze both image and surrounding text together
- Good at identifying decorative vs. informational images with proper prompting
- Simple API, easy integration
- Supports base64 encoded images and URLs

**Weaknesses:**
- More expensive than specialized vision APIs
- Rate limits can be restrictive for large batch jobs
- Requires careful prompt engineering for consistent results

**Best Use Case:**
- PDFs with complex images requiring contextual understanding
- Documents where image relationship to text is important
- When natural, human-like descriptions are needed

**API Example:**
```python
import openai
import base64

def generate_alt_text_openai(image_bytes, page_context):
    """Generate alt text using OpenAI GPT-4 Vision."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    response = openai.chat.completions.create(
        model="gpt-4o",  # or gpt-4-vision-preview
        messages=[
            {
                "role": "system",
                "content": """You are an accessibility expert generating alt-text for PDF images.

Rules:
1. If image is decorative (borders, lines, backgrounds), respond with: {"is_decorative": true}
2. If image contains meaningful content, provide concise, descriptive alt-text
3. Focus on what the image depicts, not just identifying it as "chart" or "diagram"
4. Use surrounding text context to understand image purpose
5. Keep alt-text under 150 characters when possible"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Context from page: {page_context}\n\nGenerate appropriate alt-text for this image:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content
```

**Pricing:**
- Input: ~$0.0025 per image (assuming ~1000 tokens)
- Output: ~$0.01 per image (assuming ~100 tokens)
- **Total: ~$0.0125 per image** (for standard quality images)

---

### 2. Anthropic Claude 3.5 Sonnet (Recommended ✓)

**Strengths:**
- **Best contextual understanding** of document structure
- Excellent at reasoning about whether images are decorative
- Very detailed, accurate descriptions
- Strong understanding of accessibility requirements
- Can analyze long context (200K tokens)
- Excellent at following complex instructions

**Weaknesses:**
- Slightly more expensive than OpenAI
- Requires Messages API (slightly different format)
- Need to encode images as base64

**Best Use Case:**
- **RECOMMENDED FOR PDF REMEDIATION**
- Complex documents with many interrelated images
- When decorative vs. descriptive determination is critical
- Professional accessibility compliance required

**API Example:**
```python
import anthropic
import base64

def generate_alt_text_claude(image_bytes, page_context):
    """Generate alt text using Anthropic Claude."""
    client = anthropic.Anthropic(api_key="your-api-key")

    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Determine image type (png, jpeg, etc.)
    import imghdr
    image_type = imghdr.what(None, h=image_bytes) or 'jpeg'

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        system="""You are an accessibility expert generating alt-text for PDF images following WCAG 2.2 guidelines.

CRITICAL RULES:
1. Decorative images (borders, lines, spacers, backgrounds, purely aesthetic) must return: {"is_decorative": true, "alt_text": ""}
2. Informational images require concise, descriptive alt-text that conveys the content
3. Focus on WHAT the image shows, not just identifying the type
4. Use page context to understand image purpose
5. Keep alt-text clear and under 150 characters when possible

Respond in JSON format:
{"is_decorative": false, "alt_text": "description here", "reasoning": "why this classification"}""",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Page context: {page_context}\n\nAnalyze this image and provide appropriate alt-text:"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": f"image/{image_type}",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    )

    return message.content[0].text
```

**Pricing:**
- Input: ~$0.003 per image (assuming ~1000 tokens)
- Output: ~$0.015 per image (assuming ~100 tokens)
- **Total: ~$0.018 per image**

---

### 3. Google Cloud Vision AI

**Strengths:**
- **Best OCR capabilities** for text-in-images
- Very fast processing
- Good batch processing support
- Most cost-effective for high volume
- Excellent label detection

**Weaknesses:**
- Not designed for natural language descriptions
- Cannot analyze document context
- Requires manual interpretation of labels
- More complex setup (GCP project, service account)

**Best Use Case:**
- High-volume processing (thousands of images)
- Images with embedded text requiring OCR
- When cost is primary concern
- Batch processing workflows

**API Example:**
```python
from google.cloud import vision

def generate_alt_text_gcp(image_bytes, page_context):
    """Generate alt text using Google Cloud Vision."""
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_bytes)

    # Multiple detection types
    response = client.annotate_image({
        'image': image,
        'features': [
            {'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': 10},
            {'type_': vision.Feature.Type.TEXT_DETECTION},
            {'type_': vision.Feature.Type.OBJECT_LOCALIZATION},
            {'type_': vision.Feature.Type.IMAGE_PROPERTIES}
        ]
    })

    # Build description from labels
    labels = [label.description for label in response.label_annotations[:5]]
    text = response.text_annotations[0].description if response.text_annotations else ""

    # Heuristic: if very few objects and low confidence, likely decorative
    objects = response.localized_object_annotations

    if len(objects) == 0 and len(labels) < 3:
        return {"is_decorative": True, "alt_text": ""}

    # Build alt text from labels and text
    if text:
        alt_text = f"Image containing text: {text[:100]}"
    else:
        alt_text = f"Image showing {', '.join(labels[:3])}"

    return {"is_decorative": False, "alt_text": alt_text}
```

**Pricing:**
- **$1.50 per 1000 images** (first 1000/month free)
- Very cost-effective at scale

---

### 4. Azure Computer Vision (Image Analysis 4.0)

**Strengths:**
- Good balance of features and cost
- Built-in "dense captions" feature
- Microsoft ecosystem integration
- Good documentation

**Weaknesses:**
- Captions can be generic
- Limited contextual understanding
- Requires Azure subscription setup

**Best Use Case:**
- Organizations already using Azure
- Standard business documents
- Moderate volume processing

**API Example:**
```python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

def generate_alt_text_azure(image_bytes, page_context):
    """Generate alt text using Azure Computer Vision."""
    client = ComputerVisionClient(
        endpoint="your-endpoint",
        credentials=CognitiveServicesCredentials("your-key")
    )

    # Analyze image
    analysis = client.analyze_image_in_stream(
        image_bytes,
        visual_features=['Description', 'Tags', 'Objects', 'ImageType']
    )

    # Check if likely decorative
    if analysis.image_type.clip_art_type > 2 or analysis.image_type.line_drawing_type > 2:
        # Might be decorative
        if len(analysis.objects) == 0:
            return {"is_decorative": True, "alt_text": ""}

    # Use caption
    if analysis.description.captions:
        alt_text = analysis.description.captions[0].text
    else:
        # Fallback to tags
        tags = [tag.name for tag in analysis.tags[:3]]
        alt_text = f"Image showing {', '.join(tags)}"

    return {"is_decorative": False, "alt_text": alt_text}
```

**Pricing:**
- **$1.00 per 1000 images**
- Free tier: 5000 images/month

---

## Recommendation Summary

### Best Overall: **Anthropic Claude 3.5 Sonnet**

**Why:**
1. ✓ Excellent at understanding document context
2. ✓ Best at determining decorative vs. descriptive
3. ✓ Generates WCAG-compliant alt-text
4. ✓ Can reason about image purpose in document
5. ✓ Natural, professional descriptions
6. ✓ Simple API integration

**Cost:** ~$18 per 1000 images (reasonable for quality)

### Best for Budget: **Google Cloud Vision**

**Why:**
1. ✓ Only $1.50 per 1000 images
2. ✓ Excellent OCR for text-in-images
3. ✓ Fast batch processing

**Tradeoff:** Requires more post-processing to generate natural alt-text

### Best for OpenAI Users: **GPT-4o (with vision)**

**Why:**
1. ✓ Good balance of quality and cost
2. ✓ Familiar API for OpenAI users
3. ✓ Good contextual understanding

**Cost:** ~$12.50 per 1000 images

---

## Implementation Strategy

### Hybrid Approach (Recommended)

Use **multiple APIs** based on image characteristics:

```python
def choose_api_strategy(img_info, page_context):
    """Choose best API based on image characteristics."""

    # 1. Heuristic decorative detection first (free)
    if img_info.determine_if_decorative():
        return "heuristic", {"is_decorative": True}

    # 2. For text-heavy images, use Google Cloud Vision (cheap OCR)
    if likely_contains_text(img_info):
        return "google_vision", None

    # 3. For complex images, use Claude 3.5 (best quality)
    if needs_contextual_analysis(img_info, page_context):
        return "claude", None

    # 4. Default to GPT-4o (good balance)
    return "openai", None
```

This approach:
- Reduces costs by using heuristics first
- Uses specialized APIs for specific tasks
- Falls back to premium API for complex cases

---

## Configuration

Recommended config file structure:

```json
{
  "ai_alt_text": {
    "enabled": false,
    "provider": "claude",
    "fallback_provider": "openai",
    "api_keys": {
      "openai": "sk-...",
      "anthropic": "sk-ant-...",
      "google": "path/to/service-account.json",
      "azure": {
        "key": "...",
        "endpoint": "..."
      }
    },
    "options": {
      "max_tokens": 300,
      "temperature": 0.3,
      "use_heuristic_first": true,
      "batch_size": 10,
      "max_alt_text_length": 150
    },
    "cost_limit": {
      "max_cost_per_document": 5.00,
      "warn_threshold": 1.00
    }
  }
}
```

---

## Next Steps

1. Implement Claude 3.5 Sonnet integration (recommended)
2. Add OpenAI GPT-4o as fallback
3. Create configuration system for API keys
4. Add cost tracking and limits
5. Implement caching to avoid re-processing images
6. Add batch processing for efficiency

