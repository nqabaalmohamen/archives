import os
import re

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add user_create view
user_create_view = """
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
                profile.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    action='edit',
                    document_title="إدارة المستخدمين",
                    details=f"تم إضافة مستخدم جديد: {username} ({full_name})"
                )
                messages.success(request, f"تم إضافة المستخدم {full_name} بنجاح")
                return redirect('user_list')
    
    return render(request, 'eams/user_form.html', {
        'roles': [('admin', 'مدير نظام'), ('employee', 'موظف'), ('viewer', 'مشاهد')]
    })
"""

# Append the new view if it doesn't exist
if 'def user_create' not in content:
    content += user_create_view

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Added user_create view to views.py")
