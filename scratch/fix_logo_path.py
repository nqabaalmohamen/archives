import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update the export view to include the absolute path of the logo
new_code = """
@login_required
def reports_export_pdf(request):
    from .models import Document, Category, AuditLog
    from django.db.models import Count, Q
    from django.contrib.auth.models import User
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    from weasyprint import HTML
    from django.conf import settings
    
    # Get filters
    category_id = request.GET.get('category')
    doc_type = request.GET.get('doc_type')
    user_id = request.GET.get('user_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_q = request.GET.get('q')
    
    docs = Document.objects.all()
    
    if category_id: docs = docs.filter(category_id=category_id)
    if doc_type: docs = docs.filter(doc_type=doc_type)
    if user_id: docs = docs.filter(uploaded_by_id=user_id)
    if search_q:
        docs = docs.filter(Q(title__icontains=search_q) | Q(reference_number__icontains=search_q))
    if start_date: docs = docs.filter(uploaded_at__date__gte=start_date)
    if end_date: docs = docs.filter(uploaded_at__date__lte=end_date)
    
    # Calculate Logo Path (Absolute)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
    logo_exists = os.path.exists(logo_path)
    
    context = {
        'documents': docs.order_by('-uploaded_at'),
        'total_docs': docs.count(),
        'incoming': docs.filter(doc_type='incoming').count(),
        'outgoing': docs.filter(doc_type='outgoing').count(),
        'internal': docs.filter(doc_type='internal').count(),
        'categories_stats': Category.objects.annotate(count=Count('documents', filter=Q(documents__in=docs))).order_by('-count'),
        'users_stats': User.objects.annotate(doc_count=Count('uploaded_documents', filter=Q(uploaded_documents__in=docs))).order_by('-doc_count')[:10],
        'logo_path': logo_path if logo_exists else None,
        'filters': {
            'category': Category.objects.get(id=category_id).name if category_id else 'كافة الأقسام',
            'type': dict(Document.TYPE_CHOICES).get(doc_type, 'كافة الأنواع') if doc_type else 'كافة الأنواع',
            'user': User.objects.get(id=user_id).username if user_id else 'كافة الموظفين',
            'start': start_date,
            'end': end_date
        }
    }
    
    html_string = render_to_string('eams/reports_final_pdf.html', context)
    # Important: pass base_url as the static directory for relative paths
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="archive_report.pdf"'
    return response
"""

import re
pattern = r"@login_required\s+def reports_export_pdf\(request\):.*?(?=@login_required|\Z)"
new_content = re.sub(pattern, new_code, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated views.py to handle absolute logo path for WeasyPrint")
