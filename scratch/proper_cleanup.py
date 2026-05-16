import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the specific garbage pattern at the end
# It looks like:
# return render(request, 'eams/user_form.html')
# , ('employee', '...'), ('viewer', '...')]
pattern = r"return render\(request, 'eams/user_form\.html'\)\s*,\s*\('employee', '.*?'\), \('viewer', '.*?'\)\]"
new_content = re.sub(pattern, "return render(request, 'eams/user_form.html')", content, flags=re.DOTALL)

# Also check for any other trailing garbage
new_content = new_content.strip()

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Properly cleaned views.py")
