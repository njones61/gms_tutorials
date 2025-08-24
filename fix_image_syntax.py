#!/usr/bin/env python3

import re

def fix_image_syntax(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert <img src="..."> tags to standard markdown ![alt](src) format
    content = re.sub(r'<img src="([^"]+)"[^>]*>', r'![](\1)', content)
    
    # Remove problematic image references that have broken URLs in alt text
    content = re.sub(r'!\[http://[^\]]+\]\(([^)]+)\)', r'![](\1)', content)
    
    # Remove very small/corrupted images (image19.png and image22.png are only ~380 bytes)
    content = re.sub(r'!\[[^\]]*\]\(images/media/image19\.png\)', '', content)
    content = re.sub(r'!\[[^\]]*\]\(images/media/image22\.png\)', '', content)
    
    # Convert .wmf files to .png (we'll need to handle this separately)
    content = re.sub(r'images/media/image5\.wmf', 'images/media/image5.png', content)
    
    # Standardize all image references to use consistent markdown syntax
    # Remove any remaining HTML-like syntax
    content = re.sub(r'<[^>]+>', '', content)
    
    # Write the fixed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed image syntax in {output_file}")

if __name__ == "__main__":
    fix_image_syntax('docs/modflow/grid/MODFLOW-GridApproach.md', 'docs/modflow/grid/MODFLOW-GridApproach_fixed.md')
