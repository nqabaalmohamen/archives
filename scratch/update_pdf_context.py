import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update context to include 'documents' list
new_pdf_view = """
@login_required
def reports_export_pdf(request):
    from .models import Document, Category, AuditLog
    from django.db.models import Count, Q
    from django.contrib.auth.models import User
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    from weasyprint import HTML
    
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
    
    context = {
        'documents': docs.order_by('-uploaded_at'),
        'total_docs': docs.count(),
        'incoming': docs.filter(doc_type='incoming').count(),
        'outgoing': docs.filter(doc_type='outgoing').count(),
        'internal': docs.filter(doc_type='internal').count(),
        'categories_stats': Category.objects.annotate(count=Count('documents', filter=Q(documents__in=docs))).order_by('-count'),
        'filters': {
            'category': Category.objects.get(id=category_id).name if category_id else 'كافة الأقسام',
            'type': dict(Document.TYPE_CHOICES).get(doc_type, 'كافة الأنواع') if doc_type else 'كافة الأنواع',
            'user': User.objects.get(id=user_id).username if user_id else 'كافة الموظفين',
            'start': start_date,
            'end': end_date
        }
    }
    
    html_string = render_to_string('eams/reports_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="archive_report.pdf"'
    return response
"""

import re
pattern = r"@login_required\s+def reports_export_pdf\(request\):.*?(?=@login_required|\Z)"
new_content = re.sub(pattern, new_pdf_view, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated reports_export_pdf view to include full document list for the report")
