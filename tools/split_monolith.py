import os
import re

INDEX_PATH = 'frontend/index.html'
CSS_PATH = 'frontend/css/legacy.css'
JS_PATH = 'frontend/js/app.js'
NEW_INDEX_PATH = 'frontend/index.html'

def split_monolith():
    print(f"Reading {INDEX_PATH}...")
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract CSS
    css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if css_match:
        css_content = css_match.group(1).strip()
        os.makedirs(os.path.dirname(CSS_PATH), exist_ok=True)
        with open(CSS_PATH, 'w', encoding='utf-8') as f:
            f.write(css_content)
        print(f"Extracted {len(css_content)} chars of CSS to {CSS_PATH}")
    else:
        print("No CSS found!")

    # Extract JS
    # Look for the main script block at the end
    # We'll use a regex that finds the last script tag content, assuming it's the main app logic
    # Or better, find specifically the block starting with "let backendConfig = null;" or similar unique string
    # Given the previous context, let's look for the script tag after the library imports
    
    # Strategy: Find the start of our custom script
    script_start_marker = '<script>'
    # Find all script tags
    script_pattern = re.compile(r'<script>(.*?)</script>', re.DOTALL)
    scripts = list(script_pattern.finditer(content))
    
    if scripts:
        # The last script tag is likely our main app logic based on file structure
        main_script_match = scripts[-1]
        js_content = main_script_match.group(1).strip()
        
        # Verify it's the right one (contains 'backendConfig')
        if 'backendConfig' in js_content:
            os.makedirs(os.path.dirname(JS_PATH), exist_ok=True)
            with open(JS_PATH, 'w', encoding='utf-8') as f:
                f.write(js_content)
            print(f"Extracted {len(js_content)} chars of JS to {JS_PATH}")
        else:
            print("Warning: Last script tag didn't contain 'backendConfig'. dumping anyway.")
            with open(JS_PATH, 'w', encoding='utf-8') as f:
                f.write(js_content)
    else:
        print("No JS found!")

    # Create new HTML
    # Remove the style block
    new_html = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="css/style.css">\n    <link rel="stylesheet" href="css/legacy.css">', content, flags=re.DOTALL)
    
    # Remove the main script block
    # We need to be careful not to remove library scripts
    if scripts:
        last_script = scripts[-1]
        start, end = last_script.span()
        # Replace the *content* of the last script tag with src attribute
        # Actually easier to just replace the whole tag
        # Construct the replacement
        script_tag_replacement = '<script src="js/app.js"></script>'
        new_html = new_html[:start] + script_tag_replacement + new_html[end:]

    with open(NEW_INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Wrote updated HTML to {NEW_INDEX_PATH}")

if __name__ == '__main__':
    split_monolith()
