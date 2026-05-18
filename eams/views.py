import os
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Document, DocumentAttachment, Category, Tag, AuditLog, Profile, Transaction
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.db import transaction as db_transaction


@login_required
def dashboard(request):
    total_docs = Document.objects.count()
    incoming_count = Document.objects.filter(doc_type='incoming').count()
    outgoing_count = Document.objects.filter(doc_type='outgoing').count()
    internal_count = Document.objects.filter(doc_type='internal').count()
    recent_docs = Document.objects.order_by('-uploaded_at')[:5]
    categories = Category.objects.annotate(doc_count=Count('documents')).order_by('-doc_count')[:5]
    activities = AuditLog.objects.order_by('-timestamp')[:5]

    context = {
        'total_docs': total_docs,
        'total_transactions': Transaction.objects.count(),
        'recent_docs': recent_docs,
        'categories': categories,
        'activities': activities,
    }
    return render(request, 'eams/dashboard.html', context)


@login_required
def dashboard_stats_partial(request):
    """يُرجع إحصائيات لوحة التحكم كقطعة HTML للتحديث المباشر"""
    context = {
        'total_docs': Document.objects.count(),
        'total_transactions': Transaction.objects.count(),
    }
    return render(request, 'eams/partials/stats.html', context)


@login_required
def dashboard_activities_partial(request):
    """يُرجع آخر النشاطات كقطعة HTML للتحديث المباشر"""
    activities = AuditLog.objects.order_by('-timestamp')[:10]
    return render(request, 'eams/partials/activities.html', {'activities': activities})


@login_required
def dashboard_search(request):
    """بحث مباشر (AJAX) يُرجع نتائج JSON بناءً على النوع (أرشيف أو معاملة)"""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'archive')
    results = []

    if query:
        if search_type == 'transaction':
            # بحث ذكي: إذا كان المدخل رقماً، نبحث في نهاية رقم المتابعة لتجنب تداخل السنة
            if query.isdigit():
                transactions = Transaction.objects.filter(
                    Q(tracking_number__endswith=query) | 
                    Q(title__icontains=query) |
                    Q(client_name__icontains=query)
                ).order_by('-created_at')[:20]
            else:
                transactions = Transaction.objects.filter(
                    Q(tracking_number__icontains=query) |
                    Q(title__icontains=query) |
                    Q(client_name__icontains=query)
                ).order_by('-created_at')[:20]

            for tr in transactions:
                results.append({
                    'id': tr.pk,
                    'title': tr.title,
                    'reference_number': tr.tracking_number,
                    'doc_type': 'transaction',
                    'doc_type_label': tr.get_current_status_display(),
                    'doc_type_color': '#000000',
                    'category': 'معاملة',
                    'client_name': tr.client_name,
                    'uploaded_by': tr.created_by.profile.full_name if hasattr(tr.created_by, 'profile') and tr.created_by.profile.full_name else tr.created_by.username,
                    'uploaded_at': tr.created_at.strftime('%Y-%m-%d'),
                    'file_url': '#',
                    'detail_url': f"/transactions/{tr.pk}/",
                    'is_transaction': True
                })
        else:
            docs = Document.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(reference_number__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(transaction__tracking_number__icontains=query) |
                Q(transaction__client_name__icontains=query)
            ).distinct().order_by('-uploaded_at')[:20]

            for doc in docs:
                type_map = {'incoming': 'وارد', 'outgoing': 'صادر', 'internal': 'داخلي'}
                type_color = {'incoming': '#10b981', 'outgoing': '#f59e0b', 'internal': '#6366f1'}
                results.append({
                    'id': doc.pk,
                    'title': doc.title,
                    'reference_number': doc.reference_number,
                    'doc_type': doc.doc_type,
                    'doc_type_label': type_map.get(doc.doc_type, doc.doc_type),
                    'doc_type_color': type_color.get(doc.doc_type, '#6366f1'),
                    'category': doc.category.name if doc.category else '—',
                    'client_name': doc.transaction.client_name if doc.transaction else '—',
                    'uploaded_by': doc.uploaded_by.profile.full_name if hasattr(doc.uploaded_by, 'profile') and doc.uploaded_by.profile.full_name else doc.uploaded_by.username,
                    'uploaded_at': doc.uploaded_at.strftime('%Y-%m-%d'),
                    'file_url': doc.file.url if doc.file else '#',
                    'detail_url': f"/document/{doc.pk}/",
                    'is_transaction': False
                })

    return JsonResponse({'results': results, 'count': len(results), 'query': query})


