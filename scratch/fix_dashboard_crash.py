import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the accidental injection from dashboard
# It's after 'activities = AuditLog...' and before 'context = {'
pattern_to_remove = r"# Dynamic Title Logic.*?context = \{"
# But we need to be careful not to remove it from the reports views.
# Let's target the dashboard specifically.

# Finding dashboard view
dash_start = content.find('def dashboard(request):')
dash_end = content.find('return render(request, \'eams/dashboard.html\', context)')

if dash_start != -1 and dash_end != -1:
    dash_code = content[dash_start:dash_end]
    # Remove the bad part
    dash_code = re.sub(r'# Dynamic Title Logic.*?context = \{', 'context = {', dash_code, flags=re.DOTALL)
    # Also remove 'report_title': report_title, and 'documents': docs... from the context if they were added
    dash_code = dash_code.replace("'report_title': report_title,", "")
    dash_code = dash_code.replace("'documents': docs.order_by('-uploaded_at'),", "")
    
    content = content[:dash_start] + dash_code + content[dash_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned up dashboard view and removed accidental variable injections")
