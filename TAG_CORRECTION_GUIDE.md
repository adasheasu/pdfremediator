# Tag Correction - Enhanced Feature Guide

## Overview

PDF Remediator v2.3 now includes **intelligent tag correction** capabilities that detect and automatically fix incorrectly placed structure tags in PDFs. This ensures that content is not only tagged, but tagged correctly according to PDF/UA standards.

---

## What's New in v2.3

### 🔧 Automatic Tag Correction

The tool now detects and fixes structural tag errors that would cause accessibility failures:

**Common Issues Fixed:**
- Images tagged as `/Table` instead of `/Figure`
- Tables tagged as `/Figure` instead of `/Table`
- Form fields tagged with wrong structure types
- Skipped heading levels (H1→H3 corrected to H1→H2→H3)
- First heading not starting with H1

**Before (v2.2):**
```
PDF with Image tagged as /Table
→ Tool skips (appears "properly tagged")
→ Screen readers misinterpret content
→ ❌ Accessibility failure
```

**After (v2.3):**
```
PDF with Image tagged as /Table
→ Tool detects incorrect type
→ Corrects /Table to /Figure
→ ✓ Screen readers work correctly
```

---

## Features

### ✅ Tag Type Validation

**Validates and corrects:**
- Images must be tagged as `/Figure`
- Tables must be tagged as `/Table`
- Form fields must be tagged as `/Form`
- Headings must be `/H1` through `/H6`
- Artifacts must be tagged as `/Artifact`

**Detection method:**
- Analyzes structure element `/S` (type) field
- Cross-references with element title and content
- Identifies type mismatches
- Corrects in place

**Example output:**
```
Validating and fixing tag types...
  ⚠️ Fixing incorrect tag: 'Image on page 1' tagged as /Table, should be /Figure
  ⚠️ Fixing incorrect tag: 'Table on page 3' tagged as /Figure, should be /Table
  ⚠️ Fixing incorrect tag: 'Form field' tagged as /Span, should be /Form
  ✓ Fixed 3 incorrect tag types
```

### ✅ Heading Hierarchy Correction

**Fixes hierarchy issues:**
- Ensures first heading is H1
- Fills skipped heading levels
- Maintains proper nesting (H1→H2→H3, not H1→H3)

**Detection method:**
- Collects all headings in document
- Validates hierarchy order
- Adjusts levels to fix gaps
- Preserves heading content

**Example output:**
```
Fixing heading hierarchy...
  ⚠️ Fixing heading hierarchy: First heading is H2, changing to H1
  ⚠️ Fixing heading hierarchy: H2→H4 (skipped level), changing H4 to H3
  ✓ Fixed 2 heading hierarchy issues
```

### ✅ Structure Element Removal

**Can remove incorrect tags:**
- Duplicate structure elements
- Malformed tag entries
- Orphaned structure references
- Invalid parent-child relationships

**Safety features:**
- Only removes after validation
- Preserves valid structure
- Maintains document integrity

---

## How It Works

### Validation Process

```
1. Load PDF and existing structure tree
   ↓
2. For each structure element:
   - Extract /S (type) field
   - Extract /T (title) field
   - Extract /Alt (alt-text) field
   ↓
3. Validate tag type matches content:
   - Check title for clues ("image", "table", etc.)
   - Verify type is appropriate
   - Flag mismatches
   ↓
4. Correction Decision:
   - Incorrect type → Fix in place
   - Missing type → Add correct type
   - Invalid structure → Remove or fix
   ↓
5. Apply corrections and save
```

### Tag Type Mapping

The tool uses these mappings to validate types:

```python
Content Type    → Expected Structure Types
─────────────────────────────────────────
image           → /Figure
table           → /Table
form field      → /Form
heading         → /H1, /H2, /H3, /H4, /H5, /H6
annotation      → /Note, /Annot, /Stamp
artifact        → /Artifact
paragraph       → /P
list            → /L, /LI
```

---

## Usage

### Automatic (Default Behavior)

Tag correction runs automatically during remediation:

```bash
python pdf_remediator.py input.pdf
```

The tool will:
1. Detect existing tags
2. Validate tag types
3. Fix incorrect types
4. Correct heading hierarchy
5. Output corrected PDF

### Output During Correction

You'll see progress messages:

```
Starting comprehensive remediation...
...
Validating and fixing tag types...
  ⚠️ Fixing incorrect tag: 'Image on page 1' tagged as /Table, should be /Figure
  ⚠️ Fixing incorrect tag: 'Data table' tagged as /Figure, should be /Table
  ✓ Fixed 2 incorrect tag types

Fixing heading hierarchy...
  ⚠️ Fixing heading hierarchy: H1→H3 (skipped level), changing H3 to H2
  ✓ Fixed 1 heading hierarchy issues
```

### Validation Reports

Check the final report for correction statistics:

