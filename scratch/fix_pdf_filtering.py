import os

path = 'templates/eams/reports.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add IDs to main filter inputs to avoid conflict with hidden inputs
content = content.replace('name="category"', 'name="category" id="main_category"')
content = content.replace('name="doc_type"', 'name="doc_type" id="main_doc_type"')
content = content.replace('name="user_id"', 'name="user_id" id="main_user_id"')
content = content.replace('name="start_date"', 'name="start_date" id="main_start_date"')
content = content.replace('name="end_date"', 'name="end_date" id="main_end_date"')
content = content.replace('name="q"', 'name="q" id="main_q"')

# Fix 2: Update JS to use these new IDs
new_js = """
<script>
    function submitExportForm() {
        // Sync filter values from main form to hidden export form
        document.getElementById('hidden_category').value = document.getElementById('main_category').value;
        document.getElementById('hidden_doc_type').value = document.getElementById('main_doc_type').value;
        document.getElementById('hidden_user_id').value = document.getElementById('main_user_id').value;
        document.getElementById('hidden_start_date').value = document.getElementById('main_start_date').value;
        document.getElementById('hidden_end_date').value = document.getElementById('main_end_date').value;
        document.getElementById('hidden_q').value = document.getElementById('main_q').value;
        
        // Submit the hidden form
        document.getElementById('pdfExportForm').submit();
    }
</script>
"""

import re
pattern = r"<script>\s+function submitExportForm.*?/script>"
content = re.sub(pattern, new_js, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed filter sync bug by adding unique IDs to main inputs and updating JS")
