from django.contrib import admin
from .models import Profile, Category, Tag, Document, DocumentAttachment, AuditLog

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'job_title', 'department')
    search_fields = ('user__username', 'full_name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class DocumentAttachmentInline(admin.TabularInline):
    model = DocumentAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'uploaded_at')
    list_filter = ('category', 'uploaded_at', 'tags')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)
    inlines = [DocumentAttachmentInline]

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'document_title', 'timestamp')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('user', 'action', 'document_title', 'timestamp', 'details')
