#!/usr/bin/env python3
"""
AI-Powered Alt-Text Generator for PDF Remediator

This module provides AI-powered alt-text generation using various vision APIs:
- Anthropic Claude 3.5 Sonnet (recommended)
- OpenAI GPT-4o with vision
- Google Cloud Vision AI
- Azure Computer Vision

Features:
- Automatic decorative vs. descriptive image detection
- Context-aware alt-text generation using surrounding page text
- Multiple provider support with fallback
- Cost tracking and limits
- Batch processing support
- Caching to avoid redundant API calls
"""

import base64
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from datetime import datetime
import io

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from msrest.authentication import CognitiveServicesCredentials
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


@dataclass
class AltTextResult:
    """Result from AI alt-text generation."""
    is_decorative: bool
    alt_text: str
    reasoning: str = ""
    confidence: float = 1.0
    provider: str = ""
    cost: float = 0.0
    cached: bool = False


@dataclass
class CostTracker:
    """Track API costs."""
    total_cost: float = 0.0
    images_processed: int = 0
    by_provider: Dict[str, float] = None
    by_document: Dict[str, float] = None

    def __post_init__(self):
        if self.by_provider is None:
            self.by_provider = {}
        if self.by_document is None:
            self.by_document = {}

    def add_cost(self, provider: str, cost: float, document: str = "default"):
        """Add cost for an API call."""
        self.total_cost += cost
        self.images_processed += 1
        self.by_provider[provider] = self.by_provider.get(provider, 0.0) + cost
        self.by_document[document] = self.by_document.get(document, 0.0) + cost

    def get_average_cost(self) -> float:
        """Get average cost per image."""
        return self.total_cost / self.images_processed if self.images_processed > 0 else 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class AltTextCache:
    """Cache for alt-text results to avoid redundant API calls."""

    def __init__(self, cache_dir: Path = None):
        """Initialize cache."""
        self.cache_dir = cache_dir or Path.home() / ".pdf_remediator" / "alt_text_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "cache.json"
        self.cache: Dict[str, dict] = {}
        self.load_cache()

    def _hash_image(self, image_bytes: bytes, context: str = "") -> str:
        """Generate hash for image + context."""
        hasher = hashlib.sha256()
        hasher.update(image_bytes)
        hasher.update(context.encode('utf-8'))
        return hasher.hexdigest()

    def get(self, image_bytes: bytes, context: str = "") -> Optional[AltTextResult]:
        """Get cached result."""
        key = self._hash_image(image_bytes, context)
        if key in self.cache:
            data = self.cache[key]
            result = AltTextResult(**data)
            result.cached = True
            return result
        return None

    def set(self, image_bytes: bytes, result: AltTextResult, context: str = ""):
        """Cache result."""
        key = self._hash_image(image_bytes, context)
        self.cache[key] = {
            'is_decorative': result.is_decorative,
            'alt_text': result.alt_text,
            'reasoning': result.reasoning,
            'confidence': result.confidence,
            'provider': result.provider,
            'cost': result.cost,
            'timestamp': datetime.now().isoformat()
        }
        self.save_cache()

    def load_cache(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                self.cache = {}

    def save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def clear(self):
        """Clear cache."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()


class AIAltTextGenerator:
    """AI-powered alt-text generator with multi-provider support."""

    # Pricing per 1M tokens (input/output)
    PRICING = {
        'claude-3-5-sonnet-20241022': {'input': 3.0, 'output': 15.0},
        'gpt-4o': {'input': 2.5, 'output': 10.0},
        'gpt-4-vision-preview': {'input': 10.0, 'output': 30.0},
        'google-vision': {'per_image': 0.0015},  # $1.50 per 1000
        'azure-vision': {'per_image': 0.001}  # $1.00 per 1000
    }

    def __init__(self, config: Dict = None):
        """
        Initialize AI alt-text generator.

        Args:
            config: Configuration dictionary with API keys and options
        """
        self.config = config or {}
        self.cost_tracker = CostTracker()
        self.cache = AltTextCache()

        # Initialize API clients
        self.anthropic_client = None
        self.openai_client = None
        self.google_client = None
        self.azure_client = None

        self._init_clients()

    def _init_clients(self):
        """Initialize API clients based on available libraries and config."""
        api_keys = self.config.get('api_keys', {})

        # Anthropic Claude
        if ANTHROPIC_AVAILABLE and api_keys.get('anthropic'):
            try:
                self.anthropic_client = anthropic.Anthropic(
                    api_key=api_keys['anthropic']
                )
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")

        # OpenAI
        if OPENAI_AVAILABLE and api_keys.get('openai'):
            try:
                openai.api_key = api_keys['openai']
                self.openai_client = openai
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")

        # Google Cloud Vision
        if GOOGLE_VISION_AVAILABLE and api_keys.get('google'):
            try:
                # Set credentials
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = api_keys['google']
                self.google_client = vision.ImageAnnotatorClient()
            except Exception as e:
                print(f"Warning: Could not initialize Google Vision client: {e}")

        # Azure Computer Vision
        if AZURE_AVAILABLE and api_keys.get('azure'):
            try:
                azure_config = api_keys['azure']
                self.azure_client = ComputerVisionClient(
                    endpoint=azure_config['endpoint'],
                    credentials=CognitiveServicesCredentials(azure_config['key'])
                )
            except Exception as e:
                print(f"Warning: Could not initialize Azure client: {e}")

    def generate_alt_text(
        self,
        image_bytes: bytes,
        page_context: str = "",
        provider: str = "auto",
        use_cache: bool = True
    ) -> AltTextResult:
        """
        Generate alt-text for an image.

        Args:
            image_bytes: Image data as bytes
            page_context: Surrounding text from the page for context
            provider: API provider to use ('auto', 'claude', 'openai', 'google', 'azure')
            use_cache: Whether to use cached results

        Returns:
            AltTextResult with alt-text and metadata
        """
        # Check cache first
        if use_cache:
            cached_result = self.cache.get(image_bytes, page_context)
            if cached_result:
                return cached_result

        # Determine provider
        if provider == "auto":
            provider = self._choose_provider(image_bytes, page_context)

        # Generate alt-text using selected provider
        result = None
        try:
            if provider == "claude":
                result = self._generate_with_claude(image_bytes, page_context)
            elif provider == "openai":
                result = self._generate_with_openai(image_bytes, page_context)
            elif provider == "google":
                result = self._generate_with_google(image_bytes, page_context)
            elif provider == "azure":
                result = self._generate_with_azure(image_bytes, page_context)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Track cost
            self.cost_tracker.add_cost(provider, result.cost)

            # Cache result
            if use_cache:
                self.cache.set(image_bytes, result, page_context)

            return result

        except Exception as e:
            print(f"Error generating alt-text with {provider}: {e}")

            # Try fallback
            fallback_provider = self.config.get('fallback_provider')
            if fallback_provider and fallback_provider != provider:
                print(f"Trying fallback provider: {fallback_provider}")
                return self.generate_alt_text(
                    image_bytes, page_context, fallback_provider, use_cache
                )

            # Return error result
            return AltTextResult(
                is_decorative=False,
                alt_text="[Error generating alt-text - manual review required]",
                reasoning=f"Error: {str(e)}",
                confidence=0.0,
                provider=provider
            )

    def _choose_provider(self, image_bytes: bytes, page_context: str) -> str:
        """Choose best provider based on configuration and availability."""
        # Get preferred provider from config
        preferred = self.config.get('provider', 'claude')

        # Check if preferred provider is available
        if preferred == 'claude' and self.anthropic_client:
            return 'claude'
        elif preferred == 'openai' and self.openai_client:
            return 'openai'
        elif preferred == 'google' and self.google_client:
            return 'google'
        elif preferred == 'azure' and self.azure_client:
            return 'azure'

        # Fallback to first available
        if self.anthropic_client:
            return 'claude'
        elif self.openai_client:
            return 'openai'
        elif self.google_client:
            return 'google'
        elif self.azure_client:
            return 'azure'

        raise ValueError("No AI vision providers available. Please install and configure at least one.")

    def _generate_with_claude(self, image_bytes: bytes, page_context: str) -> AltTextResult:
        """Generate alt-text using Anthropic Claude."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")

        # Encode image
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Detect image type
        import imghdr
        image_type = imghdr.what(None, h=image_bytes)
        if not image_type:
            # Try to detect from bytes
            if image_bytes[:4] == b'\x89PNG':
                image_type = 'png'
            elif image_bytes[:3] == b'\xff\xd8\xff':
                image_type = 'jpeg'
            else:
                image_type = 'jpeg'  # default fallback

        # Create prompt
        system_prompt = """You are an accessibility expert generating alt-text for PDF images following WCAG 2.2 guidelines.

CRITICAL RULES:
1. Decorative images (borders, lines, spacers, backgrounds, purely aesthetic elements, page numbers, headers/footers) MUST return: {"is_decorative": true, "alt_text": "", "reasoning": "explanation"}
2. Informational images require concise, descriptive alt-text that conveys the content
3. Focus on WHAT the image shows, not just identifying the type (avoid "image of", "picture of", "diagram of")
4. Use page context to understand image purpose in the document
5. Keep alt-text clear and under 150 characters when possible
6. For charts/graphs: describe the key takeaway, not just "bar chart" or "line graph"
7. For photos: describe relevant details, not just "photo of people"
8. For logos: include company name and any tagline if visible

Respond ONLY in valid JSON format:
{"is_decorative": boolean, "alt_text": "description", "reasoning": "why this classification", "confidence": 0.0-1.0}"""

        user_prompt = f"""Page context (surrounding text):
{page_context[:500] if page_context else "[No context available]"}

Analyze this image and provide appropriate alt-text following WCAG 2.2 guidelines."""

        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
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

            # Parse response
            response_text = message.content[0].text

            # Extract JSON from response (in case there's extra text)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                response_data = json.loads(response_text)

            # Calculate cost
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            cost = (input_tokens * self.PRICING['claude-3-5-sonnet-20241022']['input'] / 1_000_000 +
                   output_tokens * self.PRICING['claude-3-5-sonnet-20241022']['output'] / 1_000_000)

            return AltTextResult(
                is_decorative=response_data.get('is_decorative', False),
                alt_text=response_data.get('alt_text', ''),
                reasoning=response_data.get('reasoning', ''),
                confidence=response_data.get('confidence', 0.9),
                provider='claude',
                cost=cost
            )

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _generate_with_openai(self, image_bytes: bytes, page_context: str) -> AltTextResult:
        """Generate alt-text using OpenAI GPT-4 Vision."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        # Encode image
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an accessibility expert generating alt-text for PDF images following WCAG 2.2 guidelines.

Rules:
1. If image is decorative (borders, lines, backgrounds, page numbers), respond with: {"is_decorative": true, "alt_text": "", "reasoning": "explanation"}
2. If image contains meaningful content, provide concise, descriptive alt-text
3. Focus on what the image depicts, not just identifying it as "chart" or "diagram"
4. Use surrounding text context to understand image purpose
5. Keep alt-text under 150 characters when possible

Respond in JSON format: {"is_decorative": boolean, "alt_text": "text", "reasoning": "explanation", "confidence": 0.0-1.0}"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Page context: {page_context[:500] if page_context else '[No context]'}\n\nAnalyze this image:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )

            # Parse response
            response_text = response.choices[0].message.content

            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                response_data = json.loads(response_text)

            # Calculate cost (approximation)
            # GPT-4o vision pricing is complex, using rough estimate
            cost = 0.0125  # ~$0.0125 per image

            return AltTextResult(
                is_decorative=response_data.get('is_decorative', False),
                alt_text=response_data.get('alt_text', ''),
                reasoning=response_data.get('reasoning', ''),
                confidence=response_data.get('confidence', 0.85),
                provider='openai',
                cost=cost
            )

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _generate_with_google(self, image_bytes: bytes, page_context: str) -> AltTextResult:
        """Generate alt-text using Google Cloud Vision."""
        if not self.google_client:
            raise ValueError("Google Vision client not initialized")

        try:
            image = vision.Image(content=image_bytes)

            # Multiple detection types
            response = self.google_client.annotate_image({
                'image': image,
                'features': [
                    {'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': 10},
                    {'type_': vision.Feature.Type.TEXT_DETECTION},
                    {'type_': vision.Feature.Type.OBJECT_LOCALIZATION},
                    {'type_': vision.Feature.Type.IMAGE_PROPERTIES}
                ]
            })

            # Analyze results
            labels = [label.description for label in response.label_annotations]
            text = response.text_annotations[0].description if response.text_annotations else ""
            objects = response.localized_object_annotations

            # Heuristic for decorative
            is_decorative = False
            reasoning = ""

            if len(objects) == 0 and len(labels) < 3:
                is_decorative = True
                reasoning = "Few objects and labels detected, likely decorative"

            # Check for common decorative labels
            decorative_labels = {'line', 'border', 'background', 'pattern', 'texture', 'separator'}
            if any(label.lower() in decorative_labels for label in labels[:3]):
                is_decorative = True
                reasoning = "Detected decorative elements"

            # Build alt text
            alt_text = ""
            if not is_decorative:
                if text and len(text) > 10:
                    alt_text = f"Image containing text: {text[:100]}"
                    reasoning = "Image contains text content"
                elif objects:
                    obj_names = [obj.name for obj in objects[:3]]
                    alt_text = f"Image showing {', '.join(obj_names)}"
                    reasoning = f"Detected objects: {', '.join(obj_names)}"
                elif labels:
                    alt_text = f"Image showing {', '.join(labels[:3])}"
                    reasoning = f"Based on labels: {', '.join(labels[:5])}"
                else:
                    alt_text = "[Image requires manual review]"
                    reasoning = "Could not determine image content"

            return AltTextResult(
                is_decorative=is_decorative,
                alt_text=alt_text,
                reasoning=reasoning,
                confidence=0.7,
                provider='google',
                cost=self.PRICING['google-vision']['per_image']
            )

        except Exception as e:
            raise Exception(f"Google Vision API error: {str(e)}")

    def _generate_with_azure(self, image_bytes: bytes, page_context: str) -> AltTextResult:
        """Generate alt-text using Azure Computer Vision."""
        if not self.azure_client:
            raise ValueError("Azure client not initialized")

        try:
            # Analyze image
            analysis = self.azure_client.analyze_image_in_stream(
                io.BytesIO(image_bytes),
                visual_features=['Description', 'Tags', 'Objects', 'ImageType']
            )

            # Check if likely decorative
            is_decorative = False
            reasoning = ""

            if analysis.image_type.clip_art_type > 2 or analysis.image_type.line_drawing_type > 2:
                if len(analysis.objects) == 0:
                    is_decorative = True
                    reasoning = "Detected as clip art or line drawing with no objects"

            # Generate alt text
            alt_text = ""
            if not is_decorative:
                if analysis.description.captions:
                    alt_text = analysis.description.captions[0].text
                    confidence = analysis.description.captions[0].confidence
                    reasoning = f"Caption generated with {confidence:.0%} confidence"
                else:
                    tags = [tag.name for tag in analysis.tags[:3]]
                    if tags:
                        alt_text = f"Image showing {', '.join(tags)}"
                        reasoning = f"Based on tags: {', '.join(tags)}"
                    else:
                        alt_text = "[Image requires manual review]"
                        reasoning = "Could not generate description"

            return AltTextResult(
                is_decorative=is_decorative,
                alt_text=alt_text,
                reasoning=reasoning,
                confidence=0.75,
                provider='azure',
                cost=self.PRICING['azure-vision']['per_image']
            )

        except Exception as e:
            raise Exception(f"Azure API error: {str(e)}")

    def get_cost_summary(self) -> Dict:
        """Get cost tracking summary."""
        return self.cost_tracker.to_dict()

    def clear_cache(self):
        """Clear alt-text cache."""
        self.cache.clear()


# Example usage and testing
if __name__ == "__main__":
    print("AI Alt-Text Generator - Test Mode")
    print("=" * 60)

    # Example configuration
    config = {
        'provider': 'claude',  # or 'openai', 'google', 'azure'
        'fallback_provider': 'openai',
        'api_keys': {
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            # 'google': '/path/to/service-account.json',
            # 'azure': {
            #     'key': os.getenv('AZURE_VISION_KEY'),
            #     'endpoint': os.getenv('AZURE_VISION_ENDPOINT')
            # }
        }
    }

    try:
        generator = AIAltTextGenerator(config)
        print(f"✓ Initialized with provider: {config['provider']}")
        print(f"✓ Providers available:")
        print(f"  - Claude: {generator.anthropic_client is not None}")
        print(f"  - OpenAI: {generator.openai_client is not None}")
        print(f"  - Google: {generator.google_client is not None}")
        print(f"  - Azure: {generator.azure_client is not None}")

    except Exception as e:
        print(f"✗ Error initializing: {e}")
        print("\nTo use this module, install required libraries:")
        print("  pip install anthropic openai google-cloud-vision azure-cognitiveservices-vision-computervision")
        print("\nAnd set API keys:")
        print("  export ANTHROPIC_API_KEY='your-key'")
        print("  export OPENAI_API_KEY='your-key'")
