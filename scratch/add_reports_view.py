import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_view = """
@login_required
def reports_view(request):
    from .models import Document, Category, AuditLog
    from django.db.models import Count
    from django.contrib.auth.models import User
    
    # Overall Stats
    total_docs = Document.objects.count()
    incoming = Document.objects.filter(doc_type='incoming').count()
    outgoing = Document.objects.filter(doc_type='outgoing').count()
    internal = Document.objects.filter(doc_type='internal').count()
    
    # Category Distribution
    categories_stats = Category.objects.annotate(count=Count('documents')).order_by('-count')
    
    # User Activity Stats
    users_stats = User.objects.annotate(
        doc_count=Count('documents')
    ).order_by('-doc_count')[:10]
    
    # Recent Logs
    recent_logs = AuditLog.objects.all().order_by('-timestamp')[:15]
    
    context = {
        'total_docs': total_docs,
        'incoming': incoming,
        'outgoing': outgoing,
        'internal': internal,
        'categories_stats': categories_stats,
        'users_stats': users_stats,
        'recent_logs': recent_logs,
    }
    return render(request, 'eams/reports.html', context)
"""

if "def reports_view" not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(new_view)
    print("Added reports_view")
else:
    print("reports_view already exists")
