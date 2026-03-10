# GMS Tutorial: Word-to-Markdown Conversion Guide

Instructions for converting GMS tutorial Word documents (in `docs/word_docs/`) to markdown format for hosting on ReadTheDocs via MkDocs.

## Reference Example

See `docs/modflow/MODFLOW-GridApproach/index.md` as the completed reference for all conventions described below.

---

## Step 1: Initial Conversion

### Source Files
- Primary source: `.docx` file in `docs/word_docs/`
- The Word document is the authoritative source for all content and formatting

### Output Structure
Each tutorial gets its own folder under `docs/`:
```
docs/<category>/<TutorialName>/
    index.md
    images/
        figure1.png
        figure2.png
        ...
```

### Extracting Content
- Use the `python-docx` library to read the Word document programmatically
- Extract ALL text content — every paragraph, every table, every list item
- Do NOT skip sections, do NOT summarize, do NOT add content that isn't in the source

### Extracting Images (Figures)
- Extract images from the Word document and save to the `images/` subfolder
- Name them sequentially: `figure1.png`, `figure2.png`, etc.
- Crop images accurately — do not lose parts of figures
- If images extract poorly from `.docx`, check for a parallel `.pdf` file and extract from that instead

### Extracting Inline Icons
The Word documents contain small inline icons (tool buttons, view mode icons, arrows) embedded directly in the text next to the tool/button names. These must be extracted and placed in the markdown.

**How to identify icons vs figures:** Icons are inline images smaller than ~0.5 inches. Figures are larger images that appear on their own line.

**Extraction method using python-docx:**
```python
from docx import Document

doc = Document('path/to/file.docx')
extracted = {}

for para in doc.paragraphs:
    for run in para.runs:
        inlines = run._element.findall(
            './/{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'
        )
        for shape in inlines:
            extent = shape.find(
                '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent'
            )
            cx = int(extent.get('cx', 0)) / 914400  # EMU to inches
            cy = int(extent.get('cy', 0)) / 914400
            if cx < 0.5 and cy < 0.5:  # It's an icon
                blip = shape.find(
                    './/{http://schemas.openxmlformats.org/drawingml/2006/main}blip'
                )
                rId = blip.get(
                    '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
                )
                docPr = shape.find(
                    './/{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr'
                )
                descr = docPr.get('descr', '') if docPr is not None else ''
                if rId not in extracted:
                    blob = doc.part.rels[rId].target_part.blob
                    extracted[rId] = {'descr': descr, 'blob': blob}

# Save each unique icon
for rId, info in extracted.items():
    filename = f"icon_{rId}.png"  # rename to something meaningful
    with open(f"docs/icons/{filename}", 'wb') as f:
        f.write(info['blob'])
```

**Icon placement in markdown:** Icons go inline immediately after the tool/button name they represent:
```markdown
1. Turn on **Ortho Mode** ![alt text](../../icons/ortho_mode.png).
2. Switch to **Side View** ![alt text](../../icons/side_view.png).
3. Click **Display Options** ![alt text](../../icons/display_options.png) to bring up...
4. Using the **Select Cells** tool ![alt text](../../icons/select_cells.png) while holding...
```

**Shared icon library:** Icons are stored in `docs/icons/` and shared across all tutorials (referenced via relative path `../../icons/`). Many icons repeat across tutorials (e.g., Select Cells, Plan View, Ortho Mode). Before extracting, check if the icon already exists in `docs/icons/`.

**Naming conventions for icons:** Use descriptive lowercase names with underscores:
- `select_cells.png`, `ortho_mode.png`, `plan_view.png`, `side_view.png`
- `display_options.png`, `up_arrow.png`, `down_arrow.png`
- `3dgrid_module.png`, `dot_dot_dot.png`

The Word doc `descr` field gives hints (e.g., `"File:Select 3D Cell Tool.svg"`, `"up"`, `"down"`) but naming requires human judgment since descriptions are inconsistent.

---

## Step 2: Markdown Structure

### Page Header
```markdown
# Tutorial Title

*GMS 10.9 Tutorial*

Short one-line description

![alt text](images/figureN.png)

## Objectives

Brief description of what the tutorial covers.

| Prerequisite Tutorials | Required Components | Time |
|---|---|---|
| ... | ... | ... |

---
```

### Header Graphic
The Word documents have a main graphic/screenshot near the top of the tutorial (on the cover page or just before the introduction). This image is often difficult to extract automatically because it may be stored as a separate cover page element rather than an inline image. **You will likely need to manually capture or extract this image.** Check the PDF version of the tutorial — it is usually easier to grab the header graphic from there.

### Table of Contents
The Word documents contain a table of contents near the beginning. **Skip it entirely** — do not convert it to markdown. MkDocs generates its own TOC automatically from the section headings.

### Sections
- Use `## N Title` for main sections (numbered to match the Word doc)
- Use `### N.N Title` for subsections
- Add `---` horizontal rules between major sections

### Figures
```markdown
![Descriptive alt text](images/figureN.png)

*Figure N: Caption text*
```
- Always include the caption below the image in italics
- Always include descriptive alt text

