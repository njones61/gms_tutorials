#!/usr/bin/env python3

import re

def cleanup_markdown(input_file, output_file):
    """Clean up the markdown formatting issues."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicate figure text (e.g., "Figure 4 Figure 1 Sample problem to be solved")
    content = re.sub(r'\*\*Figure \d+\*\* Figure \d+\s+', r'', content)
    
    # Clean up figure captions that are just "Figure X" without description
    content = re.sub(r'\*\*Figure \d+\*\* Figure \d+\s*$', '', content, flags=re.MULTILINE)
    
    # Remove standalone "Figure X" lines that don't have descriptions
    content = re.sub(r'^Figure \d+\s+[A-Za-z\s]+$', '', content, flags=re.MULTILINE)
    
    # Clean up excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix spacing around image tags
    content = re.sub(r'\n!\[([^\]]+)\]\(([^)]+)\)\n\n', r'\n\n![\1](\2)\n\n', content)
    
    # Clean up any remaining formatting issues
    content = re.sub(r'\*\*Figure \d+\*\*\s*\n', r'', content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Markdown cleanup completed!")

if __name__ == "__main__":
    cleanup_markdown(
        'docs/modflow/grid/MODFLOW-GridApproach.md',
        'docs/modflow/grid/MODFLOW-GridApproach_clean.md'
    )
