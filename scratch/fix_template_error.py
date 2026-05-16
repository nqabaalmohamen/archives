import os
import re

def fix_template(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix incorrect escaping in onclick - the error is due to \'{% url \'...\' ... %}\'
    # We want it to be '{% url '...' ... %}'
    
    # Pattern to find the problematic string
    pattern = r"onclick=\"return showDeleteModal\(\\\'{% url \\\'(.*?)\\\' (.*?) %}\\\'\)\\\""
    replacement = r"onclick=\"return showDeleteModal('{% url '\1' \2 %}')\""
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed Template: {path}")
    else:
        # Try a more literal match if regex fails
        literal_pattern = "\\\'{% url \\\'user_delete\\\' user.pk %}\\\'"
        if literal_pattern in content:
            new_content = content.replace(literal_pattern, "'{% url 'user_delete' user.pk %}'")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed Template (Literal): {path}")

fix_template('templates/eams/user_list.html')
fix_template('templates/eams/document_list.html')