### Tables
- Use standard markdown table syntax
- Preserve all table data exactly as in the Word document

---

## Step 3: Text Formatting (Bold and Italic)

This is critical. The Word documents use specific formatting conventions that must be preserved in markdown.

### How to Extract Formatting
Use `python-docx` to identify bold and italic runs:
```python
from docx import Document
doc = Document('path/to/file.docx')
for i, para in enumerate(doc.paragraphs):
    for run in para.runs:
        if run.bold:
            # This text should be **bold** in markdown
        if run.italic:
            # This text should be *italic* in markdown
```

### Formatting Conventions
These tutorials follow a consistent pattern for GMS UI elements:

- **Bold** (`**text**`) — Clickable items the user acts on:
  - Button labels: **OK**, **Cancel**, **Save**, **Close**, **Done**, **Add BC**, **Run Check**
  - Menu commands (the final/actionable item in a menu path): **Units...**, **Packages...**, **New MODFLOW...**, **Run MODFLOW**
  - Tool/mode names: **Ortho Mode**, **Select Cells**, **Plan View**, **Side View**, **Display Options**
  - Dialog button labels: **Constant &rarr; Layer...**, **Horizontal Hydraulic Conductivity...**

- *Italic* (`*text*`) — Names of things (not clicked directly):
  - Parent menu items in a path: *File*, *Edit*, *MODFLOW*, *Optional Packages*
  - Dialog names: *Units dialog*, *Layer Value dialog*, *MODFLOW Global/Basic Package dialog*
  - Field/column names: *Layer*, *Value*, *Zone budget ID*
  - UI labels and option names: *Starting heads equal grid top elevation*, *Read solution on exit*

### Menu Path Convention
Menu paths use italic for parent items, bold for the final command:
```markdown
Select *File* | **Save As...** to bring up the Save As dialog.
Select *MODFLOW* | *Optional Packages* | **RCH** -- **Recharge...** to bring up the MODFLOW Recharge Package dialog.
```

---

## Step 4: Numbered Lists and Interrupted Steps

### The Problem
GMS tutorials frequently have explanatory paragraphs between numbered steps. In standard markdown, a paragraph between list items resets the numbering.

### The Solution
The `sane_lists` extension is enabled in `mkdocs.yml`. This extension honors the actual numbers written in the markdown source. So when a paragraph interrupts a list, just continue with the correct number:

```markdown
1. First step

Some explanatory paragraph here.

2. Second step continues correctly because sane_lists honors the "2."
```

**Important:** Always write the actual intended number for each list item. Do NOT rely on auto-numbering. If steps go 1-7, write `1.`, `2.`, `3.`, `4.`, `5.`, `6.`, `7.` even if paragraphs interrupt the sequence.

---

## Step 5: Verification

After conversion, verify the markdown against the Word document:

1. **Complete content check** — Use `python-docx` to extract all paragraph text from the Word doc and confirm every paragraph has a match in the markdown. Watch for:
   - Missing sentences or paragraphs (especially near section transitions)
   - Extra text that doesn't belong (e.g., content from a different tutorial)
   - Steps that were combined or split incorrectly

2. **Formatting check** — Extract bold/italic runs from the Word doc and confirm the markdown matches:
   - Every bold word in the Word doc should be `**bold**` in markdown
   - Every italic word should be `*italic*` in markdown
   - Pay attention to the bold vs italic distinction for UI elements

3. **Numbering check** — Verify that numbered step sequences match the Word doc, especially where paragraphs interrupt the list

4. **Figure check** — Confirm all figures are present, correctly cropped, and have captions

5. **Table check** — Confirm all tables have correct data and structure

6. **Section structure check** — Verify sections and subsections match the Word doc's organization. Watch for steps that got placed in the wrong section.

---

## Step 6: MkDocs Integration

After converting a tutorial, add it to the navigation in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - MODFLOW:
    - Grid Approach: modflow/MODFLOW-GridApproach/index.md
    - New Tutorial: modflow/NewTutorial/index.md
```

---

## MkDocs Configuration Reference

The following extensions are enabled in `mkdocs.yml`:
- `attr_list` — Allows setting image width: `![alt](img.png){width=300}`
- `sane_lists` — Honors actual numbers in ordered lists
- `admonition` — Note/warning blocks
- `codehilite` — Code syntax highlighting
- `toc` — Table of contents with permalinks

---

## Common Pitfalls

1. **Missing text near section boundaries** — When converting, text at the end of one section or start of another can get lost. Always verify.
2. **Steps in wrong section** — The Word doc may have steps that visually follow a description but belong to a different logical section. Match the Word doc's structure.
3. **Image quality** — Extracting images from `.docx` can lose quality or crop incorrectly. Compare against the PDF version if available.
4. **Extraneous content** — Do not add text that isn't in the source document. No UGrid references in a Grid Approach tutorial, etc.
5. **Bold vs italic confusion** — The distinction matters for these tutorials. When in doubt, check the Word doc's run-level formatting.
6. **Em-dashes** — Use `--` for en-dashes in markdown (e.g., "35--55 minutes", "MODFLOW -- Grid Approach").
