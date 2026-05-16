import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update user_create and user_update to handle full CRUD matrix
new_views = """
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
                
                # Documents
                profile.can_view_docs = request.POST.get('can_view_docs') == 'on'
                profile.can_add_docs = request.POST.get('can_add_docs') == 'on'
                profile.can_edit_docs = request.POST.get('can_edit_docs') == 'on'
                profile.can_delete_docs = request.POST.get('can_delete_docs') == 'on'
                
                # Categories
                profile.can_view_cats = request.POST.get('can_view_cats') == 'on'
                profile.can_add_cats = request.POST.get('can_add_cats') == 'on'
                profile.can_edit_cats = request.POST.get('can_edit_cats') == 'on'
                profile.can_delete_cats = request.POST.get('can_delete_cats') == 'on'
                
                # Users
                profile.can_view_users = request.POST.get('can_view_users') == 'on'
                profile.can_add_users = request.POST.get('can_add_users') == 'on'
                profile.can_edit_users = request.POST.get('can_edit_users') == 'on'
                profile.can_delete_users = request.POST.get('can_delete_users') == 'on'
                
                # Others
                profile.can_view_reports = request.POST.get('can_view_reports') == 'on'
                profile.can_view_audit_log = request.POST.get('can_view_audit_log') == 'on'
                
                profile.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    action='edit',
                    document_title="إدارة المستخدمين",
                    details=f"تم إضافة مستخدم جديد بصلاحيات CRUD كاملة: {username}"
                )
                messages.success(request, f"تم إضافة المستخدم {full_name} بنجاح")
                return redirect('user_list')
    
    return render(request, 'eams/user_form.html')

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
        
        # Documents
        profile.can_view_docs = request.POST.get('can_view_docs') == 'on'
        profile.can_add_docs = request.POST.get('can_add_docs') == 'on'
        profile.can_edit_docs = request.POST.get('can_edit_docs') == 'on'
        profile.can_delete_docs = request.POST.get('can_delete_docs') == 'on'
        
        # Categories
        profile.can_view_cats = request.POST.get('can_view_cats') == 'on'
        profile.can_add_cats = request.POST.get('can_add_cats') == 'on'
        profile.can_edit_cats = request.POST.get('can_edit_cats') == 'on'
        profile.can_delete_cats = request.POST.get('can_delete_cats') == 'on'
        
        # Users
        profile.can_view_users = request.POST.get('can_view_users') == 'on'
        profile.can_add_users = request.POST.get('can_add_users') == 'on'
        profile.can_edit_users = request.POST.get('can_edit_users') == 'on'
        profile.can_delete_users = request.POST.get('can_delete_users') == 'on'
        
        # Others
        profile.can_view_reports = request.POST.get('can_view_reports') == 'on'
        profile.can_view_audit_log = request.POST.get('can_view_audit_log') == 'on'
        
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
            details=f"تم تحديث صلاحيات CRUD للمستخدم: {target_user.username}"
        )
        messages.success(request, f"تم تحديث بيانات {full_name} بنجاح")
        return redirect('user_list')
    
    return render(request, 'eams/user_form.html', {'target_user': target_user, 'profile': profile, 'is_edit': True})
"""

# Replace user_create and user_update
content = re.sub(r"@login_required\s+def user_create\(request\):.*?return render\(request, 'eams/user_form\.html'\)", new_views.split('@login_required\ndef user_update')[0].strip(), content, flags=re.DOTALL)
content = re.sub(r"@login_required\s+def user_update\(request, pk\):.*?return render\(request, 'eams/user_form\.html', \{'target_user': target_user, 'profile': profile, 'is_edit': True\}\)", "@login_required" + new_views.split('@login_required')[2], content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated views with CRUD permission logic.")
