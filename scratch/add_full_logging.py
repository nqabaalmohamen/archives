import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add document_download view and Login/Logout signals
new_views = """
@login_required
def document_download(request, pk):
    from .models import Document, AuditLog
    from django.shortcuts import get_object_or_404
    from django.http import FileResponse
    
    doc = get_object_or_404(Document, pk=pk)
    
    # Log the download action
    AuditLog.objects.create(
        user=request.user,
        action='view',
        document_title=doc.title,
        details=f"تم تحميل الملف برقم مرجعي: {doc.reference_number}"
    )
    
    return FileResponse(doc.file, as_attachment=True)

# Add signals for Login/Logout logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    from eams.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action='view',
        document_title="النظام",
        details="تسجيل دخول إلى النظام"
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    from eams.models import AuditLog
    if user:
        AuditLog.objects.create(
            user=user,
            action='view',
            document_title="النظام",
            details="تسجيل خروج من النظام"
        )
"""

content += new_views

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Added document_download view and Login/Logout tracking to views.py")