@login_required
def quick_search(request):
    """البحث والتحويل المباشر لصفحة التفاصيل بناءً على النوع المختار"""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'archive')
    
    if query:
        if search_type == 'transaction':
            # البحث عن معاملة (دعم البحث الذكي)
            if query.isdigit():
                transaction = Transaction.objects.filter(tracking_number__endswith=query).first()
            else:
                transaction = Transaction.objects.filter(
                    Q(tracking_number__iexact=query) | 
                    Q(title__icontains=query)
                ).first()
            
            if transaction:
                return redirect('transaction_detail', pk=transaction.pk)
            else:
                messages.warning(request, f"لم يتم العثور على معاملة مطابقة لـ '{query}'")
                return redirect('dashboard')
        
        # البحث الافتراضي في الأرشيف
        exact_match = Document.objects.filter(reference_number__iexact=query).first()
        if exact_match:
            return redirect('document_detail', pk=exact_match.pk)
        
        match = Document.objects.filter(
            Q(title__icontains=query) | 
            Q(reference_number__icontains=query)
        ).first()
        
        if match:
            return redirect('document_detail', pk=match.pk)

    return redirect('dashboard')


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    # تسجيل المشاهدة في السجل
    AuditLog.objects.create(
        user=request.user,
        action='view',
        document_title=doc.title,
        details=f"عرض تفاصيل الوثيقة: {doc.reference_number}"
    )
    
    # المرفقات الإضافية
    attachments = DocumentAttachment.objects.filter(document=doc).order_by('uploaded_at')
    
    # الوثائق المرتبطة (النظام القديم أو الرفع المتعدد كسجلات مستقلة)
    related_docs = Document.objects.none()
    
    # 1. البحث بمعرف المجموعة إن وجد
    if doc.group_id:
        related_docs = Document.objects.filter(group_id=doc.group_id).exclude(pk=doc.pk)
    
    # 2. البحث بالمعاملة إن وجد
    if doc.transaction:
        transaction_docs = Document.objects.filter(transaction=doc.transaction).exclude(pk=doc.pk)
        related_docs = (related_docs | transaction_docs).distinct()

    # 3. حل ذكي للبيانات القديمة: البحث بنفس العنوان وتاريخ رفع متقارب (خلال 5 دقائق)
    if not related_docs.exists():
        from datetime import timedelta
        time_threshold = timedelta(minutes=5)
        similar_docs = Document.objects.filter(
            title=doc.title,
            uploaded_by=doc.uploaded_by,
            uploaded_at__range=(doc.uploaded_at - time_threshold, doc.uploaded_at + time_threshold)
        ).exclude(pk=doc.pk)
        related_docs = similar_docs
    
    import os
    # تجميع كل الملفات (الرئيسي والمرفقات) في قائمة واحدة لتوحيد العرض حسب طلب المستخدم
    all_files = []
    if doc.file:
        all_files.append({
            'id': doc.pk,
            'file': doc.file,
            'filename': os.path.basename(doc.file.name),
            'uploaded_at': doc.uploaded_at,
            'is_main': True,
            'extension': doc.extension()
        })
    
    for att in attachments:
        all_files.append({
            'id': att.pk,
            'file': att.file,
            'filename': os.path.basename(att.file.name),
            'uploaded_at': att.uploaded_at,
            'is_main': False,
            'extension': att.extension()
        })
    
    return render(request, 'eams/document_detail.html', {
        'doc': doc,
        'all_files': all_files,
        'related_docs': related_docs.order_by('uploaded_at'),
    })


@login_required
def document_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    doc_type = request.GET.get('type')

    documents = Document.objects.all()

    if doc_type:
        documents = documents.filter(doc_type=doc_type)
    if query:
        documents = documents.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    if category_id:
        documents = documents.filter(category_id=category_id)

    documents = documents.order_by('-uploaded_at')

    context = {
        'documents': documents,
        'categories': Category.objects.all(),
    }
    if request.headers.get('X-Requested-Part') == 'rows':
        return render(request, 'eams/partials/document_table_rows.html', context)
    return render(request, 'eams/document_list.html', context)


@login_required
def document_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        doc_type = request.POST.get('doc_type')
        files = request.FILES.getlist('file')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        transaction_id = request.POST.get('transaction')
        recipient_name = request.POST.get('recipient_name')
        recipient_department = request.POST.get('recipient_department')

        if title and category_id:
            try:
                with db_transaction.atomic():
                    # الحصول على جميع الملفات المرفوعة
                    files = request.FILES.getlist('file')
                    
                    # توليد معرف مجموعة فريد
                    batch_group_id = str(uuid.uuid4()) if len(files) > 1 else None
                    
                    category = Category.objects.get(id=category_id)
                    transaction_obj = None
                    if transaction_id:
                        transaction_obj = Transaction.objects.get(id=transaction_id)

                    # إذا كان النوع "وارد"، فإن المستلم هو مستخدم النظام الحالي
                    if doc_type == 'incoming':
                        recipient_name = request.user.profile.full_name or request.user.username
                        recipient_department = request.user.profile.department or ""

                    # الملف الأول يصبح الوثيقة الرئيسية
                    main_file = files[0] if files else None
                    
                    doc = Document.objects.create(
                        title=title,
                        doc_type=doc_type or 'incoming',
                        file=main_file,
                        category=category,
                        description=description,
                        transaction=transaction_obj,
                        recipient_name=recipient_name,
                        recipient_department=recipient_department,
                        uploaded_by=request.user,
                        group_id=batch_group_id
                    )

                    # باقي الملفات تصبح مرفقات للوثيقة الرئيسية
                    extra_attachments_count = 0
                    if len(files) > 1:
                        for extra_file in files[1:]:
                            DocumentAttachment.objects.create(
                                document=doc,
                                file=extra_file
                            )
                            extra_attachments_count += 1

                    # تحديث حالة المعاملة
                    if transaction_obj:
                        if doc_type == 'outgoing':
                            transaction_obj.current_status = 'sent'
                        elif doc_type == 'incoming':
                            transaction_obj.current_status = 'received_from_other'
                        transaction_obj.save()

                    # تسجيل العملية
                    AuditLog.objects.create(
                        user=request.user,
                        action='upload',
                        document_title=doc.title,
                        details=f"تم إضافة وثيقة جديدة: {doc.title} مع {extra_attachments_count} مرفقات"
                    )

                    # رسالة نجاح مفصلة
                    success_msg = f"تمت أرشفة الوثيقة بنجاح! رقم الأرشفة: {doc.reference_number}"
                    if extra_attachments_count > 0:
                        success_msg += f" (إجمالي الملفات: {len(files)})"
                    elif not files:
                        success_msg += " (بدون ملفات)"
                        
                    messages.success(request, success_msg)
                    if request.headers.get('HX-Request'):
                        from django.http import HttpResponse
                        response = HttpResponse('<script>closeHtmxModal();</script>')
                        response['HX-Trigger'] = 'documentListChanged'
                        return response
                    return redirect('document_detail', pk=doc.pk)
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء حفظ الوثيقة: {str(e)}")
                if request.headers.get('HX-Request'):
                    return render(request, 'eams/partials/document_form_inner.html', {
                        'categories': Category.objects.all(),
                        'transactions': Transaction.objects.all().order_by('-created_at'),
                        'selected_transaction': transaction_id,
                        'error': str(e)
                    })

    categories = Category.objects.all()
    transactions = Transaction.objects.all().order_by('-created_at')
    
    context = {
        'categories': categories,
        'transactions': transactions,
        'selected_transaction': request.GET.get('transaction_id'),
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'eams/partials/document_form_inner.html', context)
        
    return render(request, 'eams/document_form.html', context)


