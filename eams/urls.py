from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/', permanent=True)),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/stats-partial/', views.dashboard_stats_partial, name='dashboard_stats_partial'),
    path('dashboard/activities-partial/', views.dashboard_activities_partial, name='dashboard_activities_partial'),
    path('dashboard/search/', views.dashboard_search, name='dashboard_search'),
    path('dashboard/quick-search/', views.quick_search, name='quick_search'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/', views.document_list, name='document_list'),
    path('document/create/', views.document_create, name='document_create'),
    path('document/<int:pk>/download/', views.document_download, name='document_download'),
    path('document/<int:pk>/update/', views.document_update, name='document_update'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('users/', views.user_management, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/update/', views.user_update, name='user_update'),
    path('users/<int:pk>/detail/', views.user_detail, name='user_detail'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    path('documents/delete/<int:pk>/', views.document_delete, name='document_delete'),
    path('documents/attachment/<int:pk>/delete/', views.attachment_delete, name='attachment_delete'),
    path('documents/<int:doc_pk>/attachments/add/', views.attachment_add, name='attachment_add'),
    path('audit/', views.audit_log_view, name='audit_log'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/export/', views.reports_export_pdf, name='reports_export_pdf'),
    
    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:pk>/update/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('transactions/<int:pk>/print/', views.transaction_print, name='transaction_print'),
    path('track/', views.tracking_page, name='tracking_page'),
    path('api/track/', views.public_tracking_api, name='public_tracking_api'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='eams/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
]
