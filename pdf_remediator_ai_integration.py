#!/usr/bin/env python3
"""
PDF Remediator - AI Integration Patch

This file contains the modifications needed to integrate AI alt-text generation
into the main pdf_remediator.py file.

Usage:
1. Install required libraries:
   pip install anthropic openai google-cloud-vision azure-cognitiveservices-vision-computervision

2. Create config file: ~/.pdf_remediator/ai_config.json
   {
     "ai_alt_text": {
       "enabled": true,
       "provider": "claude",
       "fallback_provider": "openai",
       "api_keys": {
         "anthropic": "sk-ant-...",
         "openai": "sk-..."
       }
     }
   }

3. Use with pdf_remediator.py:
   python pdf_remediator.py input.pdf --use-ai-alt-text

This file shows what needs to be added to pdf_remediator.py.
"""

from pathlib import Path
import json
import sys

# Add these imports to pdf_remediator.py
"""
# Add after existing imports:
try:
    from ai_alt_text import AIAltTextGenerator, AltTextResult
    AI_ALT_TEXT_AVAILABLE = True
except ImportError:
    AI_ALT_TEXT_AVAILABLE = False
"""


# Add this method to the EnhancedPDFRemediator class
def _load_ai_config(self) -> dict:
    """
    Load AI configuration from file.

    Looks for config in:
    1. ~/.pdf_remediator/ai_config.json
    2. ./ai_config.json (current directory)
    3. Environment variables

    Returns:
        dict: AI configuration
    """
    config = {
        'ai_alt_text': {
            'enabled': False,
            'provider': 'claude',
            'fallback_provider': 'openai',
            'api_keys': {}
        }
    }

    # Try to load from config file
    config_paths = [
        Path.home() / '.pdf_remediator' / 'ai_config.json',
        Path('./ai_config.json')
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                    print(f"  Loaded AI config from: {config_path}")
                    break
            except Exception as e:
                print(f"  Warning: Could not load config from {config_path}: {e}")

    # Override with environment variables if present
    import os
    if os.getenv('ANTHROPIC_API_KEY'):
        config['ai_alt_text']['api_keys']['anthropic'] = os.getenv('ANTHROPIC_API_KEY')
    if os.getenv('OPENAI_API_KEY'):
        config['ai_alt_text']['api_keys']['openai'] = os.getenv('OPENAI_API_KEY')
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        config['ai_alt_text']['api_keys']['google'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    return config


# Add this to EnhancedPDFRemediator.__init__
def _init_ai_generator(self, use_ai: bool = False):
    """
    Initialize AI alt-text generator if enabled.

    Add this to __init__ method after existing initialization:

    self.ai_generator = None
    self.use_ai_alt_text = use_ai

    if use_ai and AI_ALT_TEXT_AVAILABLE:
        try:
            ai_config = self._load_ai_config()
            if ai_config.get('ai_alt_text', {}).get('enabled') or use_ai:
                self.ai_generator = AIAltTextGenerator(ai_config['ai_alt_text'])
                print("  ✓ AI alt-text generation enabled")
        except Exception as e:
            print(f"  Warning: Could not initialize AI generator: {e}")
            print("  Falling back to heuristic alt-text generation")
    """
    pass


# Modified _generate_alt_text method for EnhancedPDFRemediator
def _generate_alt_text_enhanced(self, img_info, page_num: int) -> str:
    """
    Generate contextual alt text for an image.
    ENHANCED with AI capabilities.

    Replace the existing _generate_alt_text method with this version.
    """
    # If AI is available and enabled, use it
    if hasattr(self, 'ai_generator') and self.ai_generator:
        try:
            # Extract page context (surrounding text)
            page_context = self._extract_page_context(page_num)

            # Extract image bytes
            image_bytes = self._extract_image_bytes(img_info, page_num)

            if image_bytes:
                # Generate with AI
                result = self.ai_generator.generate_alt_text(
                    image_bytes,
                    page_context=page_context,
                    use_cache=True
                )

                # Update image info based on AI result
                if result.is_decorative:
                    img_info.is_decorative = True
                    img_info.alt_text = ""
                    return ""
                else:
                    img_info.alt_text = result.alt_text
                    return result.alt_text

        except Exception as e:
            print(f"  Warning: AI alt-text generation failed: {e}")
            print(f"  Falling back to heuristic for image on page {page_num}")

    # Fallback to original heuristic method
    aspect_ratio = img_info.width / img_info.height if img_info.height > 0 else 1

    if aspect_ratio > 2:
        return f"Horizontal diagram or illustration (page {page_num}). Review and update with actual content description."
    elif aspect_ratio < 0.5:
        return f"Vertical graphic (page {page_num}). Review and update with actual content description."
    elif img_info.width > 400 and img_info.height > 400:
        return f"Figure or photograph (page {page_num}). Review and update with description of what image depicts."
    else:
        return f"Graphic element (page {page_num}). Review and update with actual content or purpose."


# Add these helper methods to EnhancedPDFRemediator
def _extract_page_context(self, page_num: int, context_chars: int = 500) -> str:
    """
    Extract text context from page for AI analysis.

    Args:
        page_num: Page number (1-indexed)
        context_chars: Number of characters to extract

    Returns:
        str: Text content from page
    """
    try:
        page = self.pdf.pages[page_num - 1]

        # Try to extract text using pikepdf
        # This is a simplified extraction - full implementation would parse content streams
        if '/Contents' in page:
            # This would need proper content stream parsing
            # For now, return placeholder
            return f"[Page {page_num} context - implement content stream parsing]"

        return ""

    except Exception as e:
        print(f"  Warning: Could not extract page context: {e}")
        return ""


def _extract_image_bytes(self, img_info, page_num: int) -> bytes:
    """
    Extract image bytes from PDF.

    Args:
        img_info: ImageInfo object
        page_num: Page number (1-indexed)

    Returns:
        bytes: Image data
    """
    try:
        page = self.pdf.pages[page_num - 1]

        if '/Resources' not in page or '/XObject' not in page.Resources:
            return None

        xobjects = page.Resources.XObject

        # Find the image by name
        for obj_name in xobjects.keys():
            if str(obj_name) == img_info.name:
                obj = xobjects[obj_name]

                if obj.get('/Subtype') == '/Image':
                    # Extract image using pikepdf
                    try:
                        from pikepdf import PdfImage
                        pdf_image = PdfImage(obj)

                        # Get image as PIL Image, then convert to bytes
                        pil_image = pdf_image.as_pil_image()

                        import io
                        img_bytes = io.BytesIO()
                        pil_image.save(img_bytes, format='PNG')
                        return img_bytes.getvalue()

                    except Exception as e:
                        print(f"  Warning: Could not extract image: {e}")
                        return None

        return None

    except Exception as e:
        print(f"  Warning: Could not extract image bytes: {e}")
        return None


# Modified analyze_images method
def analyze_images_with_ai(self):
    """
    Analyze all images in the PDF and determine if decorative.
    ENHANCED with AI capabilities.

    This replaces the existing analyze_images method.
    """
    images = []

    try:
        for page_num, page in enumerate(self.pdf.pages, 1):
            if '/Resources' not in page or '/XObject' not in page.Resources:
                continue

            xobjects = page.Resources.XObject

            for obj_name in xobjects.keys():
                obj = xobjects[obj_name]

                if obj.get('/Subtype') == '/Image':
                    width = obj.get('/Width', 0)
                    height = obj.get('/Height', 0)

                    img_info = ImageInfo(
                        name=str(obj_name),
                        width=width,
                        height=height,
                        page_number=page_num
                    )

                    # First, try heuristic decorative detection (free)
                    img_info.is_decorative = img_info.determine_if_decorative()

                    if img_info.is_decorative:
                        img_info.alt_text = ""
                        self.report.decorative_images += 1
                    else:
                        # Generate alt text (will use AI if available)
                        img_info.alt_text = self._generate_alt_text(img_info, page_num)

                        # Check if AI determined it's decorative
                        if img_info.is_decorative:
                            self.report.decorative_images += 1

                    images.append(img_info)

        # If AI was used, print cost summary
        if hasattr(self, 'ai_generator') and self.ai_generator:
            cost_summary = self.ai_generator.get_cost_summary()
            if cost_summary['images_processed'] > 0:
                print(f"\n  AI Alt-Text Generation Summary:")
                print(f"  - Images processed: {cost_summary['images_processed']}")
                print(f"  - Total cost: ${cost_summary['total_cost']:.4f}")
                print(f"  - Average cost/image: ${cost_summary['total_cost']/cost_summary['images_processed']:.4f}")

    except Exception as e:
        print(f"Warning: Error analyzing images: {e}")

    self.images = images
    return images


# Add command-line argument to main()
def add_cli_arguments():
    """
    Add these arguments to the argparse parser in main():

    parser.add_argument('--use-ai-alt-text', action='store_true',
                       help='Use AI to generate alt-text for images (requires API keys)')
    parser.add_argument('--ai-provider', choices=['auto', 'claude', 'openai', 'google', 'azure'],
                       default='auto', help='AI provider to use for alt-text generation')
    parser.add_argument('--ai-config', help='Path to AI configuration file')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable caching of AI-generated alt-text')
    """
    pass


# Modified main() function integration
def integrate_ai_in_main():
    """
    In the main() function, after initializing remediator:

    # Initialize enhanced remediator
    print(f"Loading PDF: {args.input}")
    remediator = EnhancedPDFRemediator(args.input, args.output)

    # NEW: Initialize AI if requested
    if args.use_ai_alt_text:
        if not AI_ALT_TEXT_AVAILABLE:
            print("Error: AI alt-text feature requires additional libraries.")
            print("Install with: pip install anthropic openai")
            sys.exit(1)

        remediator._init_ai_generator(use_ai=True)
        if args.ai_provider != 'auto':
            remediator.ai_generator.config['provider'] = args.ai_provider

    # Continue with rest of main()...
    """
    pass


# Example configuration file template
def create_example_config():
    """
    Create example configuration file.
    """
    config = {
        "ai_alt_text": {
            "enabled": True,
            "provider": "claude",
            "fallback_provider": "openai",
            "api_keys": {
                "anthropic": "sk-ant-api03-...",
                "openai": "sk-...",
                "google": "/path/to/service-account.json",
                "azure": {
                    "key": "your-azure-key",
                    "endpoint": "https://your-resource.cognitiveservices.azure.com/"
                }
            },
            "options": {
                "max_tokens": 300,
                "temperature": 0.3,
                "use_heuristic_first": True,
                "batch_size": 10,
                "max_alt_text_length": 150
            },
            "cost_limit": {
                "max_cost_per_document": 5.0,
                "warn_threshold": 1.0
            }
        }
    }

    config_path = Path.home() / '.pdf_remediator' / 'ai_config.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Created example config at: {config_path}")
    print("\nEdit this file to add your API keys.")


if __name__ == "__main__":
    print("PDF Remediator - AI Integration Guide")
    print("=" * 60)
    print("\nThis file contains the code needed to integrate AI alt-text")
    print("generation into pdf_remediator.py")
    print("\nOptions:")
    print("1. Create example config file")
    print("2. Show integration instructions")
    print("3. Exit")

    choice = input("\nSelect option (1-3): ").strip()

    if choice == "1":
        create_example_config()
    elif choice == "2":
        print("\nIntegration Instructions:")
        print("-" * 60)
        print("\n1. Copy ai_alt_text.py to the same directory as pdf_remediator.py")
        print("\n2. Install required libraries:")
        print("   pip install anthropic openai google-cloud-vision")
        print("\n3. Add imports to pdf_remediator.py:")
        print("   from ai_alt_text import AIAltTextGenerator, AltTextResult")
        print("\n4. Add --use-ai-alt-text argument to CLI")
        print("\n5. Initialize AI generator in __init__")
        print("\n6. Replace _generate_alt_text method with AI version")
        print("\n7. Create config file with API keys:")
        print("   ~/.pdf_remediator/ai_config.json")
        print("\nSee this file's source code for detailed implementation.")
    else:
        print("Exiting.")
