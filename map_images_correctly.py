#!/usr/bin/env python3

import re

def map_images_correctly(input_file, output_file):
    """Map the actual extracted images to their correct figure references."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Based on the document analysis, here's the correct mapping:
    # Figure 1 -> image1.png (extracted as image 16)
    # Figure 2 -> image2.png (extracted as image 13) 
    # Figure 3 -> image3.png (extracted as image 6)
    # Figure 4 -> image4.png (extracted as image 21)
    # Figure 5 -> image5.wmf (extracted as image 14)
    # Figure 6 -> image6.png (extracted as image 3)
    # Figure 7 -> image7.jpeg (extracted as image 17)
    # Figure 8 -> image8.png (extracted as image 10)
    # Figure 9 -> image9.png (extracted as image 7)
    # Figure 10 -> image10.png (extracted as image 22)
    # Figure 11 -> image11.png (extracted as image 1)
    # Figure 12 -> image12.png (extracted as image 18)
    # Figure 13 -> image13.png (extracted as image 11)
    # Figure 14 -> image14.png (extracted as image 5)
    # Figure 15 -> image15.png (extracted as image 19)
    # Figure 16 -> image16.png (extracted as image 15)
    # Figure 17 -> image17.png (extracted as image 8)
    # Figure 18 -> image18.png (extracted as image 23)
    # Figure 19 -> image19.png (extracted as image 4)
    # Figure 20 -> image20.png (extracted as image 20)
    # Figure 21 -> image21.png (extracted as image 12)
    # Figure 22 -> image22.png (extracted as image 9)
    # Figure 23 -> image23.png (extracted as image 24)
    # Figure 24 -> image24.png (extracted as image 2)
    
    # Create the mapping dictionary
    figure_to_image = {
        1: "image1.png",
        2: "image2.png", 
        3: "image3.png",
        4: "image4.png",
        5: "image5.wmf",
        6: "image6.png",
        7: "image7.jpeg",
        8: "image8.png",
        9: "image9.png",
        10: "image10.png",
        11: "image11.png",
        12: "image12.png",
        13: "image13.png",
        14: "image14.png",
        15: "image15.png",
        16: "image16.png",
        17: "image17.png",
        18: "image18.png",
        19: "image19.png",
        20: "image20.png",
        21: "image21.png",
        22: "image22.png",
        23: "image23.png",
        24: "image24.png"
    }
    
    # Find all figure references and insert images above them
    figure_pattern = r'(Figure \d+\s+[^\n]+)'
    
    def insert_image_before_figure(match):
        figure_text = match.group(1)
        # Extract figure number
        figure_match = re.search(r'Figure (\d+)', figure_text)
        if figure_match:
            figure_num = int(figure_match.group(1))
            if figure_num in figure_to_image:
                image_name = figure_to_image[figure_num]
                return f"![Figure {figure_num}](images/{image_name})\n\n{figure_text}"
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
            if figure_num in figure_to_image:
                image_name = figure_to_image[figure_num]
                return f"![Figure {figure_num}](images/{image_name})\n\n{figure_text}"
        return figure_text
    
    content = re.sub(standalone_pattern, insert_image_before_standalone, content, flags=re.MULTILINE)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Images mapped correctly to figure references!")

if __name__ == "__main__":
    map_images_correctly(
        'docs/modflow/grid/MODFLOW-GridApproach.md',
        'docs/modflow/grid/MODFLOW-GridApproach_with_correct_images.md'
    )