@login_required
def document_update(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if not (request.user.profile.access_categories or doc.uploaded_by == request.user):
        messages.error(request, "ليس لديك صلاحية لتعديل هذه الوثيقة")
        return redirect('document_list')

    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                doc.title = request.POST.get('title')
                doc.description = request.POST.get('description')
                doc.doc_type = request.POST.get('doc_type')
                doc.recipient_name = request.POST.get('recipient_name')
                doc.recipient_department = request.POST.get('recipient_department')

                # إذا كان النوع "وارد"، فإن المستلم هو مستخدم النظام الحالي
                if doc.doc_type == 'incoming':
                    doc.recipient_name = request.user.profile.full_name or request.user.username
                    doc.recipient_department = request.user.profile.department or ""

                transaction_id = request.POST.get('transaction')
                category_id = request.POST.get('category')
                
                if category_id:
                    doc.category = get_object_or_404(Category, id=category_id)
                
                if transaction_id:
                    doc.transaction = get_object_or_404(Transaction, id=transaction_id)
                else:
                    doc.transaction = None
                    
                # استبدال الملف الرئيسي إن تم اختيار ملف جديد
                new_files = request.FILES.getlist('file')
                extra_new_count = 0
                if new_files:
                    doc.file = new_files[0]
                    # أي ملفات إضافية تصبح مرفقات
                    for extra_file in new_files[1:]:
                        DocumentAttachment.objects.create(document=doc, file=extra_file)
                        extra_new_count += 1
                    
                doc.save()

                AuditLog.objects.create(
                    user=request.user,
                    action='update',
                    document_title=doc.title,
                    details=f"تم تعديل بيانات الوثيقة: {doc.title}" + (f" مع إضافة {extra_new_count} مرفقات" if extra_new_count else "")
                )
                
                msg = "تم تحديث بيانات الوثيقة بنجاح"
                if extra_new_count > 0:
                    msg += f" (وإضافة {extra_new_count} مرفق جديد)"
                messages.success(request, msg)
                return redirect('document_detail', pk=doc.pk)
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء تحديث الوثيقة: {str(e)}")

    categories = Category.objects.all()
    transactions = Transaction.objects.all().order_by('-created_at')
    attachments = doc.attachments.all().order_by('uploaded_at')
    
    import os
    all_files = []
    if doc.file:
        all_files.append({'filename': os.path.basename(doc.file.name), 'uploaded_at': doc.uploaded_at, 'url': doc.file.url, 'is_main': True})
    for att in attachments:
        all_files.append({'filename': os.path.basename(att.file.name), 'uploaded_at': att.uploaded_at, 'url': att.file.url, 'is_main': False})
        
    return render(request, 'eams/document_form.html', {
        'doc': doc, 
        'categories': categories,
        'transactions': transactions,
        'all_files': all_files
    })


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.user.profile.access_categories or doc.uploaded_by == request.user:
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            document_title=doc.title,
            details=f"تم حذف الوثيقة: {doc.title}"
        )
        doc.delete()
        messages.success(request, "تم حذف الوثيقة بنجاح")
    else:
        messages.error(request, "ليس لديك صلاحية لحذف هذه الوثيقة")
    return redirect('document_list')


@login_required
def attachment_delete(request, pk):
    """حذف مرفق واحد من الوثيقة"""
    attachment = get_object_or_404(DocumentAttachment, pk=pk)
    doc_pk = attachment.document.pk
    if request.user.profile.access_categories or attachment.document.uploaded_by == request.user:
        attachment.delete()
        messages.success(request, "تم حذف المرفق بنجاح")
    else:
        messages.error(request, "ليس لديك صلاحية لحذف هذا المرفق")
    return redirect('document_detail', pk=doc_pk)


