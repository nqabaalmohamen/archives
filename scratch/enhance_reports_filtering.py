import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_reports_view = """
@login_required
def reports_view(request):
    from .models import Document, Category, AuditLog
    from django.db.models import Count, Q
    from django.contrib.auth.models import User
    
    # Get filters
    category_id = request.GET.get('category')
    doc_type = request.GET.get('doc_type')
    user_id = request.GET.get('user_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_q = request.GET.get('q')
    
    # Base Querysets
    docs = Document.objects.all()
    logs = AuditLog.objects.all()
    
    # Apply filters
    if category_id:
        docs = docs.filter(category_id=category_id)
    if doc_type:
        docs = docs.filter(doc_type=doc_type)
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
    
    # Recalculate Stats based on filters
    total_docs = docs.count()
    incoming_count = docs.filter(doc_type='incoming').count()
    outgoing_count = docs.filter(doc_type='outgoing').count()
    internal_count = docs.filter(doc_type='internal').count()
    
    # Category Distribution
    categories_stats = Category.objects.annotate(
        count=Count('documents', filter=Q(documents__in=docs))
    ).order_by('-count')
    
    # User Activity Stats
    users_stats = User.objects.annotate(
        doc_count=Count('uploaded_documents', filter=Q(uploaded_documents__in=docs))
    ).order_by('-doc_count')[:10]
    
    # Recent Logs
    recent_logs = logs.order_by('-timestamp')[:50]
    
    context = {
        'total_docs': total_docs,
        'incoming': incoming_count,
        'outgoing': outgoing_count,
        'internal': internal_count,
        'categories_stats': categories_stats,
        'users_stats': users_stats,
        'recent_logs': recent_logs,
        'categories': Category.objects.all(),
        'users': User.objects.all(),
        'doc_types': Document.TYPE_CHOICES,
        'selected_category': category_id,
        'selected_type': doc_type,
        'selected_user': user_id,
        'start_date': start_date,
        'end_date': end_date,
        'q': search_q,
    }
    return render(request, 'eams/reports.html', context)
"""

import re
pattern = r"@login_required\s+def reports_view\(request\):.*?(?=@login_required|\Z)"
new_content = re.sub(pattern, new_reports_view, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Enhanced reports_view with more precise filtering")
