from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
import uuid

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'مدير نظام'),
        ('employee', 'موظف'),
        ('viewer', 'مشاهد'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="الاسم بالكامل")
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="الوظيفة")
    department = models.CharField(max_length=255, blank=True, null=True, verbose_name="القسم")
    raw_password = models.CharField(max_length=255, blank=True, null=True, verbose_name="كلمة المرور الحالية (للمدير)")
    
    # Simplified Section Access Permissions
    # Archive Sections
    access_incoming = models.BooleanField(default=True, verbose_name="الأرشيف الوارد")
    access_outgoing = models.BooleanField(default=True, verbose_name="الأرشيف الصادر")
    access_internal = models.BooleanField(default=True, verbose_name="البريد الداخلي")
    
    # Settings Sections
    access_reports = models.BooleanField(default=False, verbose_name="التقارير الإحصائية")
    access_categories = models.BooleanField(default=False, verbose_name="إدارة الأقسام")
    access_audit = models.BooleanField(default=False, verbose_name="سجل التحركات")
    access_users = models.BooleanField(default=False, verbose_name="إدارة المستخدمين")
    
    @property
    def can_access_documents(self):
        return self.access_incoming or self.access_outgoing or self.access_internal

    @property
    def can_access_reports(self):
        return self.access_reports

    @property
    def can_access_categories(self):
        return self.access_categories

    @property
    def can_access_audit_log(self):
        return self.access_audit

    @property
    def can_manage_users(self):
        return self.access_users

    def __str__(self):
        return self.full_name if self.full_name else self.user.username

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم التصنيف")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name="التصنيف الأب")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "تصنيفات"

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="الوسم")

    def __str__(self):
        return self.name

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('received', 'تم الاستلام'),
        ('sent_to_dept', 'تم الإرسال للقسم المختص'),
        ('under_review', 'تحت المراجعة'),
        ('in_progress', 'جاري التنفيذ'),
        ('completed', 'تم الانتهاء'),
    )
    tracking_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المتابعة")
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='received', verbose_name="الحالة الحالية")
    
    # Client Details (Added)
    client_name = models.CharField(max_length=255, verbose_name="الاسم", default="غير محدد")
    client_phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", default="000")
    client_gender = models.CharField(max_length=10, choices=(('male', 'ذكر'), ('female', 'أنثى')), verbose_name="النوع", default='male')
    registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم القيد (اختياري)")
    
    title = models.CharField(max_length=255, verbose_name="عنوان المعاملة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المعاملة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="بواسطة")
    secure_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="رمز الأمان")
    missing_info = models.TextField(blank=True, null=True, verbose_name="ملاحظات للنواقص (تظهر لصاحب الشأن)")
    completion_note = models.TextField(blank=True, null=True, verbose_name="تعليمات الاستلام عند الانتهاء (تظهر لصاحب الشأن)")

    def __str__(self):
        return f"{self.tracking_number} - {self.title}"

    @property
    def creator_name(self):
        if self.created_by:
            if hasattr(self.created_by, 'profile') and self.created_by.profile.full_name:
                return self.created_by.profile.full_name
            return self.created_by.username
        return "النظام"

    @property
    def simple_number(self):
        """استخراج الرقم الأخير من الكود (مثلاً 0001 يصبح 1)"""
        if self.tracking_number and '-' in self.tracking_number:
            try:
                return int(self.tracking_number.split('-')[-1])
            except (ValueError, IndexError):
                return self.id
        return self.id

    @property
    def display_tracking_number(self):
        """إرجاع رقم المتابعة بالكامل مثل TRK-2026-1 وبدون الأصفار الزائدة"""
        if self.tracking_number:
            parts = self.tracking_number.split('-')
            if len(parts) >= 3:
                try:
                    prefix = parts[0]
                    year = parts[1]
                    seq = int(parts[2])
                    return f"{prefix}-{year}-{seq}"
                except (ValueError, IndexError):
                    pass
            elif len(parts) == 2:
                try:
                    if len(parts[0]) == 4 and parts[0].isdigit():
                        return f"TRK-{parts[0]}-{int(parts[1])}"
                except ValueError:
                    pass
        return self.tracking_number

    @property
    def short_tracking_number(self):
        """إرجاع رقم المتابعة بشكل مبسط مثل 2026-1 للـ PDF وبدون الأصفار الزائدة"""
        if self.tracking_number:
            parts = self.tracking_number.split('-')
            if len(parts) >= 3:
                try:
                    year = parts[1]
                    seq = int(parts[2])
                    return f"{year}-{seq}"
                except (ValueError, IndexError):
                    pass
            elif len(parts) == 2:
                try:
                    if len(parts[0]) == 4 and parts[0].isdigit():
                        return f"{parts[0]}-{int(parts[1])}"
                except ValueError:
                    pass
        return self.tracking_number

    @property
    def get_whatsapp_url(self):
        from urllib.parse import quote
        
        # Format the phone number
        phone = str(self.client_phone or '').strip()
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('01'):
            clean_phone = '2' + clean_phone
        elif clean_phone.startswith('1'):
            clean_phone = '20' + clean_phone
        elif not clean_phone.startswith('20') and len(clean_phone) == 11 and clean_phone.startswith('0'):
            clean_phone = '2' + clean_phone[1:]
            
        if not clean_phone or clean_phone == '000':
            return "#" # Invalid phone

        greeting = "يا أستاذة" if self.client_gender == 'female' else "يا أستاذ"
        name = self.client_name or ""
        title = self.title or ""
        tracking_num = self.display_tracking_number
        track_url = self.tracking_url

        # The message is constructed safely server-side
        message = (
            f"تم تسجيل طلبكم بنجاح في نقابة المحامين بالفيوم\n\n"
            f"مرحباً بك {greeting} / {name}\n\n"
            f"بيانات الطلب: -\n"
            f"الموضوع : {title}\n"
            f"رقم المتابعة : {tracking_num}\n\n"
            f"رابط التتبع الطلب اونلاين:\n"
            f"{track_url}"
        )

        encoded_message = quote(message)
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"

    @property
    def tracking_url(self):
        from django.conf import settings
        github_pages_url = getattr(settings, 'REMOTE_TRACKING_URL', 'https://nqabaalmohamen.github.io/archives/').rstrip('/')
        return f"{github_pages_url}/track.html?tr={self.secure_token}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            year = timezone.now().year
            last_transaction = Transaction.objects.filter(tracking_number__startswith=f"TRK-{year}").order_by('id').last()
            if last_transaction and '-' in last_transaction.tracking_number:
                try:
                    last_sequence = int(last_transaction.tracking_number.split('-')[-1])
                    new_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    new_sequence = Transaction.objects.filter(created_at__year=year).count() + 1
            else:
                new_sequence = Transaction.objects.filter(created_at__year=year).count() + 1
            self.tracking_number = f"TRK-{year}-{new_sequence}"
        super().save(*args, **kwargs)

