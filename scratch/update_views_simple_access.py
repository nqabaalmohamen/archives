import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update views to handle simplified section access
new_views = """
@login_required
def user_create(request):
    if not request.user.profile.access_users:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        job_title = request.POST.get('job_title')
        department = request.POST.get('department')
        password = request.POST.get('password')
        
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
                
                # Archive Sections
                profile.access_incoming = request.POST.get('access_incoming') == 'on'
                profile.access_outgoing = request.POST.get('access_outgoing') == 'on'
                profile.access_internal = request.POST.get('access_internal') == 'on'
                
                # Settings Sections
                profile.access_reports = request.POST.get('access_reports') == 'on'
                profile.access_categories = request.POST.get('access_categories') == 'on'
                profile.access_audit = request.POST.get('access_audit') == 'on'
                profile.access_users = request.POST.get('access_users') == 'on'
                
                profile.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    action='edit',
                    document_title="إدارة المستخدمين",
                    details=f"تم إضافة مستخدم جديد بصلاحيات وصول للأقسام: {username}"
                )
                messages.success(request, f"تم إضافة المستخدم {full_name} بنجاح")
                return redirect('user_list')
    
    return render(request, 'eams/user_form.html')

@login_required
def user_update(request, pk):
    if not request.user.profile.access_users:
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
        
        # Archive Sections
        profile.access_incoming = request.POST.get('access_incoming') == 'on'
        profile.access_outgoing = request.POST.get('access_outgoing') == 'on'
        profile.access_internal = request.POST.get('access_internal') == 'on'
        
        # Settings Sections
        profile.access_reports = request.POST.get('access_reports') == 'on'
        profile.access_categories = request.POST.get('access_categories') == 'on'
        profile.access_audit = request.POST.get('access_audit') == 'on'
        profile.access_users = request.POST.get('access_users') == 'on'
        
        profile.full_name = full_name
        profile.job_title = job_title
        profile.department = department
        
        if password:
            target_user.set_password(password)
            target_user.save()
            
        profile.save()
        
        AuditLog.objects.create(
            user=request.user,
            action='edit',
            document_title="إدارة المستخدمين",
            details=f"تم تحديث صلاحيات الوصول للمستخدم: {target_user.username}"
        )
        messages.success(request, f"تم تحديث بيانات {full_name} بنجاح")
        return redirect('user_list')
    
    return render(request, 'eams/user_form.html', {'target_user': target_user, 'profile': profile, 'is_edit': True})
"""

# Replace old views
content = re.sub(r"@login_required\s+def user_create\(request\):.*?return render\(request, 'eams/user_form\.html'\)", new_views.split('@login_required\ndef user_update')[0].strip(), content, flags=re.DOTALL)
content = re.sub(r"@login_required\s+def user_update\(request, pk\):.*?return render\(request, 'eams/user_form\.html', \{'target_user': target_user, 'profile': profile, 'is_edit': True\}\)", "@login_required" + new_views.split('@login_required')[2], content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated views with simplified section access logic.")
