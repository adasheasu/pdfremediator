#!/usr/bin/env python3
"""
AI Alt-Text Generation - Proof of Concept Demo

This demonstrates the AI-powered alt-text generation for PDF images.

Prerequisites:
1. Install: pip install anthropic openai pikepdf Pillow
2. Set API key: export ANTHROPIC_API_KEY='your-key' or export OPENAI_API_KEY='your-key'
3. Have a PDF with images

Usage:
    python ai_alt_text_demo.py /path/to/document.pdf

This will:
- Extract all images from the PDF
- Show each image and ask for page context
- Generate AI alt-text for each image
- Show decorative vs. descriptive classification
- Display cost summary
"""

import sys
from pathlib import Path
import os

# Add parent directory to path to import ai_alt_text
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai_alt_text import AIAltTextGenerator, AltTextResult
except ImportError:
    print("Error: Could not import ai_alt_text module")
    print("Make sure ai_alt_text.py is in the parent directory")
    sys.exit(1)

try:
    import pikepdf
    from pikepdf import Pdf, PdfImage
except ImportError:
    print("Error: pikepdf not installed")
    print("Install with: pip install pikepdf")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not installed")
    print("Install with: pip install Pillow")
    sys.exit(1)


def extract_images_from_pdf(pdf_path: Path) -> list:
    """Extract all images from a PDF."""
    images = []

    try:
        pdf = Pdf.open(pdf_path)

        for page_num, page in enumerate(pdf.pages, 1):
            if '/Resources' not in page or '/XObject' not in page.Resources:
                continue

            xobjects = page.Resources.XObject

            for obj_name in xobjects.keys():
                obj = xobjects[obj_name]

                if obj.get('/Subtype') == '/Image':
                    try:
                        # Extract image
                        pdf_image = PdfImage(obj)
                        pil_image = pdf_image.as_pil_image()

                        # Convert to bytes
                        import io
                        img_bytes = io.BytesIO()
                        pil_image.save(img_bytes, format='PNG')
                        img_bytes_data = img_bytes.getvalue()

                        images.append({
                            'name': str(obj_name),
                            'page': page_num,
                            'width': obj.get('/Width', 0),
                            'height': obj.get('/Height', 0),
                            'image': pil_image,
                            'bytes': img_bytes_data
                        })

                        print(f"  ✓ Extracted {obj_name} from page {page_num} ({pil_image.size[0]}x{pil_image.size[1]})")

                    except Exception as e:
                        print(f"  ✗ Could not extract {obj_name}: {e}")

        pdf.close()

    except Exception as e:
        print(f"Error opening PDF: {e}")

    return images


def display_image_info(img_data: dict):
    """Display information about an image."""
    print("\n" + "=" * 70)
    print(f"Image: {img_data['name']}")
    print(f"Page: {img_data['page']}")
    print(f"Size: {img_data['width']}x{img_data['height']} pixels")
    print("=" * 70)


def demo_heuristic_detection(img_data: dict):
    """Show heuristic decorative detection."""
    width = img_data['width']
    height = img_data['height']

    # Heuristic rules (same as pdf_remediator.py)
    is_decorative = False
    reason = ""

    if width < 20 or height < 20:
        is_decorative = True
        reason = "Very small image (< 20px)"
    elif width * height < 400:
        is_decorative = True
        reason = "Small area (< 400px total)"
    else:
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio > 20 or aspect_ratio < 0.05:
            is_decorative = True
            reason = f"Extreme aspect ratio ({aspect_ratio:.2f})"

    print(f"\nHeuristic Detection:")
    print(f"  Decorative: {is_decorative}")
    if reason:
        print(f"  Reason: {reason}")

    return is_decorative


def get_page_context(page_num: int) -> str:
    """Get page context from user (in real use, would extract from PDF)."""
    print(f"\nEnter context for page {page_num} (or press Enter to skip):")
    print("(This would normally be extracted automatically from the PDF)")
    context = input("Context: ").strip()

    if not context:
        # Provide some example contexts
        examples = {
            1: "This document discusses the quarterly financial results for Q3 2024.",
            2: "The following chart shows revenue growth trends over the past 5 years.",
            3: "Our team consists of experienced professionals in various fields."
        }
        context = examples.get(page_num, "")
        if context:
            print(f"Using example context: {context}")

    return context


