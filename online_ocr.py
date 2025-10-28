#!/usr/bin/env python3
"""
Online OCR Script using OCR.space API
Free tier: 25,000 requests/month
No installation required - uses cloud-based OCR
"""

import requests
import sys
import os
from pathlib import Path

def ocr_pdf_online(input_pdf_path, output_pdf_path=None, api_key=None):
    """
    Perform OCR on a PDF using OCR.space free API.

    Args:
        input_pdf_path: Path to input PDF file
        output_pdf_path: Path to output searchable PDF (optional)
        api_key: OCR.space API key (optional, uses free tier if not provided)

    Returns:
        True if successful, False otherwise
    """

    # Free API key (limited to 500 requests/day per IP)
    # Get your own key at https://ocr.space/ocrapi for higher limits
    if not api_key:
        api_key = 'helloworld'  # Free tier key

    input_path = Path(input_pdf_path)

    if not input_path.exists():
        print(f"Error: File not found: {input_pdf_path}")
        return False

    if not output_pdf_path:
        output_pdf_path = input_path.parent / f"{input_path.stem}_ocr{input_path.suffix}"

    print(f"Starting online OCR...")
    print(f"Input:  {input_pdf_path}")
    print(f"Output: {output_pdf_path}")
    print()

    # OCR.space API endpoint
    url = 'https://api.ocr.space/parse/image'

    # Check file size (API limit is 1MB for free tier)
    file_size = input_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    if file_size_mb > 1:
        print(f"Error: File size is {file_size_mb:.2f} MB")
        print("Free API tier supports files up to 1 MB")
        print()
        print("ALTERNATIVE OPTIONS:")
        print()
        print("1. Adobe Acrobat Pro (RECOMMENDED - Best Quality):")
        print("   - Open PDF in Adobe Acrobat Pro")
        print("   - Tools → Enhance Scans → Recognize Text")
        print("   - Save and then run: python3 pdf_remediator.py output.pdf --no-flatten")
        print()
        print("2. Install Tesseract locally (FREE - Good Quality):")
        print("   - In Terminal: sudo port install tesseract")
        print("   - Then run: tesseract input.pdf output pdf")
        print("   - Then run: python3 pdf_remediator.py output.pdf --no-flatten")
        print()
        print("3. Split PDF into smaller files (<1MB each):")
        print("   - Use Preview.app to extract pages")
        print("   - OCR each section separately")
        print("   - Merge results")
        print()
        return False

    print("Uploading PDF to OCR.space API...")
    print("This may take several minutes for large PDFs...")
    print()

    try:
        with open(input_pdf_path, 'rb') as f:
            # API parameters
            payload = {
                'apikey': api_key,
                'language': 'eng',
                'isOverlayRequired': True,  # Create searchable PDF
                'OCREngine': 2,  # Engine 2 is more accurate
                'scale': True,
                'isTable': True,
                'detectOrientation': True
            }

            files = {
                'file': f
            }

            # Make API request
            response = requests.post(url, files=files, data=payload)
            result = response.json()

            if result.get('IsErroredOnProcessing'):
                error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
                print(f"Error: OCR processing failed: {error_msg}")

                # Provide helpful suggestions
                if 'file size' in error_msg.lower() or 'too large' in error_msg.lower():
                    print("\nSuggestions:")
                    print("1. Split PDF into smaller files")
                    print("2. Use Adobe Acrobat Pro: Tools → Enhance Scans")
                    print("3. Install Tesseract locally: sudo port install tesseract")
                    print("4. Get free API key at ocr.space/ocrapi for higher limits")

                return False

            # Get the searchable PDF URL
            if 'SearchablePDFURL' in result:
                pdf_url = result['SearchablePDFURL']
                print(f"✓ OCR completed successfully!")
                print(f"Downloading searchable PDF from: {pdf_url}")

                # Download the searchable PDF
                pdf_response = requests.get(pdf_url)

                with open(output_pdf_path, 'wb') as out_file:
                    out_file.write(pdf_response.content)

                print(f"✓ Searchable PDF saved: {output_pdf_path}")
                print()
                print("Next steps:")
                print(f"  python3 pdf_remediator.py \"{output_pdf_path}\" --no-flatten")
                print()
                return True
            else:
                print("Error: No searchable PDF URL in response")
                print("Response:", result)
                return False

    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 online_ocr.py <input_pdf> [output_pdf] [api_key]")
        print()
        print("Examples:")
        print('  python3 online_ocr.py input.pdf')
        print('  python3 online_ocr.py input.pdf output_ocr.pdf')
        print('  python3 online_ocr.py input.pdf output_ocr.pdf YOUR_API_KEY')
        print()
        print("Note: Free tier limited to 1MB files and 500 requests/day")
        print("Get free API key at: https://ocr.space/ocrapi")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    api_key = sys.argv[3] if len(sys.argv) > 3 else None

    success = ocr_pdf_online(input_pdf, output_pdf, api_key)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
