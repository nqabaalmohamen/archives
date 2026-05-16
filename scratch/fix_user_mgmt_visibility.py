import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix user_management view to use access_users permission
new_user_mgmt = """
@login_required
def user_management(request):
    if not request.user.profile.access_users:
        messages.error(request, "ليس لديك صلاحية الوصول لإدارة المستخدمين")
        return redirect('dashboard')
    
    from django.db.models import Q
    from django.contrib.auth.models import User
    
    query = request.GET.get('q')
    users = User.objects.all().select_related('profile')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(profile__full_name__icontains=query) |
            Q(profile__job_title__icontains=query)
        )
    return render(request, 'eams/user_list.html', {'users': users})
"""

# Replace the old user_management
pattern = r"@login_required\s+def user_management\(request\):.*?return render\(request, 'eams/user_list\.html', \{'users': users\}\)"
content = re.sub(pattern, new_user_mgmt.strip(), content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed user_management view to use new permissions.")
