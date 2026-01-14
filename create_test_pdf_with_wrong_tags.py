#!/usr/bin/env python3
"""
Create a test PDF with intentionally incorrect structure tags.
This will allow us to test the tag correction functionality.
"""

import pikepdf
from pikepdf import Name, Array, Dictionary, String

def create_test_pdf_with_wrong_tags():
    """Create a test PDF with images incorrectly tagged as Tables and headings with wrong hierarchy."""

    # Use the freshly remediated PDF as a base
    input_path = "/Users/alejandradashe/Documents/remediation/remediated/ChatGPT is Dumber Than You Think_remediated.pdf"
    output_path = "/Users/alejandradashe/pdfremediator_github/test_pdf_with_wrong_tags.pdf"

    print("Creating test PDF with intentionally incorrect tags...")
    print(f"Input: {input_path}")

    # Open the remediated PDF
    pdf = pikepdf.open(input_path)

    # Check if it has a structure tree
    if '/StructTreeRoot' not in pdf.Root:
        print("ERROR: Input PDF doesn't have a structure tree. Cannot create test.")
        return False

    struct_tree = pdf.Root.StructTreeRoot

    if '/K' not in struct_tree or not struct_tree.K:
        print("ERROR: Structure tree has no elements. Cannot create test.")
        return False

    struct_elements = struct_tree.K
    wrong_tags_created = 0

    print(f"Found {len(struct_elements)} structure elements")

    # Intentionally corrupt some tags
    for idx, elem in enumerate(struct_elements):
        try:
            if not (isinstance(elem, dict) or hasattr(elem, 'get')):
                continue

            struct_type = str(elem.get('/S', ''))
            title = str(elem.get('/T', ''))

            # Change Figure tags to Table tags (incorrect!)
            if struct_type in ['/Figure', 'Figure'] or 'Figure' in str(struct_type):
                print(f"  ✗ Corrupting tag: '{title}' from {struct_type} to /Table (WRONG!)")
                elem['/S'] = Name('/Table')
                elem['/T'] = String(f"Image on page {idx+1}")  # Keep title with "image" to trigger detection
                wrong_tags_created += 1

            # If there are any H2 headings, make them H4 to create hierarchy gaps
            elif struct_type in ['/H2', 'H2'] or 'H2' in str(struct_type):
                print(f"  ✗ Corrupting heading: '{title}' from H2 to H4 (creates gap!)")
                elem['/S'] = Name('/H4')
                wrong_tags_created += 1

            # Change first H1 to H2 to test "first heading not H1" detection
            elif idx == 0 and (struct_type in ['/H1', 'H1'] or 'H1' in str(struct_type)):
                print(f"  ✗ Corrupting first heading: '{title}' from H1 to H2 (should start with H1!)")
                elem['/S'] = Name('/H2')
                wrong_tags_created += 1

        except Exception as e:
            print(f"  Warning: Error corrupting element {idx}: {e}")
            continue

    if wrong_tags_created == 0:
        print("WARNING: Could not create any incorrect tags. PDF may not have suitable structure.")
        # Create some wrong tags manually
        print("Creating manual incorrect tags...")

        # Add a fake image tagged as Table
        fake_image = Dictionary({
            '/S': Name('/Table'),  # WRONG! Should be /Figure
            '/T': String('Image on page 1'),
            '/Alt': String('This is an image incorrectly tagged as a table'),
            '/P': struct_tree
        })

        # Add a fake heading with wrong hierarchy
        fake_heading_h3 = Dictionary({
            '/S': Name('/H3'),  # WRONG if first heading! Should be H1
            '/T': String('Section Title'),
            '/P': struct_tree
        })

        # Convert to list and add
        elements_list = list(struct_elements) if hasattr(struct_elements, '__iter__') else [struct_elements]
        elements_list.insert(0, fake_image)
        elements_list.insert(1, fake_heading_h3)
        struct_tree['/K'] = Array(elements_list)
        wrong_tags_created = 2
        print(f"  ✗ Added fake image tagged as /Table")
        print(f"  ✗ Added fake first heading as H3 (should be H1)")

    # Save the corrupted PDF
    pdf.save(output_path)
    pdf.close()

    print(f"\n✓ Created test PDF with {wrong_tags_created} intentionally incorrect tags")
    print(f"Output: {output_path}")
    print("\nNow run remediation on this file to test tag correction:")
    print(f"  python3 pdf_remediator.py {output_path} -o test_pdf_corrected.pdf")

    return True

if __name__ == "__main__":
    create_test_pdf_with_wrong_tags()