```
REMEDIATION STATISTICS
----------------------------------------------------------------------
Images Tagged:           12
Tables Tagged:           2
Headings Tagged:         5
Tag Types Corrected:     3    ← New statistic
Hierarchy Issues Fixed:  1    ← New statistic
```

---

## Benefits

### 1. **Ensures Correct Structure**

Fixes type mismatches that break accessibility:

```
Before: Image tagged as /Table
→ JAWS announces "Table with 0 rows and 0 columns"
→ ❌ Confusing for users

After: Image tagged as /Figure
→ JAWS announces "Figure: [alt-text]"
→ ✓ Clear and correct
```

### 2. **Prevents PAC Failures**

Common PAC 3 errors that are now auto-fixed:

```
❌ "Structure element type mismatch"
❌ "Invalid heading hierarchy"
❌ "Skipped heading level"
```

After correction:

```
✓ All structure elements properly typed
✓ Valid heading hierarchy
✓ No skipped levels
```

### 3. **Saves Manual Correction Time**

```
Manual correction in Adobe Acrobat:
- Find incorrect tags: 30 minutes
- Fix each tag individually: 2 minutes each
- Total for 10 errors: 50 minutes

Automatic correction:
- Total time: < 1 second
- Savings: ~99% faster
```

### 4. **Improves Compliance**

Meets stricter PDF/UA requirements:

```
PDF/UA-1 Requirements:
✓ All structure elements properly typed
✓ Logical heading hierarchy
✓ No gaps in structure tree
✓ Valid parent-child relationships
```

---

## Examples

### Example 1: Image Tagged as Table

**Problem PDF:**
```xml
<StructElem>
  <S>/Table</S>  ← Wrong!
  <T>Image on page 1</T>
  <Alt>Chart showing revenue growth</Alt>
</StructElem>
```

**After Correction:**
```xml
<StructElem>
  <S>/Figure</S>  ← Fixed!
  <T>Image on page 1</T>
  <Alt>Chart showing revenue growth</Alt>
</StructElem>
```

**Output:**
```
Validating and fixing tag types...
  ⚠️ Fixing incorrect tag: 'Image on page 1' tagged as /Table, should be /Figure
  ✓ Fixed 1 incorrect tag types
```

### Example 2: Skipped Heading Level

**Problem PDF:**
```xml
<StructElem><S>/H1</S><T>Chapter 1</T></StructElem>
<StructElem><S>/H3</S><T>Section 1.1</T></StructElem>  ← Skipped H2!
<StructElem><S>/H3</S><T>Section 1.2</T></StructElem>
```

**After Correction:**
```xml
<StructElem><S>/H1</S><T>Chapter 1</T></StructElem>
<StructElem><S>/H2</S><T>Section 1.1</T></StructElem>  ← Fixed to H2!
<StructElem><S>/H2</S><T>Section 1.2</T></StructElem>  ← Fixed to H2!
```

**Output:**
```
Fixing heading hierarchy...
  ⚠️ Fixing heading hierarchy: H1→H3 (skipped level), changing H3 to H2
  ⚠️ Fixing heading hierarchy: H1→H3 (skipped level), changing H3 to H2
  ✓ Fixed 2 heading hierarchy issues
```

### Example 3: First Heading Not H1

**Problem PDF:**
```xml
<StructElem><S>/H2</S><T>Introduction</T></StructElem>  ← Should be H1!
<StructElem><S>/H3</S><T>Background</T></StructElem>
```

**After Correction:**
```xml
<StructElem><S>/H1</S><T>Introduction</T></StructElem>  ← Fixed!
<StructElem><S>/H2</S><T>Background</T></StructElem>    ← Adjusted!
```

**Output:**
```
Fixing heading hierarchy...
  ⚠️ Fixing heading hierarchy: First heading is H2, changing to H1
  ✓ Fixed 1 heading hierarchy issues
```

---

## Technical Details

### New Methods Added

#### `_validate_tag_type(elem, content_type)`
Validates that structure element type matches expected content type.

**Parameters:**
- `elem`: Structure element to validate
- `content_type`: Expected type ('image', 'table', 'heading', etc.)

**Returns:** `True` if valid, `False` if mismatch

#### `_remove_incorrect_tag(elem)`
Removes incorrectly placed structure element from the structure tree.

**Parameters:**
- `elem`: Structure element to remove

**Returns:** `True` if successfully removed

#### `_fix_incorrect_tag_type(elem, correct_type, title, alt_text)`
Replaces incorrect structure element type with correct one in place.

**Parameters:**
- `elem`: Structure element with wrong type
- `correct_type`: Correct structure type (e.g., '/Figure')
- `title`: Optional title for element
- `alt_text`: Optional alt text for element

**Returns:** `True` if successfully fixed

#### `_fix_heading_hierarchy()`
Fixes incorrect heading hierarchy by reordering and filling gaps.

