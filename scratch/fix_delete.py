import sys
import os

file_path = 'eams/views.py'
if not os.path.exists(file_path):
    print("File not found")
    sys.exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_func = """@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.user.profile.role == 'admin' or doc.uploaded_by == request.user:
        doc_title = doc.title
        doc.delete()
        from eams.models import AuditLog
        AuditLog.objects.create(user=request.user, action='delete', document_title=doc_title, details=f"تم حذف الوثيقة: {doc_title}")
        from django.contrib import messages
        messages.success(request, "تم حذف الوثيقة بنجاح")
    else:
        from django.contrib import messages
        messages.error(request, "ليس لديك صلاحية لحذف هذه الوثيقة")
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'document_list'
    return redirect(next_url)
"""

start_marker = "def document_delete(request, pk):"
start_idx = content.find(start_marker)

if start_idx != -1:
    decorator_idx = content.rfind('@login_required', 0, start_idx)
    if decorator_idx != -1:
        # Replace from decorator to end of file
        new_content = content[:decorator_idx] + new_func
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated views.py")
    else:
        print("Decorator not found")
else:
    print("Function not found")
