from django.urls import path
from . import views

urlpatterns = [

    # HOME
    path('', views.home, name='home'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),
    path("invoices/", views.all_invoices, name="all_invoices"),

    # INVOICE CRUD
    path('create/', views.create_invoice, name='create_invoice'),

    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/edit/', views.edit_invoice, name='edit_invoice'),
    path('invoice/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),

    # PDF
    path('invoice/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),

    # PUBLIC SHARE
    path('share/<uuid:token>/', views.public_invoice, name='public_invoice'),

    # ANALYTICS
    path('analytics/', views.analytics, name='analytics'),

    # AUTH
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # PRODUCTS
    path("products/", views.products, name="products"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:product_id>/delete/", views.delete_product, name="delete_product"),
    path("products/<int:product_id>/restore/", views.restore_product, name="restore_product"),

    # PROFILE + RESTOCK
    path("profile/", views.profile, name="profile"),
    path("restock/", views.restock, name="restock"),

    # =========================
    # NOTIFICATIONS API CORE
    # =========================
    path("notifications/api/", views.notifications_api, name="notifications_api"),
    path("notifications/<int:notification_id>/ok/", views.notification_ok, name="notification_ok"),
    path("notifications/<int:notification_id>/resolve/", views.notification_resolve, name="notification_resolve"),
    path("notifications/<int:notification_id>/delete/", views.notification_delete, name="notification_delete"),

    # FIXED NAME (IMPORTANT)
    path("notifications/clear/", views.notifications_clear, name="notifications_clear"),
    path("notifications/read-all/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
]