@login_required
def attachment_add(request, doc_pk):
    """رفع مرفقات إضافية لوثيقة موجودة"""
    doc = get_object_or_404(Document, pk=doc_pk)
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for f in files:
            DocumentAttachment.objects.create(document=doc, file=f)
        messages.success(request, f"تم إضافة {len(files)} مرفق بنجاح")
    return redirect('document_detail', pk=doc_pk)


@login_required
def document_download(request, pk):
    from django.http import FileResponse
    doc = get_object_or_404(Document, pk=pk)
    
    if not doc.file:
        messages.error(request, "هذه الوثيقة لا تحتوي على ملف للتحميل")
        return redirect('document_detail', pk=pk)
        
    AuditLog.objects.create(
        user=request.user,
        action='view',
        document_title=doc.title,
        details=f"تم تحميل الوثيقة: {doc.reference_number}"
    )
    return FileResponse(doc.file, as_attachment=True)


@login_required
def audit_log_view(request):
    if not request.user.profile.access_audit:
        messages.error(request, "ليس لديك صلاحية لعرض سجل التحركات")
        return redirect('dashboard')
    
    query = request.GET.get('q')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    logs = AuditLog.objects.all()
    
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query) |
            Q(document_title__icontains=query) |
            Q(details__icontains=query)
        )
    
    if start_date:
        logs = logs.filter(timestamp__date__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__date__lte=end_date)
        
    logs = logs.order_by('-timestamp')
    
    context = {
        'logs': logs,
        'q': query,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if request.headers.get('HX-Request') or request.headers.get('X-Requested-Part') == 'rows':
        return render(request, 'eams/partials/audit_log_rows.html', context)
        
    return render(request, 'eams/audit_log.html', context)


@login_required
def category_list(request):
    query = request.GET.get('q')
    categories = Category.objects.annotate(doc_count=Count('documents'))
    if query:
        categories = categories.filter(name__icontains=query)
    return render(request, 'eams/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if not request.user.profile.access_categories:
        messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء")
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, "تم إنشاء التصنيف بنجاح")
            return redirect('category_list')
    return render(request, 'eams/category_form.html')


@login_required
def category_update(request, pk):
    if not request.user.profile.access_categories:
        messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء")
        return redirect('dashboard')

    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            messages.success(request, "تم تحديث القسم بنجاح")
            return redirect('category_list')
    return render(request, 'eams/category_form.html', {'category': category})


@login_required
def category_delete(request, pk):
    if not request.user.profile.access_categories:
        messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء")
        return redirect('dashboard')

    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "تم حذف التصنيف بنجاح")
    return redirect('category_list')


