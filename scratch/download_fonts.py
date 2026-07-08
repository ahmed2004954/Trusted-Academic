import urllib.request
import re
import os

# Target folder in workspace
workspace_static_fonts = r"static/fonts/ibm-plex-sans-arabic"
os.makedirs(workspace_static_fonts, exist_ok=True)

url = "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Fetching Google Fonts CSS...")
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as response:
    css_content = response.read().decode('utf-8')

# RegEx to capture the comment, subset name, and the body of @font-face
# E.g. /* arabic */
# @font-face { ... }
pattern = re.compile(r'(/\*\s*([a-z\-]+)\s*\*/\s*@font-face\s*\{([^}]+)\})', re.DOTALL)

matches = pattern.findall(css_content)
print(f"Found {len(matches)} font face declarations.")

generated_css = []

for full_block, subset, body in matches:
    # Extract weight
    weight_match = re.search(r'font-weight:\s*(\d+);', body)
    weight = weight_match.group(1) if weight_match else "400"
    
    # Extract style
    style_match = re.search(r'font-style:\s*([a-z\-]+);', body)
    style = style_match.group(1) if style_match else "normal"
    
    # Extract URL
    url_match = re.search(r'src:\s*url\((https://[^)]+)\)', body)
    if not url_match:
        print(f"Could not find URL in block for weight {weight}, subset {subset}")
        continue
    
    font_url = url_match.group(1)
    
    # Extract unicode-range
    ur_match = re.search(r'unicode-range:\s*([^;]+);', body)
    unicode_range = ur_match.group(1) if ur_match else ""
    
    # Check if subset is relevant (e.g. arabic, latin, latin-ext)
    if subset not in ['arabic', 'latin', 'latin-ext']:
        continue
        
    filename = f"ibm-plex-sans-arabic-{weight}-{subset}.woff2"
    filepath = os.path.join(workspace_static_fonts, filename)
    
    # Download file if it doesn't exist
    if not os.path.exists(filepath):
        print(f"Downloading {filename} from {font_url}...")
        try:
            req_font = urllib.request.Request(font_url, headers=headers)
            with urllib.request.urlopen(req_font) as font_response:
                with open(filepath, 'wb') as out_file:
                    out_file.write(font_response.read())
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            continue
    else:
        print(f"File {filename} already exists, skipping download.")
        
    # Generate CSS
    # Path relative to static/css/main.css is ../fonts/ibm-plex-sans-arabic/filename
    local_src = f"url('../fonts/ibm-plex-sans-arabic/{filename}') format('woff2')"
    
    local_css_block = f"""/* {subset} */
@font-face {{
  font-family: 'IBM Plex Sans Arabic';
  font-style: {style};
  font-weight: {weight};
  font-display: swap;
  src: {local_src};
  unicode-range: {unicode_range};
}}"""
    generated_css.append(local_css_block)

output_css_path = os.path.join(workspace_static_fonts, "generated_font_faces.css")
with open(output_css_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(generated_css))

print(f"\nFont downloading finished. Local CSS rules written to {output_css_path}")