def demo_ai_generation(generator: AIAltTextGenerator, img_data: dict, page_context: str):
    """Demonstrate AI alt-text generation."""
    print(f"\n🤖 Generating AI alt-text...")

    try:
        result = generator.generate_alt_text(
            img_data['bytes'],
            page_context=page_context,
            use_cache=True
        )

        print(f"\n✓ AI Analysis Complete:")
        print(f"  Provider: {result.provider}")
        print(f"  Decorative: {result.is_decorative}")
        if not result.is_decorative:
            print(f"  Alt-text: \"{result.alt_text}\"")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Cost: ${result.cost:.4f}")
        if result.cached:
            print(f"  (Cached result)")

        return result

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def run_demo(pdf_path: Path):
    """Run the complete demo."""
    print("=" * 70)
    print("AI Alt-Text Generation - Proof of Concept")
    print("=" * 70)

    # Check API keys
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    has_openai = bool(os.getenv('OPENAI_API_KEY'))

    print(f"\nAPI Keys Available:")
    print(f"  Anthropic Claude: {'✓' if has_anthropic else '✗ (set ANTHROPIC_API_KEY)'}")
    print(f"  OpenAI GPT-4: {'✓' if has_openai else '✗ (set OPENAI_API_KEY)'}")

    if not has_anthropic and not has_openai:
        print("\n❌ No API keys found. Please set at least one:")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   or")
        print("   export OPENAI_API_KEY='sk-...'")
        return

    # Initialize AI generator
    config = {
        'provider': 'claude' if has_anthropic else 'openai',
        'fallback_provider': 'openai' if has_anthropic else None,
        'api_keys': {
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY')
        }
    }

    print(f"\n📄 Opening PDF: {pdf_path}")
    if not pdf_path.exists():
        print(f"❌ Error: File not found: {pdf_path}")
        return

    # Extract images
    print(f"\n🖼️  Extracting images...")
    images = extract_images_from_pdf(pdf_path)

    if not images:
        print("  No images found in PDF")
        return

    print(f"  Found {len(images)} images")

    # Initialize generator
    print(f"\n🤖 Initializing AI generator...")
    try:
        generator = AIAltTextGenerator(config)
        print(f"  ✓ Using provider: {config['provider']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return

    # Process each image
    results = []

    for idx, img_data in enumerate(images, 1):
        display_image_info(img_data)

        # Try to display image (if in terminal with image support)
        try:
            # For terminals that support images (iTerm2, etc.)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                img_data['image'].save(tmp.name)
                print(f"\n[Image saved to: {tmp.name}]")
                # In a real GUI, would display the image here
        except:
            pass

        # Show heuristic detection
        heuristic_decorative = demo_heuristic_detection(img_data)

        # Get page context
        page_context = get_page_context(img_data['page'])

        # Generate AI alt-text
        result = demo_ai_generation(generator, img_data, page_context)

        if result:
            results.append({
                'image': img_data['name'],
                'page': img_data['page'],
                'heuristic_decorative': heuristic_decorative,
                'ai_decorative': result.is_decorative,
                'alt_text': result.alt_text,
                'cost': result.cost,
                'provider': result.provider
            })

        # Ask to continue
        if idx < len(images):
            print(f"\n[{idx}/{len(images)} images processed]")
            cont = input("Continue to next image? (y/n): ").lower()
            if cont != 'y':
                break

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if results:
        total_cost = sum(r['cost'] for r in results)
        decorative_count = sum(1 for r in results if r['ai_decorative'])
        descriptive_count = len(results) - decorative_count

        print(f"\nImages Processed: {len(results)}")
        print(f"  Decorative: {decorative_count}")
        print(f"  Descriptive: {descriptive_count}")
        print(f"\nTotal Cost: ${total_cost:.4f}")
        print(f"Average Cost: ${total_cost/len(results):.4f} per image")

        print(f"\nDetailed Results:")
        for r in results:
            status = "🎨 Decorative" if r['ai_decorative'] else "📝 Descriptive"
            print(f"\n  {r['image']} (Page {r['page']}) - {status}")
            if not r['ai_decorative']:
                print(f"    \"{r['alt_text']}\"")
            print(f"    Cost: ${r['cost']:.4f} ({r['provider']})")

        # Cost tracking
        cost_summary = generator.get_cost_summary()
        print(f"\n💰 Cost Tracking:")
        print(f"  Total API calls: {cost_summary['images_processed']}")
        print(f"  Total cost: ${cost_summary['total_cost']:.4f}")
        if cost_summary['by_provider']:
            print(f"  By provider:")
            for provider, cost in cost_summary['by_provider'].items():
                print(f"    {provider}: ${cost:.4f}")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python ai_alt_text_demo.py <pdf_file>")
        print("\nExample:")
        print("  python ai_alt_text_demo.py ~/Documents/sample.pdf")
        print("\nMake sure to set your API key first:")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        print("  or")
        print("  export OPENAI_API_KEY='sk-...'")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    run_demo(pdf_path)


if __name__ == "__main__":
    main()
