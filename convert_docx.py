#!/usr/bin/env python3

from docx import Document
from markdownify import markdownify as md
import os
import re
import shutil

def convert_docx_to_markdown(docx_path, output_md_path, output_image_dir):
    """Convert Word document to markdown with better formatting and image handling."""
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
    
    # Load the Word document
    doc = Document(docx_path)
    
    # Extract images first
    extract_images_from_docx(doc, output_image_dir)
    
    # Extract text and convert to markdown
    paragraphs = []
    
    # Add title
    paragraphs.append("# GMS Tutorials: MODFLOW – Grid Approach")
    paragraphs.append("")
    
    for para in doc.paragraphs:
        if para.text.strip():
            # Convert to markdown
            markdown_text = md(para.text)
            paragraphs.append(markdown_text)
    
    # Join paragraphs with proper spacing
    markdown_content = '\n\n'.join(paragraphs)
    
    # Clean up the markdown
    markdown_content = clean_markdown(markdown_content)
    
    # Write to file
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Converted {docx_path} to {output_md_path}")
    print(f"Images directory: {output_image_dir}")

def extract_images_from_docx(doc, output_image_dir):
    """Extract images from the Word document."""
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
                
                print(f"Extracted image: {image_filename}")
                
            except Exception as e:
                print(f"Failed to extract image {image_count}: {e}")
    
    if image_count == 0:
        print("No images found in the Word document")
    else:
        print(f"Extracted {image_count} images")

def clean_markdown(content):
    """Clean up the markdown content."""
    # Remove excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix common formatting issues
    content = content.replace('** **', '**')  # Fix empty bold tags
    content = content.replace('* *', '*')     # Fix empty italic tags
    
    # Clean up figure references
    content = re.sub(r'Figure (\d+)', r'**Figure \1**', content)
    
    return content

if __name__ == "__main__":
    # Convert the Word document
    convert_docx_to_markdown(
        'docs/word_docs/MODFLOW-GridApproach.docx',
        'docs/modflow/grid/MODFLOW-GridApproach.md',
        'docs/modflow/grid/images'
    )
