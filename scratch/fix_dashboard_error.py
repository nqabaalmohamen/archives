import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the dashboard view Category annotation
# It should use 'documents' instead of 'uploaded_documents'
old_line = "Category.objects.annotate(doc_count=Count('uploaded_documents'))"
new_line = "Category.objects.annotate(doc_count=Count('documents'))"

if old_line in content:
    new_content = content.replace(old_line, new_line)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed dashboard view field name")
else:
    print("Snippet not found in dashboard view")
