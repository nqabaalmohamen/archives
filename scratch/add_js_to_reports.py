import os

path = 'templates/eams/reports.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

js_code = """
<script>
    function exportPDF() {
        const params = new URLSearchParams(window.location.search);
        const exportUrl = "{% url 'reports_export_pdf' %}?" + params.toString();
        window.open(exportUrl, '_blank');
    }
</script>
"""

if 'function exportPDF' not in content:
    idx = content.rfind('{% endblock %}')
    if idx != -1:
        new_content = content[:idx] + js_code + content[idx:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Updated reports.html with JS function")
