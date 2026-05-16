import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix document_create: Remove reference_number from POST and creation
pattern = r'def document_create\(request\):.*?if request\.method == \'POST\':(.*?)return render'
match = re.search(pattern, content, re.DOTALL)

if match:
    body = match.group(1)
    # Remove reference_number line
    body = re.sub(r'reference_number = request\.POST\.get\(\'reference_number\'\)', '', body)
    # Remove reference_number from create call
    body = re.sub(r'reference_number=reference_number,', '', body)
    # Update success message to show reference number
    body = re.sub(r'messages\.success\(request, ".*?"\)', 'messages.success(request, f"تمت أرشفة الوثيقة بنجاح! رقم الأرشفة: {doc.reference_number}")', body)
    
    new_view = content[:match.start(1)] + body + content[match.end(1):]
    content = new_view

# Also check for document_update
pattern_upd = r'def document_update\(request, pk\):.*?if request\.method == \'POST\':(.*?)return render'
match_upd = re.search(pattern_upd, content, re.DOTALL)
if match_upd:
    body_upd = match_upd.group(1)
    body_upd = re.sub(r'doc\.reference_number = request\.POST\.get\(\'reference_number\'\)', '', body_upd)
    content = content[:match_upd.start(1)] + body_upd + content[match_upd.end(1):]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed document_create and document_update to handle reference_number automatically")