**Returns:** Number of heading issues fixed

#### `_validate_and_fix_tag_types()`
Validates all structure elements and fixes incorrect tag types.

**Returns:** Number of tag type corrections made

### Remediation Workflow

Tag correction is integrated into the standard workflow:

```python
def remediate(self, options):
    # ... existing steps ...

    # Step 9.6: Validate and fix incorrect tag types
    self._validate_and_fix_tag_types()

    # Step 9.7: Fix heading hierarchy issues
    self._fix_heading_hierarchy()

    # ... remaining steps ...
```

---

## Troubleshooting

### Issue: Tool doesn't fix obvious type mismatch

**Possible causes:**
1. Element title doesn't contain type hints
2. Structure element lacks `/T` (title) field
3. Type mismatch is ambiguous

**Solution:**
Check element structure:
```python
import pikepdf
pdf = pikepdf.open('test.pdf')
struct_tree = pdf.Root.StructTreeRoot
for elem in struct_tree.K:
    print(f"Type: {elem.get('/S')}, Title: {elem.get('/T')}")
```

### Issue: Heading hierarchy not corrected

**Possible causes:**
1. Headings not using standard `/H1`-`/H6` types
2. Custom heading types in `/RoleMap`
3. Headings in nested structure

**Solution:**
Verify heading structure:
```bash
# Look for headings in structure tree
python -c "import pikepdf; pdf=pikepdf.open('test.pdf');
[print(e.get('/S')) for e in pdf.Root.StructTreeRoot.K]"
```

### Issue: Corrections not saved to output

**Possible causes:**
1. Modifications applied but save failed
2. Using `--analyze-only` flag

**Solution:**
```bash
# Ensure not using analyze-only
python pdf_remediator.py input.pdf --no-analyze-only

# Check for save errors in output
python pdf_remediator.py input.pdf 2>errors.log
```

---

## Best Practices

### 1. Run on Already-Tagged PDFs

Test correction on professionally tagged PDFs to see what gets fixed:

```bash
python pdf_remediator.py manually_tagged.pdf
# Review output for corrections made
```

### 2. Review Correction Messages

Pay attention to what's being corrected:

```
✓ Corrections expected (good fixes)
⚠️ Unexpected corrections (verify these)
```

### 3. Validate with PAC 3

Always validate corrected PDFs:

```
1. Open corrected PDF in PAC 3
2. Run full accessibility check
3. Verify no structure errors remain
4. Test with screen readers
```

### 4. Manual Review for Complex Cases

Some fixes may need human judgment:

```
Automatic: Simple type mismatches
Manual: Complex nested structures
Manual: Custom structure types
Manual: Ambiguous content
```

---

## Limitations

### Current Capabilities

✓ Detects and fixes simple tag type mismatches
✓ Corrects heading hierarchy gaps
✓ Adjusts first heading to H1
✓ Validates against standard PDF structure types

### Current Limitations

❌ Cannot fix complex nested structures
❌ Cannot detect semantic incorrectness (content vs. type mismatch at meaning level)
❌ Relies on title field for type hints
❌ May not handle custom structure types in RoleMap

### Future Enhancements

Planned improvements for v2.4:

1. **Deep structure validation**
   - Validate parent-child relationships
   - Check /Pg references
   - Verify /K children arrays

2. **Content-based type detection**
   - Analyze actual page content
   - Match structure to content position
   - Don't rely solely on title hints

3. **Custom structure type support**
   - Handle /RoleMap custom types
   - Support namespace extensions
   - Validate against custom schemas

---

## Version History

### v2.3 - Tag Correction (Current - January 2025)
- **NEW**: Automatic tag type validation and correction
- **NEW**: Heading hierarchy fixing (skipped levels, wrong start level)
- **NEW**: Structure element type mismatch detection
- **NEW**: In-place tag type correction
- **ENHANCED**: More robust structure tree validation
- **ENHANCED**: Better error detection and reporting

### v2.2 - Tag-Aware Remediation (October 2025)
- Tag detection to prevent duplicates
- Quality validation for existing tags
- Skip properly tagged content

---

## Summary

The tag correction feature ensures PDFs are not just tagged, but **correctly tagged** according to PDF/UA standards:

✅ **Detects** incorrect tag types
✅ **Fixes** structure element mismatches
✅ **Corrects** heading hierarchy issues
✅ **Validates** structure tree integrity
✅ **Preserves** valid structure
✅ **Reports** all corrections made

**Key Principle:** *Structure tags must match content type for screen readers to work properly.*

---

## Support

- **Main Documentation**: See [README.md](README.md)
- **Tag Detection**: See [TAG_DETECTION_GUIDE.md](TAG_DETECTION_GUIDE.md)
- **Issues**: Report on GitHub

---

**Version**: 2.3.0
**Last Updated**: 2025-01-25
**Status**: Production Ready
