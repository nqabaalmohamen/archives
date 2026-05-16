import os

path = 'templates/eams/reports.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_js = """
<script>
    function submitExportForm() {
        // Sync filter values to hidden inputs in export form
        const filters = {
            'category': document.querySelector('select[name="category"]').value,
            'doc_type': document.querySelector('select[name="doc_type"]').value,
            'user_id': document.querySelector('select[name="user_id"]').value,
            'start_date': document.querySelector('input[name="start_date"]').value,
            'end_date': document.querySelector('input[name="end_date"]').value,
            'q': document.querySelector('input[name="q"]').value
        };
        
        for (const [key, value] of Object.entries(filters)) {
            const hiddenInput = document.getElementById('hidden_' + key);
            if (hiddenInput) hiddenInput.value = value;
        }
        
        document.getElementById('pdfExportForm').submit();
    }
</script>
"""

# Replace the old script or append
if 'function exportPDF' in content:
    import re
    # Find the old script block and replace it
    pattern = r"<script>\s+function exportPDF.*?</script>"
    new_content = re.sub(pattern, new_js, content, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated JS function in reports.html")
else:
    print("Old JS function not found")
