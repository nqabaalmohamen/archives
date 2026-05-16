import os
import re

path = 'templates/eams/document_list.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the eye link with download link
pattern = r'<a href="{{ doc\.file\.url }}" target="_blank" class="btn-icon" title=".*?"><i class="fas fa-eye"></i></a>'
replacement = '<a href="{% url \'document_download\' doc.pk %}" target="_blank" class="btn-icon" title="تحميل الملف"><i class="fas fa-download"></i></a>'

content = re.sub(pattern, replacement, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated document_list.html links")
