#!/usr/bin/env python3

from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import os
import re

def convert_docx_to_markdown_proper(docx_path, output_md_path, output_image_dir):
    """Convert Word document to markdown preserving actual structure and image placement."""
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
    
    # Load the Word document
    doc = Document(docx_path)
    
    # Extract images first and get their mapping
    image_mapping = extract_images_from_docx(doc, output_image_dir)
    
    # Extract content with proper structure preservation
    markdown_content = extract_structured_content(doc, image_mapping)
    
    # Write to file
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Converted {docx_path} to {output_md_path}")
    print(f"Images directory: {output_image_dir}")

def extract_images_from_docx(doc, output_image_dir):
    """Extract images from the Word document and return mapping."""
    image_mapping = {}
    image_count = 0
    
    # Extract images from the document
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_count += 1
            try:
                # Get image data
                image_data = rel.target_part.blob
                
                # Determine file extension
                ext = os.path.splitext(rel.target_ref)[1]
                if not ext:
                    ext = '.png'  # Default to PNG
                
                # Save image
                image_filename = f"image_{image_count:02d}{ext}"
                image_path = os.path.join(output_image_dir, image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                # Store mapping for later reference
                image_mapping[image_count] = image_filename
                print(f"Extracted image: {image_filename}")
                
            except Exception as e:
                print(f"Failed to extract image {image_count}: {e}")
    
    if image_count == 0:
        print("No images found in the Word document")
    else:
        print(f"Extracted {image_count} images")
    
    return image_mapping

def extract_structured_content(doc, image_mapping):
    """Extract content preserving the actual document structure."""
    content = []
    
    # Add title
    content.append("# GMS Tutorials: MODFLOW – Grid Approach")
    content.append("")
    
    # Process the document in order
    for element in doc.element.body:
        if isinstance(element, CT_P):
            # This is a paragraph
            para = Paragraph(element, doc)
            if para.text.strip():
                # Check if this paragraph should have an image
                if is_figure_caption(para.text):
                    # Insert image before the caption
                    image_num = get_figure_number(para.text)
                    if image_num and image_num <= len(image_mapping):
                        content.append(f"![Figure {image_num}](images/{image_mapping[image_num]})")
                        content.append("")
                
                # Add the paragraph text
                content.append(para.text.strip())
                content.append("")
                
        elif isinstance(element, CT_Tbl):
            # This is a table - skip for now but could handle later
            continue
    
    return '\n'.join(content)

def is_figure_caption(text):
    """Check if text is a figure caption."""
    # Look for figure references
    figure_patterns = [
        r'^Figure \d+',
        r'^Figure \d+\s+[A-Z]',
        r'^Figure \d+\s*$'
    ]
    
    for pattern in figure_patterns:
        if re.match(pattern, text.strip()):
            return True
    
    return False

def get_figure_number(text):
    """Extract figure number from text."""
    match = re.search(r'Figure (\d+)', text)
    if match:
        return int(match.group(1))
    return None

if __name__ == "__main__":
    # Convert the Word document
    convert_docx_to_markdown_proper(
        'docs/word_docs/MODFLOW-GridApproach.docx',
        'docs/modflow/grid/MODFLOW-GridApproach.md',
        'docs/modflow/grid/images'
    )