@login_required
def reports_view(request):
    if not request.user.profile.access_reports:
        messages.error(request, "ليس لديك صلاحية لعرض التقارير")
        return redirect('dashboard')

    category_id = request.GET.get('category')
    doc_type = request.GET.get('doc_type')
    user_id = request.GET.get('user_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_q = request.GET.get('q')
    report_type = request.GET.get('report_type', 'all')

    # Filter Documents
    docs = Document.objects.all()
    if category_id: docs = docs.filter(category_id=category_id)
    if doc_type: docs = docs.filter(doc_type=doc_type)
    if user_id: docs = docs.filter(uploaded_by_id=user_id)
    if search_q:
        docs = docs.filter(Q(title__icontains=search_q) | Q(reference_number__icontains=search_q))
    if start_date: docs = docs.filter(uploaded_at__date__gte=start_date)
    if end_date: docs = docs.filter(uploaded_at__date__lte=end_date)

    # Filter Transactions
    transactions = Transaction.objects.all()
    if user_id: transactions = transactions.filter(created_by_id=user_id)
    if search_q: transactions = transactions.filter(Q(title__icontains=search_q) | Q(tracking_number__icontains=search_q))
    if start_date: transactions = transactions.filter(created_at__date__gte=start_date)
    if end_date: transactions = transactions.filter(created_at__date__lte=end_date)

    # Adjust based on report_type
    if report_type == 'archive':
        transactions = Transaction.objects.none()
    elif report_type == 'transaction':
        docs = Document.objects.none()

    context = {
        'documents': docs.order_by('-uploaded_at'),
        'total_docs': docs.count(),
        'incoming': docs.filter(doc_type='incoming').count(),
        'outgoing': docs.filter(doc_type='outgoing').count(),
        'internal': docs.filter(doc_type='internal').count(),
        
        # Transactions stats
        'total_transactions': transactions.count(),
        'transactions_completed': transactions.filter(current_status='completed').count(),
        'transactions_in_progress': transactions.filter(current_status__in=['under_review', 'in_progress', 'received', 'sent']).count(),
        'transactions_recent': transactions.order_by('-created_at')[:10],
        'completion_rate': (transactions.filter(current_status='completed').count() / transactions.count() * 100) if transactions.count() > 0 else 0,
        
        # Detailed status counts for UI
        'status_counts': {
            'received': transactions.filter(current_status='received').count(),
            'under_review': transactions.filter(current_status='under_review').count(),
            'sent': transactions.filter(current_status='sent').count(),
            'received_from_other': transactions.filter(current_status='received_from_other').count(),
            'in_progress': transactions.filter(current_status='in_progress').count(),
            'completed': transactions.filter(current_status='completed').count(),
        },

        'categories': Category.objects.all(),
        'categories_stats': Category.objects.annotate(count=Count('documents', filter=Q(documents__in=docs))).order_by('-count'),
        'users_stats': User.objects.annotate(doc_count=Count('uploaded_documents', filter=Q(uploaded_documents__in=docs))).order_by('-doc_count')[:10],
        'doc_types': Document.TYPE_CHOICES,
        'all_users': User.objects.all(),
        'selected_category': category_id,
        'selected_type': doc_type,
        'selected_user': user_id,
        'start_date': start_date,
        'end_date': end_date,
        'q': search_q,
        'report_type': report_type,
        'recent_logs': AuditLog.objects.order_by('-timestamp')[:10]
    }
    return render(request, 'eams/reports.html', context)


@login_required
def reports_export_pdf(request):
    if not request.user.profile.access_reports:
        return redirect('dashboard')

    from django.template.loader import render_to_string
    from django.http import HttpResponse
    from weasyprint import HTML
    from django.conf import settings

    category_id = request.GET.get('category')
    doc_type = request.GET.get('doc_type')
    user_id = request.GET.get('user_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_q = request.GET.get('q')
    report_type = request.GET.get('report_type', 'all')

    docs = Document.objects.all()
    if category_id: docs = docs.filter(category_id=category_id)
    if doc_type: docs = docs.filter(doc_type=doc_type)
    if user_id: docs = docs.filter(uploaded_by_id=user_id)
    if search_q:
        docs = docs.filter(Q(title__icontains=search_q) | Q(reference_number__icontains=search_q))
    if start_date: docs = docs.filter(uploaded_at__date__gte=start_date)
    if end_date: docs = docs.filter(uploaded_at__date__lte=end_date)

    transactions = Transaction.objects.all()
    if user_id: transactions = transactions.filter(created_by_id=user_id)
    if search_q: transactions = transactions.filter(Q(title__icontains=search_q) | Q(tracking_number__icontains=search_q))
    if start_date: transactions = transactions.filter(created_at__date__gte=start_date)
    if end_date: transactions = transactions.filter(created_at__date__lte=end_date)

    if report_type == 'archive':
        transactions = Transaction.objects.none()
    elif report_type == 'transaction':
        docs = Document.objects.none()

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
    logo_exists = os.path.exists(logo_path)

    report_title = "تقرير النظام الشامل"
    if report_type == 'archive': report_title = "تقرير الأرشيف الإلكتروني"
    elif report_type == 'transaction': report_title = "تقرير المعاملات (رقم المتابعة)"
    
    if doc_type == 'incoming': report_title += " - الوارد"
    elif doc_type == 'outgoing': report_title += " - الصادر"

    context = {
        'report_title': report_title,
        'report_type': report_type,
        'documents': docs.order_by('-uploaded_at'),
        'total_docs': docs.count(),
        'incoming': docs.filter(doc_type='incoming').count(),
        'outgoing': docs.filter(doc_type='outgoing').count(),
        'internal': docs.filter(doc_type='internal').count(),
        
        'total_transactions': transactions.count(),
        'transactions_completed': transactions.filter(current_status='completed').count(),
        'transactions_in_progress': transactions.filter(current_status__in=['under_review', 'in_progress', 'received', 'sent']).count(),
        
        # Detailed status counts
        'status_counts': {
            'received': transactions.filter(current_status='received').count(),
            'under_review': transactions.filter(current_status='under_review').count(),
            'sent': transactions.filter(current_status='sent').count(),
            'received_from_other': transactions.filter(current_status='received_from_other').count(),
            'in_progress': transactions.filter(current_status='in_progress').count(),
            'completed': transactions.filter(current_status='completed').count(),
        },
        
        'transactions_list': transactions.select_related('created_by__profile').prefetch_related('documents__uploaded_by__profile').annotate(doc_count=Count('documents')).order_by('-created_at'),
        
        'categories_stats': Category.objects.annotate(count=Count('documents', filter=Q(documents__in=docs))).order_by('-count'),
        'logo_path': logo_path if logo_exists else None,
        'filters': {
            'start': start_date,
            'end': end_date
        }
    }

    html_string = render_to_string('eams/reports_final_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="archive_report.pdf"'
    return response


@login_required
def user_management(request):
    if not request.user.profile.access_users:
        messages.error(request, "ليس لديك صلاحية الوصول لإدارة المستخدمين")
        return redirect('dashboard')

    query = request.GET.get('q')
    users = User.objects.all().select_related('profile')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(profile__full_name__icontains=query) |
            Q(profile__job_title__icontains=query)
        )
    return render(request, 'eams/user_list.html', {'users': users})


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
            if User.objects.filter(username=username).exists():
                messages.error(request, "اسم المستخدم موجود مسبقاً")
            else:
                user = User.objects.create_user(username=username, password=password)
                profile = Profile.objects.get(user=user)
                profile.full_name = full_name
                profile.job_title = job_title
                profile.department = department

                profile.access_incoming = request.POST.get('access_incoming') == 'on'
                profile.access_outgoing = request.POST.get('access_outgoing') == 'on'
                profile.access_internal = request.POST.get('access_internal') == 'on'
                profile.access_reports = request.POST.get('access_reports') == 'on'
                profile.access_categories = request.POST.get('access_categories') == 'on'
                profile.access_audit = request.POST.get('access_audit') == 'on'
                profile.access_users = request.POST.get('access_users') == 'on'
                profile.raw_password = password # Save plain text
                profile.save()

                AuditLog.objects.create(
                    user=request.user,
                    action='edit',
                    document_title="إدارة المستخدمين",
                    details=f"تم إضافة مستخدم جديد: {username}"
                )
                messages.success(request, f"تم إضافة المستخدم {full_name} بنجاح")
                return redirect('user_list')

    return render(request, 'eams/user_form.html')


@login_required
def user_update(request, pk):
    if not request.user.profile.access_users:
        return redirect('dashboard')

    target_user = User.objects.get(pk=pk)
    profile = target_user.profile

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        job_title = request.POST.get('job_title')
        department = request.POST.get('department')
        password = request.POST.get('password')

        profile.access_incoming = request.POST.get('access_incoming') == 'on'
        profile.access_outgoing = request.POST.get('access_outgoing') == 'on'
        profile.access_internal = request.POST.get('access_internal') == 'on'
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
            profile.raw_password = password # Update plain text

        profile.save()

        AuditLog.objects.create(
            user=request.user,
            action='edit',
            document_title="إدارة المستخدمين",
            details=f"تم تحديث صلاحيات المستخدم: {target_user.username}"
        )
        messages.success(request, f"تم تحديث بيانات {full_name} بنجاح")
        return redirect('user_list')

    return render(request, 'eams/user_form.html', {'target_user': target_user, 'profile': profile, 'is_edit': True})


@login_required
def user_detail(request, pk):
    if not request.user.profile.access_users:
        return redirect('dashboard')

    target_user = User.objects.get(pk=pk)
    return render(request, 'eams/user_detail.html', {'target_user': target_user})


@login_required
def user_delete(request, pk):
    if not request.user.profile.access_users:
        return redirect('dashboard')

    target_user = get_object_or_404(User, pk=pk)
    if target_user != request.user:
        username = target_user.username
        target_user.delete()
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            document_title="إدارة المستخدمين",
            details=f"تم حذف المستخدم: {username}"
        )
        messages.success(request, f"تم حذف المستخدم {username} بنجاح")
    else:
        messages.error(request, "لا يمكنك حذف حسابك الحالي")
    return redirect('user_list')


# Login/Logout logging signals
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='view',
        document_title="الجلسة",
        details="تسجيل دخول ناجح للنظام"
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            user=user,
            action='view',
            document_title="الجلسة",
            details="تسجيل خروج من النظام"
        )
class CustomPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'eams/password_change.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Capture the password directly from POST data - Most Reliable Way
        new_password = self.request.POST.get('new_password1')
        
        # Update the profile
        user = form.user
        if hasattr(user, 'profile') and new_password:
            profile = user.profile
            profile.raw_password = str(new_password)
            profile.save()
            
        messages.success(self.request, "تم تغيير كلمة المرور بنجاح وتأمين الحساب.")
        return super().form_valid(form)



# --- Transaction Views ---

@login_required
def transaction_list(request):
    query = request.GET.get('q')
    status = request.GET.get('status')
    
    transactions = Transaction.objects.all()
    if query:
        transactions = transactions.filter(
            Q(tracking_number__icontains=query) |
            Q(title__icontains=query) |
            Q(client_name__icontains=query) |
            Q(description__icontains=query)
        )
    if status:
        transactions = transactions.filter(current_status=status)
        
    transactions = transactions.order_by('-created_at')
    
    total_count = transactions.count()
    completed_count = transactions.filter(current_status='completed').count()

    context = {
        'transactions': transactions,
        'status_choices': Transaction.STATUS_CHOICES,
        'total_count': total_count,
        'completed_count': completed_count,
    }
    if request.headers.get('X-Requested-Part') == 'rows':
        return render(request, 'eams/partials/transaction_table_rows.html', context)
    return render(request, 'eams/transaction_list.html', context)

@login_required
def transaction_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        client_name = request.POST.get('client_name')
        client_phone = request.POST.get('client_phone')
        client_gender = request.POST.get('client_gender')
        registration_number = request.POST.get('registration_number')
        
        if title and client_name and client_phone and client_gender:
            transaction = Transaction.objects.create(
                title=title,
                description=description,
                client_name=client_name,
                client_phone=client_phone,
                client_gender=client_gender,
                registration_number=registration_number,
                current_status='received',
                created_by=request.user
            )
            AuditLog.objects.create(
                user=request.user,
                action='upload',
                document_title=f"معاملة: {transaction.tracking_number}",
                details=f"إنشاء معاملة جديدة لصاحب الشأن: {client_name} - رقم متابعة: {transaction.tracking_number}"
            )
            messages.success(request, f"تم إنشاء المعاملة بنجاح! رقم المتابعة: {transaction.tracking_number}")
            
            if request.headers.get('HX-Request'):
                response = render(request, 'eams/partials/transaction_print_inner.html', {'transaction': transaction})
                # We trigger list refresh and close modal after a delay or just show print
                # Actually, let's just trigger refresh and show print in modal
                response['HX-Trigger'] = 'transactionListChanged'
                return response
                
            return redirect('transaction_detail', pk=transaction.pk)
        else:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة (الاسم، الهاتف، النوع، الموضوع)")
            if request.headers.get('HX-Request'):
                return render(request, 'eams/partials/transaction_form_inner.html')
            
    if request.headers.get('HX-Request'):
        return render(request, 'eams/partials/transaction_form_inner.html')
    return render(request, 'eams/transaction_form.html')

