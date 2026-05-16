import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the reports_view function
old_code = "doc_count=Count('documents')"
new_code = "doc_count=Count('uploaded_documents')"

if old_code in content:
    new_content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed reports_view field name")
else:
    print("Code snippet not found or already fixed")
