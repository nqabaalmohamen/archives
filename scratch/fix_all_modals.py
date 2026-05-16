import os

def fix_file(path, old_marker, new_content_snippet):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the delete link
        start_idx = content.find(old_marker)
        if start_idx != -1:
            # Find the end of the <a> tag
            end_idx = content.find('>', start_idx)
            if end_idx != -1:
                # We replace the whole attribute or just inject the onclick
                # Let's find the href specifically
                href_start = content.find('href=', start_idx)
                if href_start != -1 and href_start < end_idx:
                    # Replace href and add onclick
                    tag_content = content[start_idx:end_idx]
                    # This is getting complicated, let's just do a simple replacement of the whole tag if we can find it
                    pass
        
        # Simple string replacement for the specific part we know
        if old_marker in content:
            # Replace the href and remove the onclick confirm
            # We want to change href="{% url '...' %}" to href="#" onclick="return showDeleteModal('{% url '...' %}')"
            # And remove any existing onclick="return confirm(...)"
            
            # Since we have the marker, let's just target it
            parts = content.split(old_marker)
            # Find the onclick="return confirm" after the marker
            next_part = parts[1]
            confirm_start = next_part.find('onclick="return confirm')
            if confirm_start != -1:
                confirm_end = next_part.find(')"', confirm_start) + 2
                if confirm_end != -1:
                    # Remove it
                    next_part = next_part[:confirm_start] + next_part[confirm_end:]
            
            new_content = parts[0] + f'href="#" onclick="return showDeleteModal(\'{old_marker[6:-1]}\')"' + next_part
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {path}")

# Specifically for Category List
cat_path = 'templates/eams/category_list.html'
if os.path.exists(cat_path):
    with open(cat_path, 'r', encoding='utf-8') as f:
        c = f.read()
    # Target: <a href="{% url 'category_delete' cat.pk %}" class="btn-icon delete" title="حذف" onclick="return confirm('...')">
    # We want: <a href="#" class="btn-icon delete" title="حذف" onclick="return showDeleteModal('{% url 'category_delete' cat.pk %}')">
    import re
    new_c = re.sub(r'<a href="{% url \'category_delete\' cat.pk %}"[^>]*>', 
                   r'<a href="#" class="btn-icon delete" title="حذف" onclick="return showDeleteModal(\'{% url \'category_delete\' cat.pk %}\')\">', 
                   c)
    with open(cat_path, 'w', encoding='utf-8') as f:
        f.write(new_c)
    print("Fixed category_list.html")

# Specifically for User List
user_path = 'templates/eams/user_list.html'
if os.path.exists(user_path):
    with open(user_path, 'r', encoding='utf-8') as f:
        c = f.read()
    new_c = re.sub(r'<a href="{% url \'user_delete\' user.pk %}"[^>]*>', 
                   r'<a href="#" class="btn-icon delete" title="حذف" onclick="return showDeleteModal(\'{% url \'user_delete\' user.pk %}\')\">', 
                   c)
    with open(user_path, 'w', encoding='utf-8') as f:
        f.write(new_c)
    print("Fixed user_list.html")
