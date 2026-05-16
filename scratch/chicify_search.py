import os
import re

def chicify_file(path, search_pattern, replacement):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(search_pattern, replacement, content, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Chicified {path}")

# Chicify the Search Bar in all pages
search_pattern = r'<div style=\"display: flex; align-items: center; gap: 10px; background: #fff; border: 1.5px solid var\(--border-color\); border-radius: 14px; padding: 10px 18px; box-shadow: 0 2px 8px rgba\(0,0,0,0.05\);\">'
chic_search = r'<div class="search-chic" style="display: flex; align-items: center; gap: 15px; background: #fff; border: 2px solid #e5e7eb; border-radius: 20px; padding: 12px 25px; box-shadow: 0 10px 25px rgba(0,0,0,0.03); transition: all 0.3s;">'

chicify_file('templates/eams/document_list.html', search_pattern, chic_search)
chicify_file('templates/eams/reports.html', search_pattern, chic_search)
chicify_file('templates/eams/user_list.html', search_pattern, chic_search)
chicify_file('templates/eams/audit_log.html', search_pattern, chic_search)
