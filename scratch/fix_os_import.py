import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import os to the top if not present, or just fix the function
if 'import os' not in content:
    content = 'import os\n' + content

# Also ensure it is inside the function if preferred for robustness
content = content.replace('def reports_export_pdf(request):', 'def reports_export_pdf(request):\n    import os')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed NameError by importing os in views.py")
