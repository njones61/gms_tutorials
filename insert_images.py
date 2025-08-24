#!/usr/bin/env python3

import re

def insert_images_in_markdown(input_file, output_file):
    """Insert images at the correct locations based on figure references."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all figure references and insert images above them
    # Pattern: "Figure X" followed by description
    figure_pattern = r'(Figure \d+\s+[^\n]+)'
    
    def insert_image_before_figure(match):
        figure_text = match.group(1)
        # Extract figure number
        figure_match = re.search(r'Figure (\d+)', figure_text)
        if figure_match:
            figure_num = int(figure_match.group(1))
            # Insert image above the figure text
            return f"![Figure {figure_num}](images/image_{figure_num:02d}.png)\n\n{figure_text}"
        return figure_text
    
    # Insert images before figure references
    content = re.sub(figure_pattern, insert_image_before_figure, content)
    
    # Also handle standalone "Figure X" lines
    standalone_pattern = r'^(Figure \d+)\s*$'
    
    def insert_image_before_standalone(match):
        figure_text = match.group(1)
        figure_match = re.search(r'Figure (\d+)', figure_text)
        if figure_match:
            figure_num = int(figure_match.group(1))
            return f"![Figure {figure_num}](images/image_{figure_num:02d}.png)\n\n{figure_text}"
        return figure_text
    
    content = re.sub(standalone_pattern, insert_image_before_standalone, content, flags=re.MULTILINE)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Images inserted at figure references!")

if __name__ == "__main__":
    insert_images_in_markdown(
        'docs/modflow/grid/MODFLOW-GridApproach.md',
        'docs/modflow/grid/MODFLOW-GridApproach_with_images.md'
    )
