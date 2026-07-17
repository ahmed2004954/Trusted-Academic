import os

templates_dir = r"C:\Users\h7304\Desktop\trust acadmy\templates"

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                relpath = os.path.relpath(filepath, templates_dir)
                if 'extends "base.html"' in content or "extends 'base.html'" in content:
                    print(f"OLD: {relpath}")
                elif 'extends "base_identity.html"' in content or "extends 'base_identity.html'" in content:
                    print(f"IDENTITY: {relpath}")
                else:
                    print(f"OTHER: {relpath}")
            except Exception as e:
                print(f"ERROR reading {file}: {e}")
