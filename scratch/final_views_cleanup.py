import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Remove all "Dynamic Title Logic" blocks from the wrong views
# We will identify views by their names and only keep the logic in reports views.

def clean_view(content, view_name):
    pattern = rf"def {view_name}\(request.*?\):(.*?)return render"
    match = re.search(pattern, content, re.DOTALL)
    if not match: return content
    
    body = match.group(1)
    if "# Dynamic Title Logic" in body:
        # Remove the logic block and the bad context entries
        body = re.sub(r'# Dynamic Title Logic.*?context = \{', 'context = {', body, flags=re.DOTALL)
        body = body.replace("'report_title': report_title,", "")
        body = body.replace("'documents': docs.order_by('-uploaded_at'),", "")
        # Restore it in the main content
        content = content[:match.start(1)] + body + content[match.end(1):]
    return content

# Clean up views that don't need this logic
content = clean_view(content, 'dashboard')
content = clean_view(content, 'document_list')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Properly cleaned up views.py from accidental variable injections")
