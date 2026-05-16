import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace general admin role checks with access_users
# or other appropriate permissions
replacements = [
    (r"request\.user\.profile\.role\s*==\s*'admin'", "request.user.profile.access_users"),
    (r"request\.user\.profile\.role\s*!=\s*'admin'", "not request.user.profile.access_users"),
    (r"not\s+request\.user\.profile\.role\s*==\s*'admin'", "not request.user.profile.access_users"),
]

for old, new in replacements:
    content = re.sub(old, new, content)

# Remove the unused user_update_role function if it's still there
content = re.sub(r"@login_required\s+def user_update_role\(request, pk\):.*?return redirect\('user_list'\)", "", content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced all .role checks with new permissions.")
