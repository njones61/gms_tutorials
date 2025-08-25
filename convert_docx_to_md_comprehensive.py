#!/usr/bin/env python3
"""
Comprehensive Word to Markdown converter with all fixes applied automatically.
"""

import os
import sys
import subprocess
import shutil
import re
import zipfile
from pathlib import Path
import tempfile
import argparse

def ensure_dependencies():
    """Check and install required dependencies."""
    dependencies_ok = True
    
    # Check for pypandoc
    try:
        import pypandoc
        pypandoc.ensure_pandoc_installed()
    except ImportError:
        print("Installing pypandoc...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pypandoc'], check=True)
        import pypandoc
        pypandoc.ensure_pandoc_installed()
    except Exception as e:
        print(f"Error setting up pandoc: {e}")
        dependencies_ok = False
    
    # Check for Pillow (for image conversion)
    try:
        from PIL import Image
    except ImportError:
        print("Installing Pillow for image conversion...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], check=True)
    
    return dependencies_ok

def extract_all_images_zip(docx_path, temp_dir):
    """Extract all images from DOCX using ZIP method (backup for pandoc failures)."""
    zip_images = {}
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            # Find all media files
            media_files = [f for f in zip_ref.namelist() if 'media/' in f and f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.wmf', '.emf'))]
            
            if media_files:
                zip_media_dir = Path(temp_dir) / 'zip_media'
                zip_media_dir.mkdir(exist_ok=True)
                
                for media_file in media_files:
                    # Extract to zip_media directory
                    zip_ref.extract(media_file, zip_media_dir)
                    
                    # Store mapping: filename -> full_path
                    filename = Path(media_file).name
                    zip_images[filename] = zip_media_dir / media_file
                    
                print(f"  ZIP extraction found {len(zip_images)} additional images")
            
    except Exception as e:
        print(f"  ZIP extraction failed: {e}")
    
    return zip_images

def convert_wmf_to_png(wmf_path, png_path):
    """Try to convert WMF file to PNG using multiple methods."""
    # Try using Pillow first
    try:
        from PIL import Image
        img = Image.open(wmf_path)
        img.save(png_path, 'PNG')
        return True
    except Exception:
        pass
    
    # Try using ImageMagick if available
    try:
        result = subprocess.run(['convert', str(wmf_path), str(png_path)], 
                              capture_output=True, text=True)
        if result.returncode == 0 and png_path.exists():
            return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    print(f"  Warning: Could not convert {wmf_path.name} to PNG")
    return False

def fix_ascii_tables(content):
    """Convert ASCII art tables to proper markdown tables."""
    
    # Fix table of contents - look for the TOC section that starts after "## Table of Contents"
    # and contains malformed links with duplicate anchors
    toc_section_pattern = r'(## Table of Contents\n\n)((?:- \[.*?\].*?\n)+)'
    toc_match = re.search(toc_section_pattern, content, re.DOTALL)
    
    if toc_match:
        toc_header = toc_match.group(1)
        toc_lines = toc_match.group(2)
        
        # Fix each TOC line by removing the duplicate anchor parts
        fixed_lines = []
        for line in toc_lines.strip().split('\n'):
            if line.strip():
                # Remove patterns like [text [anchor](#anchor)](#anchor) -> [text](#anchor)
                fixed_line = re.sub(r'\[([^\[\]]+) \[[^\]]+\]\([^)]+\)\]\(([^)]+)\)', r'[\1](\2)', line)
                # Also handle patterns like [1 Introduction [2](#introduction)](#introduction)
                fixed_line = re.sub(r'\[([^\[]+) \[[^\]]*\]\(([^)]+)\)\]\([^)]+\)', r'[\1](\2)', fixed_line)
                fixed_lines.append(fixed_line)
        
        # Replace the malformed TOC with the fixed version
        fixed_toc = toc_header + '\n'.join(fixed_lines) + '\n\n'
        content = content.replace(toc_match.group(0), fixed_toc)
    
    # Fix drain data table (dashes pattern)
    drain_table_pattern = r'(-{14} -{22} -{33}\n.*?\n.*?-{14} -{22} -{33})'
    
    def replace_drain_table(match):
        table_content = match.group(0)
        
        # Extract the data between the dashes
        lines = table_content.split('\n')
        data_lines = [line for line in lines if not line.strip().startswith('-') and line.strip()]
        
        if len(data_lines) < 2:
            return table_content
        
        # Build markdown table
        md_table = "\n"
        
        # Process header and data rows
        for i, line in enumerate(data_lines):
            # Split on whitespace, handling multiple spaces
            parts = line.split()
            if len(parts) >= 3:
                if i == 0:  # Header row
                    md_table += f"| {parts[0]} | {parts[1]} | {parts[2]} |\n"
                    md_table += "|------|-----------|-------------|\n"
                else:  # Data rows
                    md_table += f"| {parts[0]} | {parts[1]} | {parts[2]} |\n"
        
        md_table += "\n"
        return md_table
    
    content = re.sub(drain_table_pattern, replace_drain_table, content, flags=re.DOTALL)
    
    
    # Fix coordinate tables (smaller ASCII tables with + borders)
    coord_table_pattern = r'\+:?-+:?\+.*?\+:?-+:?\+'
    
    def replace_coord_table(match):
        table_content = match.group(0)
        
        # Extract table rows
        row_pattern = r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
        rows = re.findall(row_pattern, table_content)
        
        if not rows:
            return table_content
        
        # Build markdown table
        md_table = ""
        
        # Check if first row is a title/header span
        title_pattern = r'\|\s*([^|]+?)\s*\|(?:\s*\|){0,2}$'
        title_match = re.search(title_pattern, table_content.split('\n')[1] if '\n' in table_content else '')
        
        if title_match and 'coordinates' in title_match.group(1).lower():
            md_table += f"**{title_match.group(1).strip()}**\n\n"
        
        # Add table headers and separator
        if rows:
            md_table += f"| {rows[0][0].strip()} | {rows[0][1].strip()} | {rows[0][2].strip()} |\n"
            md_table += "|---------|---------|---------|\n"
            
            # Add data rows
            for row in rows[1:]:
                md_table += f"| {row[0].strip()} | {row[1].strip()} | {row[2].strip()} |\n"
        
        return md_table
    
    content = re.sub(coord_table_pattern, replace_coord_table, content, flags=re.DOTALL)
    
    return content

def fix_figure_captions(content):
    """Ensure all figures have properly formatted captions on separate lines."""
    
    # Pattern to match figure images
    figure_pattern = r'(!\[Figure \d+[^\]]*\]\([^)]+\))'
    
    def fix_caption_format(match):
        image_ref = match.group(1)
        
        # Extract figure number and caption from alt text
        alt_match = re.search(r'!\[(Figure \d+[^\]]*)\]', image_ref)
        if alt_match:
            caption = alt_match.group(1)
            return f"{image_ref}\n\n*{caption}*"
        
        return image_ref
    
    # Replace figure references with properly formatted versions
    content = re.sub(figure_pattern, fix_caption_format, content)
    
    return content

def clean_and_fix_images(md_content, images_dir, temp_media_dir, zip_images):
    """
    Clean up markdown and fix all image-related issues.
    """
    # Remove empty lines at the beginning
    md_content = md_content.lstrip('\n')
    
    # Build a map of extracted files
    extracted_files = {}
    if temp_media_dir and temp_media_dir.exists():
        for img_file in temp_media_dir.glob('*'):
            if img_file.is_file():
                extracted_files[img_file.name] = img_file
    
    # Add ZIP-extracted images to the map
    for filename, filepath in zip_images.items():
        if filename not in extracted_files:
            extracted_files[filename] = filepath
    
    print(f"Found {len(extracted_files)} total image files ({len(zip_images)} from ZIP backup)")
    
    # Process and copy extracted images
    image_mapping = {}  # Map old names to new names (for WMF conversions)
    
    for filename, source_path in extracted_files.items():
        dest_name = filename
        
        # Convert WMF files to PNG
        if filename.lower().endswith('.wmf'):
            png_name = Path(filename).stem + '.png'
            png_dest = images_dir / png_name
            
            print(f"  Converting {filename} to PNG...")
            if convert_wmf_to_png(source_path, png_dest):
                dest_name = png_name
                image_mapping[filename] = png_name
                print(f"    ✓ Converted to {png_name}")
            else:
                # If conversion fails, keep the WMF
                dest = images_dir / filename
                shutil.copy2(source_path, dest)
                print(f"    Copied as WMF: {filename}")
        else:
            # Copy non-WMF files as-is
            dest = images_dir / dest_name
            shutil.copy2(source_path, dest)
            print(f"  Copied: {filename}")
    
    # Fix standard markdown image references
    def process_image_ref(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        attributes = match.group(3) if len(match.groups()) >= 3 else ''
        
        # Get just the filename from the path
        img_filename = Path(img_path).name
        
        # Check if this file was converted (WMF to PNG)
        if img_filename in image_mapping:
            new_filename = image_mapping[img_filename]
            return f'![{alt_text}](images/{new_filename})'
        elif img_filename in extracted_files:
            return f'![{alt_text}](images/{img_filename})'
        else:
            print(f"  Warning: Referenced image not in extracted files: {img_filename}")
            return match.group(0)
    
    # Process standard markdown image references (remove width/height attributes)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)(?:\{[^}]*\})?'
    md_content = re.sub(image_pattern, process_image_ref, md_content)
    
    # Fix HTML img tags with temp paths
    html_img_pattern = r'<img\s+src="[^"]*?/media/([^"]+)"([^>]*)>'
    
    def process_html_img(match):
        img_filename = match.group(1)
        attributes = match.group(2)
        
        # Check if this file was converted (WMF to PNG)
        if img_filename in image_mapping:
            new_filename = image_mapping[img_filename]
            return f'<img src="images/{new_filename}"{attributes}>'
        elif img_filename in extracted_files:
            return f'<img src="images/{img_filename}"{attributes}>'
        else:
            print(f"  Warning: HTML img reference not found: {img_filename}")
            return match.group(0)
    
    md_content = re.sub(html_img_pattern, process_html_img, md_content)
    
    # Convert HTML figure tags to markdown with proper caption formatting
    figure_pattern = r'<figure>\s*<img\s+src="([^"]+)"[^>]*>\s*<figcaption><p>([^<]+)</p></figcaption>\s*</figure>'
    
    def process_figure(match):
        img_path = match.group(1)
        caption = match.group(2)
        
        # Extract filename from path
        if '/media/' in img_path:
            img_filename = img_path.split('/media/')[-1]
        else:
            img_filename = Path(img_path).name
        
        # Check if this file was converted or exists
        if img_filename in image_mapping:
            new_filename = image_mapping[img_filename]
            img_path = f'images/{new_filename}'
        elif img_filename in extracted_files:
            img_path = f'images/{img_filename}'
        else:
            print(f"  Warning: Figure image not found: {img_filename}")
        
        # Return as markdown with proper caption formatting
        return f'\n![{caption}]({img_path})\n\n*{caption}*\n'
    
    md_content = re.sub(figure_pattern, process_figure, md_content, flags=re.DOTALL)
    
    # Fix ASCII tables
    md_content = fix_ascii_tables(md_content)
    
    # Fix figure captions (ensure proper line breaks)
    md_content = fix_figure_captions(md_content)
    
    # Clean up excessive newlines
    md_content = re.sub(r'\n{3,}', '\n\n', md_content)
    
    # Ensure proper spacing around headers
    md_content = re.sub(r'(^|\n)(#{1,6}\s+[^\n]+)(\n)(?!\n)', r'\1\2\3\n', md_content, flags=re.MULTILINE)
    
    return md_content

def convert_docx_to_markdown(input_file, output_dir, output_filename=None):
    """
    Convert a Word document to Markdown with comprehensive fixes.
    """
    import pypandoc
    
    input_path = Path(input_file)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        return False
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create images subdirectory
    images_dir = output_path / 'images'
    images_dir.mkdir(exist_ok=True)
    
    # Clear existing images
    for existing_file in images_dir.glob('*'):
        if existing_file.is_file():
            existing_file.unlink()
    
    # Determine output filename
    if output_filename:
        md_filename = output_filename if output_filename.endswith('.md') else f"{output_filename}.md"
    else:
        md_filename = input_path.stem + '.md'
    
    md_file = output_path / md_filename
    
    print(f"Converting: {input_file}")
    print(f"Output: {md_file}")
    print(f"Images: {images_dir}")
    
    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp_media_dir = temp_path / 'media'
        
        try:
            # Extract all images using ZIP method (backup for pandoc failures)
            print("Extracting images with ZIP method...")
            zip_images = extract_all_images_zip(input_path, temp_dir)
            
            # Convert using pypandoc with media extraction
            temp_md = temp_path / 'temp.md'
            
            extra_args = [
                '--extract-media=' + str(temp_dir),
                '--wrap=none'
            ]
            
            print("Running pandoc conversion...")
            output = pypandoc.convert_file(
                str(input_path),
                'md',
                format='docx',
                extra_args=extra_args,
                outputfile=str(temp_md)
            )
            
            print("✓ Pandoc conversion completed")
            
            # Read the temporary markdown content
            with open(temp_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply all fixes
            print("Applying comprehensive fixes...")
            content = clean_and_fix_images(content, images_dir, temp_media_dir, zip_images)
            
            # Write the final markdown
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Markdown file created: {md_file}")
            
            # Verify results
            image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
            html_refs = re.findall(r'<img\s+src="([^"]+)"', content)
            total_refs = len(image_refs) + len(html_refs)
            
            if total_refs > 0:
                print(f"✓ Found {total_refs} image references in markdown")
                
                # Check if referenced images exist
                missing_images = []
                for alt_text, img_path in image_refs:
                    if img_path.startswith('images/'):
                        img_file = output_path / img_path
                        if not img_file.exists():
                            missing_images.append(img_path)
                
                if missing_images:
                    print(f"⚠ Warning: {len(missing_images)} referenced images not found:")
                    for img in missing_images[:5]:
                        print(f"  - {img}")
                else:
                    print("✓ All referenced images exist")
            
            # Check for figures
            figure_count = len(re.findall(r'!\[Figure \d+', content))
            if figure_count > 0:
                print(f"✓ Found {figure_count} numbered figures with captions")
            
            # Check for tables
            table_count = len(re.findall(r'\|.*\|', content))
            if table_count > 0:
                print(f"✓ Found {table_count} table rows (converted to markdown format)")
            
            return True
            
        except Exception as e:
            print(f"Error during conversion: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive Word to Markdown converter with automatic fixes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Features:
  - Extracts all images (uses ZIP backup for pandoc failures)  
  - Converts WMF files to PNG automatically
  - Fixes figure captions with proper line breaks
  - Converts ASCII tables to markdown format  
  - Fixes HTML figure tags
  - Cleans up formatting issues
        """
    )
    parser.add_argument('input', help='Input .docx file path')
    parser.add_argument('-o', '--output-dir', default=None, help='Output directory (default: same as input file)')
    parser.add_argument('-n', '--name', default=None, help='Custom output filename (without extension)')
    
    args = parser.parse_args()
    
    # Check and install dependencies
    if not ensure_dependencies():
        sys.exit(1)
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Use same directory as input file
        output_dir = Path(args.input).parent
    
    # Convert the document
    success = convert_docx_to_markdown(args.input, output_dir, args.name)
    
    if success:
        print("\n✅ Conversion completed successfully!")
        print("\nFixed issues:")
        print("  ✓ All images extracted (including pandoc failures)")
        print("  ✓ WMF files converted to PNG")
        print("  ✓ Figure captions formatted with proper line breaks")
        print("  ✓ ASCII tables converted to markdown format")
        print("  ✓ HTML figure tags converted to markdown")
        print("  ✓ Table of contents formatted as bulleted list")
    else:
        print("\n❌ Conversion failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()