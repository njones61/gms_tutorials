#!/usr/bin/env python3

from docx import Document
import os
import re

def convert_docx_to_markdown_correct(docx_path, output_md_path, output_image_dir):
    """Convert Word document to markdown with correct image mapping."""
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
    
    # Load the Word document
    doc = Document(docx_path)
    
    # Extract images first and get their actual names
    image_mapping = extract_images_from_docx(doc, output_image_dir)
    
    # Extract text content in order
    markdown_content = extract_text_content(doc)
    
    # Write to file
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Converted {docx_path} to {output_md_path}")
    print(f"Images directory: {output_image_dir}")
    print("Note: Images have been extracted with their original names.")
    print("You will need to manually place them in the markdown where they belong.")

def extract_images_from_docx(doc, output_image_dir):
    """Extract images from the Word document with their original names."""
    image_mapping = {}
    image_count = 0
    
    # Extract images from the document
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_count += 1
            try:
                # Get image data
                image_data = rel.target_part.blob
                
                # Get the original filename from the relationship
                original_name = os.path.basename(rel.target_ref)
                
                # Save image with original name
                image_path = os.path.join(output_image_dir, original_name)
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                # Store mapping
                image_mapping[image_count] = original_name
                print(f"Extracted image {image_count}: {original_name}")
                
            except Exception as e:
                print(f"Failed to extract image {image_count}: {e}")
    
    if image_count == 0:
        print("No images found in the Word document")
    else:
        print(f"Extracted {image_count} images")
    
    return image_mapping

def extract_text_content(doc):
    """Extract text content preserving paragraph order."""
    content = []
    
    # Add title
    content.append("# GMS Tutorials: MODFLOW – Grid Approach")
    content.append("")
    
    # Extract paragraphs in order
    for para in doc.paragraphs:
        if para.text.strip():
            content.append(para.text.strip())
            content.append("")
    
    return '\n'.join(content)

if __name__ == "__main__":
    # Convert the Word document
    convert_docx_to_markdown_correct(
        'docs/word_docs/MODFLOW-GridApproach.docx',
        'docs/modflow/grid/MODFLOW-GridApproach.md',
        'docs/modflow/grid/images'
    )
