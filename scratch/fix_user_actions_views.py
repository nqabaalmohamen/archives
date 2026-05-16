import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add user_update and user_detail views with correct syntax
user_views = """
@login_required
def user_update(request, pk):
    if not request.user.profile.role == 'admin':
        return redirect('dashboard')
    
    from django.contrib.auth.models import User
    from .models import Profile, AuditLog
    target_user = User.objects.get(pk=pk)
    profile = target_user.profile
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        job_title = request.POST.get('job_title')
        department = request.POST.get('department')
        password = request.POST.get('password')
        role = request.POST.get('role', profile.role)
        
        # Granular Perms
        profile.can_access_documents = request.POST.get('can_access_documents') == 'on'
        profile.can_access_reports = request.POST.get('can_access_reports') == 'on'
        profile.can_access_categories = request.POST.get('can_access_categories') == 'on'
        profile.can_access_audit_log = request.POST.get('can_access_audit_log') == 'on'
        profile.can_manage_users = request.POST.get('can_manage_users') == 'on'
        
        profile.full_name = full_name
        profile.job_title = job_title
        profile.department = department
        profile.role = role
        
        if password:
            target_user.set_password(password)
            target_user.save()
            
        profile.save()
        
        AuditLog.objects.create(
            user=request.user,
            action='edit',
            document_title="إدارة المستخدمين",
            details=f"تم تحديث بيانات المستخدم: {target_user.username}"
        )
        messages.success(request, f"تم تحديث بيانات {full_name} بنجاح")
        return redirect('user_list')
    
    return render(request, 'eams/user_form.html', {'target_user': target_user, 'profile': profile, 'is_edit': True})

@login_required
def user_detail(request, pk):
    if not request.user.profile.role == 'admin':
        return redirect('dashboard')
    
    from django.contrib.auth.models import User
    target_user = User.objects.get(pk=pk)
    return render(request, 'eams/user_detail.html', {'target_user': target_user})
"""

# Append the new view if it doesn't exist
if 'def user_update' not in content:
    content += user_views
else:
    # Overwrite the existing one to fix typo
    content = re.sub(r"@login_required\s+def user_update\(request, pk\):.*?return render\(request, 'eams/user_detail\.html'.*?\)", user_views, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated user_update and user_detail views to views.py")
