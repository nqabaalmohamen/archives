import os
import re

def fix_all_templates():
    template_dir = 'templates/eams/'
    if not os.path.exists(template_dir):
        return
    
    files = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    
    for filename in files:
        path = os.path.join(template_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # General fix for escaped single quotes in Django tags within JS calls
        # Look for things like showDeleteModal(\'{% url \'name\' pk %}\')
        pattern = r"showDeleteModal\(\\\'{% url \\\'(.*?)\\\' (.*?) %}\\\'\)"
        replacement = r"showDeleteModal('{% url '\1' \2 %}')"
        
        new_content = re.sub(pattern, replacement, content)
        
        # Also fix literal instances just in case
        new_content = new_content.replace("\\\'{%", "{%").replace("%}\\\'", "%}")
        new_content = new_content.replace("\\\'", "'")
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed Template: {path}")

fix_all_templates()
