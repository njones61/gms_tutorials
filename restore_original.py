#!/usr/bin/env python3

from pymupdf4llm import to_markdown

def convert_pdf():
    """Convert PDF to markdown using PyMuPDF4LLM."""
    
    # Convert PDF to markdown with images
    markdown_content = to_markdown(
        'docs/modflow/grid/MODFLOW-GridApproach.pdf',
        write_images=True,
        image_path='docs/modflow/grid/images',
        image_format='png',
        show_progress=True
    )
    
    # Write the markdown content
    with open('docs/modflow/grid/MODFLOW-GridApproach.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("Original PyMuPDF4LLM conversion restored!")

if __name__ == "__main__":
    convert_pdf()
