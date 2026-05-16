import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update user_create to handle granular permissions
new_user_create = """
@login_required
def user_create(request):
    if not request.user.profile.role == 'admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        job_title = request.POST.get('job_title')
        department = request.POST.get('department')
        password = request.POST.get('password')
        role = request.POST.get('role', 'viewer')
        
        # Granular Perms
        can_access_documents = request.POST.get('can_access_documents') == 'on'
        can_access_reports = request.POST.get('can_access_reports') == 'on'
        can_access_categories = request.POST.get('can_access_categories') == 'on'
        can_access_audit_log = request.POST.get('can_access_audit_log') == 'on'
        can_manage_users = request.POST.get('can_manage_users') == 'on'
        
        if username and password:
            from django.contrib.auth.models import User
            from .models import Profile, AuditLog
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "اسم المستخدم موجود مسبقاً")
            else:
                user = User.objects.create_user(username=username, password=password)
                profile = Profile.objects.get(user=user)
                profile.full_name = full_name
                profile.job_title = job_title
                profile.department = department
                profile.role = role
                profile.can_access_documents = can_access_documents
                profile.can_access_reports = can_access_reports
                profile.can_access_categories = can_access_categories
                profile.can_access_audit_log = can_access_audit_log
                profile.can_manage_users = can_manage_users
                profile.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    action='edit',
                    document_title="إدارة المستخدمين",
                    details=f"تم إضافة مستخدم جديد بصلاحيات مخصصة: {username}"
                )
                messages.success(request, f"تم إضافة المستخدم {full_name} بنجاح")
                return redirect('user_list')
    
    return render(request, 'eams/user_form.html')
"""

# Replace the old user_create with the new one
content = re.sub(r"@login_required\s+def user_create\(request\):.*?return render\(request, 'eams/user_form\.html'.*?\)", new_user_create, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated user_create view in views.py")