class Document(models.Model):
    TYPE_CHOICES = (
        ('incoming', 'وارد'),
        ('outgoing', 'صادر'),
        ('internal', 'داخلي'),
    )
    title = models.CharField(max_length=255, verbose_name="عنوان الوثيقة")
    doc_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='incoming', verbose_name="نوع الوثيقة")
    reference_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الصادر/الوارد")
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="الملف", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='documents', verbose_name="التصنيف")
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name="المعاملة (رقم المتابعة)")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="الوسوم")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    recipient_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="اسم المستلم")
    recipient_department = models.CharField(max_length=255, blank=True, null=True, verbose_name="قسم المستلم")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التعديل")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents', verbose_name="بواسطة")
    group_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="معرف المجموعة (للرفع المتعدد)")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.reference_number:
            year = timezone.now().year
            prefix = {
                'incoming': 'IN',
                'outgoing': 'OUT',
                'internal': 'INT'
            }.get(self.doc_type, 'DOC')
            
            # Get the last document of this type in this year to determine the next number
            last_doc = Document.objects.filter(
                doc_type=self.doc_type,
                uploaded_at__year=year
            ).order_by('id').last()
            
            if last_doc and last_doc.reference_number and '-' in last_doc.reference_number:
                try:
                    last_sequence = int(last_doc.reference_number.split('-')[-1])
                    new_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    new_sequence = Document.objects.filter(doc_type=self.doc_type, uploaded_at__year=year).count() + 1
            else:
                new_sequence = Document.objects.filter(doc_type=self.doc_type, uploaded_at__year=year).count() + 1
            
            self.reference_number = f"{prefix}-{year}-{new_sequence}"
        super().save(*args, **kwargs)

    @property
    def uploader_name(self):
        if self.uploaded_by:
            if hasattr(self.uploaded_by, 'profile') and self.uploaded_by.profile.full_name:
                return self.uploaded_by.profile.full_name
            return self.uploaded_by.username
        return "النظام"

    @property
    def short_reference_number(self):
        """إرجاع رقم الأرشفة بشكل مبسط مثل 2026-1 وبدون البادئة"""
        if self.reference_number:
            parts = self.reference_number.split('-')
            if len(parts) >= 3:
                try:
                    year = parts[1]
                    seq = int(parts[2])
                    return f"{year}-{seq}"
                except (ValueError, IndexError):
                    pass
            elif len(parts) == 2:
                try:
                    return f"{parts[0]}-{int(parts[1])}"
                except ValueError:
                    pass
        return self.reference_number

    def extension(self):
        if not self.file:
            return ""
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()

class DocumentAttachment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='attachments', verbose_name="الوثيقة")
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="الملف")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"مرفق لـ {self.document.title}"

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('upload', 'رفع'),
        ('edit', 'تعديل'),
        ('delete', 'حذف'),
        ('view', 'عرض'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="المستخدم")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="العملية")
    document_title = models.CharField(max_length=255, verbose_name="عنوان الوثيقة")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="الوقت")
    details = models.TextField(blank=True, null=True, verbose_name="التفاصيل")

    def __str__(self):
        return f"{self.user} {self.action} {self.document_title} at {self.timestamp}"

    @property
    def user_full_name(self):
        if self.user:
            if hasattr(self.user, 'profile') and self.user.profile.full_name:
                return self.user.profile.full_name
            return self.user.username
        return "النظام"

    @property
    def user_initial(self):
        if self.user:
            return self.user.username[0].upper()
        return "ن"

    @property
    def display_document_title(self):
        import re
        if self.document_title:
            return re.sub(r'TRK-(\d{4})-0*(\d+)', r'TRK-\1-\2', self.document_title)
        return self.document_title

    @property
    def display_details(self):
        import re
        if self.details:
            return re.sub(r'TRK-(\d{4})-0*(\d+)', r'TRK-\1-\2', self.details)
        return self.details
