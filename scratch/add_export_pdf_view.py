import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

export_view = """
@login_required
def reports_export_pdf(request):
    from .models import Document, Category, AuditLog
    from django.db.models import Count, Q
    from django.contrib.auth.models import User
    
    # Get filters (same as reports_view)
    category_id = request.GET.get('category')
    doc_type = request.GET.get('doc_type')
    user_id = request.GET.get('user_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_q = request.GET.get('q')
    
    docs = Document.objects.all()
    logs = AuditLog.objects.all()
    
    if category_id: docs = docs.filter(category_id=category_id)
    if doc_type: docs = docs.filter(doc_type=doc_type)
    if user_id: 
        docs = docs.filter(uploaded_by_id=user_id)
        logs = logs.filter(user_id=user_id)
    if search_q:
        docs = docs.filter(Q(title__icontains=search_q) | Q(reference_number__icontains=search_q))
        logs = logs.filter(Q(document_title__icontains=search_q) | Q(details__icontains=search_q))
    if start_date: 
        docs = docs.filter(uploaded_at__date__gte=start_date)
        logs = logs.filter(timestamp__date__gte=start_date)
    if end_date: 
        docs = docs.filter(uploaded_at__date__lte=end_date)
        logs = logs.filter(timestamp__date__lte=end_date)
    
    context = {
        'total_docs': docs.count(),
        'incoming': docs.filter(doc_type='incoming').count(),
        'outgoing': docs.filter(doc_type='outgoing').count(),
        'internal': docs.filter(doc_type='internal').count(),
        'categories_stats': Category.objects.annotate(count=Count('documents', filter=Q(documents__in=docs))).order_by('-count'),
        'recent_logs': logs.order_by('-timestamp')[:100],
        'export_date': AuditLog.objects.first().timestamp if AuditLog.objects.exists() else None,
        'filters': {
            'category': Category.objects.get(id=category_id).name if category_id else 'كافة الأقسام',
            'type': dict(Document.TYPE_CHOICES).get(doc_type, 'كافة الأنواع') if doc_type else 'كافة الأنواع',
            'user': User.objects.get(id=user_id).username if user_id else 'كافة الموظفين',
            'start': start_date,
            'end': end_date
        }
    }
    return render(request, 'eams/reports_pdf.html', context)
"""

if "def reports_export_pdf" not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(export_view)
    print("Added reports_export_pdf view")