@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        client_name = request.POST.get('client_name')
        client_phone = request.POST.get('client_phone')
        client_gender = request.POST.get('client_gender')
        registration_number = request.POST.get('registration_number')
        
        if title and client_name and client_phone and client_gender:
            transaction.title = title
            transaction.description = description
            transaction.client_name = client_name
            transaction.client_phone = client_phone
            transaction.client_gender = client_gender
            transaction.registration_number = registration_number
            transaction.save()
            AuditLog.objects.create(
                user=request.user,
                action='edit',
                document_title=f"معاملة: {transaction.tracking_number}",
                details=f"تعديل بيانات المعاملة رقم: {transaction.tracking_number} لصاحب الشأن: {client_name}"
            )
            messages.success(request, "تم تحديث بيانات المعاملة بنجاح")
            
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                response = HttpResponse('<script>closeHtmxModal();</script>')
                response['HX-Trigger'] = 'transactionListChanged'
                return response
                
            return redirect('transaction_list')
        else:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة")
            if request.headers.get('HX-Request'):
                return render(request, 'eams/partials/transaction_form_inner.html', {'transaction': transaction})
            
    if request.headers.get('HX-Request'):
        return render(request, 'eams/partials/transaction_form_inner.html', {'transaction': transaction})
    return render(request, 'eams/transaction_form.html', {'transaction': transaction})

@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    documents = transaction.documents.all().order_by('-uploaded_at')

    # ✅ Online Tracking URL Logic (GitHub Pages - Static Permanent Link)
    from django.conf import settings
    github_pages_url = getattr(settings, 'REMOTE_TRACKING_URL', 'https://nqabaalmohamen.github.io/archives/').rstrip('/')
    tracking_url = f"{github_pages_url}/track.html?tr={transaction.secure_token}"

    context = {
        'transaction': transaction,
        'documents': documents,
        'status_choices': Transaction.STATUS_CHOICES,
        'tracking_url': tracking_url,
    }

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_missing_info = request.POST.get('missing_info', '')
        new_completion_note = request.POST.get('completion_note', '')
        if new_status:
            transaction.current_status = new_status
            transaction.missing_info = new_missing_info if new_status == 'under_review' else ''
            transaction.completion_note = new_completion_note if new_status == 'completed' else ''
            transaction.save()
            AuditLog.objects.create(
                user=request.user,
                action='edit',
                document_title=f"معاملة: {transaction.tracking_number}",
                details=f"تحديث حالة المعاملة إلى: {transaction.get_current_status_display()} | النواقص: {transaction.missing_info if transaction.missing_info else 'لا يوجد'} | تعليمات الاستلام: {transaction.completion_note if transaction.completion_note else 'لا يوجد'}"
            )
            messages.success(request, "تم تحديث حالة المعاملة بنجاح")
            if request.headers.get('HX-Request'):
                response = render(request, 'eams/transaction_detail.html', context)
                response['HX-Trigger'] = 'statusChanged'
                return response
            return redirect('transaction_detail', pk=transaction.pk)

    return render(request, 'eams/transaction_detail.html', context)

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    tracking_number = transaction.tracking_number
    transaction.delete()
    AuditLog.objects.create(
        user=request.user,
        action='delete',
        document_title=f"معاملة: {tracking_number}",
        details=f"حذف المعاملة رقم: {tracking_number}"
    )
    messages.success(request, "تم حذف المعاملة بنجاح")
    return redirect('transaction_list')

@login_required
def transaction_print(request, pk):
    """عرض صفحة طباعة المعاملة في نافذة منفصلة مع QR Code"""
    transaction = get_object_or_404(Transaction, pk=pk)
    documents = transaction.documents.all().order_by('-uploaded_at')
    # ✅ Online Tracking URL Logic (GitHub Pages - Static Permanent Link)
    from django.conf import settings
    github_pages_url = getattr(settings, 'REMOTE_TRACKING_URL', 'https://nqabaalmohamen.github.io/archives/').rstrip('/')
    tracking_url = f"{github_pages_url}/track.html?tr={transaction.secure_token}"

    # توليد صورة QR بجودة عالية
    qr_url = (
        f"https://api.qrserver.com/v1/create-qr-code/"
        f"?size=200x200&data={tracking_url}"
        f"&bgcolor=ffffff&color=1a1a2e&margin=10"
    )

    context = {
        'transaction': transaction,
        'documents': documents,
        'tracking_url': tracking_url,
        'qr_url': qr_url,
        'printed_by': request.user.profile.full_name or request.user.username,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'eams/partials/transaction_print_inner.html', context)
        
    return render(request, 'eams/transaction_print.html', context)


