#!/usr/bin/env python3
"""
Add heading structure to CreateAI LLM Models PDF
"""

import pikepdf
from pikepdf import Name, Array, Dictionary, String
import sys

def add_heading_structure(input_path, output_path):
    """Add proper heading tags to the PDF structure tree."""

    pdf = pikepdf.open(input_path)

    # Ensure structure tree exists
    if '/StructTreeRoot' not in pdf.Root:
        struct_tree = pdf.make_indirect(Dictionary({
            '/Type': Name('/StructTreeRoot'),
            '/K': Array([])
        }))
        pdf.Root['/StructTreeRoot'] = struct_tree
    else:
        struct_tree = pdf.Root.StructTreeRoot

    if '/K' not in struct_tree or not struct_tree.K:
        struct_tree['/K'] = Array([])

    struct_elements = struct_tree.K

    # Define heading structure
    # Page 1 headings
    headings = [
        {"text": "Use Case", "level": 1, "page": 0},
        {"text": "1. Reasoning-Focused Models", "level": 2, "page": 0},
        {"text": "2. General Purpose / High Similarity Across Domains", "level": 2, "page": 0},
        {"text": "3. Creative Writing", "level": 2, "page": 0},
        {"text": "4. Mathematics", "level": 2, "page": 0},
        {"text": "5. Summarization", "level": 2, "page": 0},
        # Page 2 headings
        {"text": "6. Cost-Efficiency", "level": 2, "page": 1},
        {"text": "7. Quality of Response", "level": 2, "page": 1},
        {"text": "8. Instruction Following", "level": 2, "page": 1},
        {"text": "9. Coding", "level": 2, "page": 1},
        {"text": "Deep Reasoning : o1 Models", "level": 2, "page": 1},
        {"text": "Multilingual: Gemini and Llama and GPT models are multilingual", "level": 2, "page": 1},
    ]

    print(f"Adding {len(headings)} headings to the PDF...")

    # Add heading structure elements
    for heading in headings:
        heading_elem = pdf.make_indirect(Dictionary({
            '/Type': Name('/StructElem'),
            '/S': Name(f'/H{heading["level"]}'),
            '/P': struct_tree,
            '/T': String(heading["text"]),
            '/Pg': pdf.pages[heading["page"]].obj
        }))

        struct_elements.append(heading_elem)
        print(f"  Added H{heading['level']}: {heading['text'][:50]}...")

    # Mark the document as tagged
    if '/MarkInfo' not in pdf.Root:
        pdf.Root['/MarkInfo'] = pdf.make_indirect(Dictionary())

    pdf.Root.MarkInfo['/Marked'] = True
    pdf.Root.MarkInfo['/UserProperties'] = False
    pdf.Root.MarkInfo['/Suspects'] = False

    # Save the PDF
    pdf.save(output_path)
    pdf.close()

    print(f"\nHeadings added successfully!")
    print(f"Output: {output_path}")
    return len(headings)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_headings.py input.pdf output.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        num_headings = add_heading_structure(input_file, output_file)
        print(f"\n✓ Successfully added {num_headings} headings")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
