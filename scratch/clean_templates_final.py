import os
import re

def clean_template(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the trailing backslash issue: onclick="..."\ -> onclick="..."
    # and showDeleteModal('...')\ -> showDeleteModal('...')
    
    # Remove any backslashes before quotes or parentheses at the end of onclick
    new_content = re.sub(r"onclick=\"(.*?)\\\"", r'onclick="\1"', content)
    new_content = re.sub(r"showDeleteModal\('(.*?)'\)\\", r"showDeleteModal('\1')", new_content)
    
    # General cleanup of any escaped single quotes that might have been left
    new_content = new_content.replace("\\'", "'")
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned Template: {path}")

# Run on all templates in eams
template_dir = 'templates/eams/'
for f in os.listdir(template_dir):
    if f.endswith('.html'):
        clean_template(os.path.join(template_dir, f))