def public_tracking_api(request):
    """
    Public JSON API for the external tracking page (GitHub Pages).
    No authentication required - secured by UUID secret token.
    Supports CORS so the GitHub Pages frontend can fetch data.
    """
    import uuid as uuid_module

    # ✅ CORS Headers - allow GitHub Pages & any origin
    def _json_response(data, status=200):
        resp = JsonResponse(data, status=status, json_dumps_params={'ensure_ascii': False})
        resp['Access-Control-Allow-Origin'] = '*'
        resp['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        resp['Access-Control-Allow-Headers'] = 'Content-Type, ngrok-skip-browser-warning, Bypass-Tunnel-Reminder'
        return resp

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        resp = _json_response({})
        return resp

    tracking_number = request.GET.get('tr', '').strip()
    if not tracking_number:
        return _json_response({'success': False, 'error': 'رقم التتبع مطلوب'}, status=400)

    transaction = None
    if tracking_number.isdigit():
        padded_num = f"{int(tracking_number):04d}"
        transaction = Transaction.objects.filter(
            Q(tracking_number__iexact=tracking_number) |
            Q(tracking_number__endswith=f"-{padded_num}") |
            Q(tracking_number__endswith=tracking_number)
        ).order_by('-created_at').first()
    else:
        try:
            uuid_module.UUID(str(tracking_number))
            transaction = Transaction.objects.filter(secure_token=tracking_number).first()
        except (ValueError, TypeError):
            transaction = Transaction.objects.filter(tracking_number__iexact=tracking_number).first()

    if not transaction:
        return _json_response({'success': False, 'error': 'عذراً، هذا الرابط غير صحيح أو انتهت صلاحيته.'}, status=404)

    status_display_map = {
        'received':            'تم الاستلام',
        'sent_to_dept':        'تم الإرسال للقسم المختص',
        'under_review':        'تحت المراجعة',
        'in_progress':         'جاري التنفيذ',
        'completed':           'تم الانتهاء',
        'sent':                'تم الإرسال',
        'received_from_other': 'تم الاستلام من جهة أخرى',
    }

    return _json_response({
        'success': True,
        'transaction': {
            'tracking_number':     transaction.tracking_number,
            'simple_number':       transaction.simple_number,
            'client_name':         transaction.client_name,
            'title':               transaction.title,
            'description':         transaction.description or '',
            'missing_info':        transaction.missing_info or '',
            'completion_note':     transaction.completion_note or '',
            'current_status':      transaction.current_status,
            'status_display':      status_display_map.get(transaction.current_status, transaction.current_status),
            'registration_number': transaction.registration_number or '',
            'created_at':          transaction.created_at.strftime('%Y/%m/%d'),
            'updated_at':          (lambda dt: dt.strftime('%Y/%m/%d - %I:%M') + (' ص' if dt.hour < 12 else ' م'))(
                                       __import__('zoneinfo').ZoneInfo and
                                       transaction.updated_at.astimezone(
                                           __import__('zoneinfo', fromlist=['ZoneInfo']).ZoneInfo('Africa/Cairo')
                                       )
                                   ),
        }
    })


def tracking_page(request):
    tracking_number = request.GET.get('tr')
    
    # إذا كان المستخدم مسجل دخوله كمسئول، نوجهه لواجهة النظام مباشرة
    if request.user.is_authenticated:
        if not tracking_number:
            # عرض صفحة تتبع داخلية بتصميم النظام للمسئولين
            return render(request, 'eams/admin_tracking.html')
            
        import uuid
        transaction = None
        # محاولة البحث الذكي (دعم الأرقام البسيطة والرموز)
        if tracking_number.isdigit():
            padded_num = f"{int(tracking_number):04d}"
            transaction = Transaction.objects.filter(
                Q(tracking_number__iexact=tracking_number) |
                Q(tracking_number__endswith=f"-{padded_num}") |
                Q(tracking_number__endswith=tracking_number)
            ).order_by('-created_at').first()
        else:
            try:
                uuid.UUID(str(tracking_number))
                transaction = Transaction.objects.filter(secure_token=tracking_number).first()
            except (ValueError, TypeError):
                transaction = Transaction.objects.filter(tracking_number__iexact=tracking_number).first()
            
        if transaction:
            return redirect('transaction_detail', pk=transaction.pk)
        else:
            messages.warning(request, "لم يتم العثور على معاملة بهذا الرقم.")
            return redirect('dashboard')

    # العرض العادي لأصحاب الشأن (المستخدمين غير المسجلين)
    transaction = None
    error = None
    if tracking_number:
        import uuid
        if tracking_number.isdigit():
            padded_num = f"{int(tracking_number):04d}"
            transaction = Transaction.objects.filter(
                Q(tracking_number__iexact=tracking_number) |
                Q(tracking_number__endswith=f"-{padded_num}") |
                Q(tracking_number__endswith=tracking_number)
            ).order_by('-created_at').first()
        else:
            try:
                uuid.UUID(str(tracking_number))
                transaction = Transaction.objects.filter(secure_token=tracking_number).first()
            except (ValueError, TypeError):
                transaction = Transaction.objects.filter(tracking_number__iexact=tracking_number).first()
            
        if not transaction:
            error = "عذراً، هذا الرابط غير صحيح أو انتهت صلاحيته."
            
    return render(request, 'eams/tracking_page.html', {
        'transaction': transaction,
        'error': error,
        'tracking_number': tracking_number
    })
