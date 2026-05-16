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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base Querysets
    docs = Document.objects.all()
    logs = AuditLog.objects.all()
    
    # Apply filters
    if category_id:
        docs = docs.filter(category_id=category_id)
        # Note: Logs don't have category directly, but we can filter by doc title if needed
        # For now, let's keep logs general or filter them if the user asks
    
    if start_date:
        docs = docs.filter(uploaded_at__date__gte=start_date)
        logs = logs.filter(timestamp__date__gte=start_date)
    
    if end_date:
        docs = docs.filter(uploaded_at__date__lte=end_date)
        logs = logs.filter(timestamp__date__lte=end_date)
    
    # Recalculate Stats based on filters
    total_docs = docs.count()
    incoming = docs.filter(doc_type='incoming').count()
    outgoing = docs.filter(doc_type='outgoing').count()
    internal = docs.filter(doc_type='internal').count()
    
    # Category Distribution (always show all categories but with filtered counts)
    # If a category filter is active, we show only that one or highlighting it
    categories_stats = Category.objects.annotate(
        count=Count('documents', filter=Q(documents__in=docs))
    ).order_by('-count')
    
    # User Activity Stats
    users_stats = User.objects.annotate(
        doc_count=Count('uploaded_documents', filter=Q(uploaded_documents__in=docs))
    ).order_by('-doc_count')[:10]
    
    # Recent Logs
    recent_logs = logs.order_by('-timestamp')[:20]
    
    categories = Category.objects.all()
    
    context = {
        'total_docs': total_docs,
        'incoming': incoming,
        'outgoing': outgoing,
        'internal': internal,
        'categories_stats': categories_stats,
        'users_stats': users_stats,
        'recent_logs': recent_logs,
        'categories': categories,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'eams/reports.html', context)
"""

# Replace the existing reports_view
import re
# Find the start of reports_view and replace until the end
pattern = r"@login_required\s+def reports_view\(request\):.*?(?=@login_required|\Z)"
new_content = re.sub(pattern, new_reports_view, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated reports_view with filtering logic")
