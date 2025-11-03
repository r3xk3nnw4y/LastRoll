from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Django Admin + API
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),

    # 🔐 Authentication routes (using Django’s built-in views)
    path('login/', auth_views.LoginView.as_view(
        template_name='shop/login.html',
        redirect_authenticated_user=True,
        next_page='shop-role-redirect'
    ), name='shop-login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='shop/logout.html'
    ), name='shop-logout'),

    # 🧭 Role-based redirect after login
    path('redirect/', views.role_redirect, name='shop-role-redirect'),
    path('suspension/', views.suspension_notice, name='shop-suspension-notice'),

    # 🏠 Main Pages
    path('', views.home, name='shop-home'),
    path('about/', views.about, name='shop-about'),
    path('register/', views.register, name='shop-register'),
    path('register/buyer/', views.buyerregister, name='shop-register-buyer'),
    path('register/seller/', views.sellerregister, name='shop-register-seller'),


    # 👤 Buyer Pages
    path('buyerhome/', views.buyerhome, name='shop-buyerhome'),
    path('cart/', views.cart, name='shop-cart'),
    path('buyeraccount/', views.buyeraccount, name='shop-buyeraccount'),
    path('alllistings/', views.alllistings, name='shop-alllistings'),
    path('featuredlistings/', views.featuredlistings, name='shop-featuredlistings'),

    # Seller Pages
    path('sellerdashboard/', views.sellerdashboard, name='shop-sellerdashboard'),
    path('selleraccount/', views.selleraccount, name='shop-selleraccount'),
    path('sellermylistings/', views.sellermylistings, name='shop-sellermylistings'),
    path('sellercreatelisting/', views.sellercreatelisting, name='shop-sellercreatelisting'),
    path('sellermyorders/', views.sellermyorders, name='shop-sellermyorders'),
    path('sellersales/', views.sellersales, name='shop-sellersales'),

    # Admin Pages
    path('admindashboard/', views.admindashboard, name='shop-admindashboard'),
    path('adminaccount/', views.adminaccount, name='shop-adminaccount'),
    path('pendingsellers/', views.pendingsellers, name='shop-pendingsellers'),
    path('pendingsellers/update/<int:seller_id>/', views.update_seller_status, name='shop-update-seller-status'),
    path('pendinglistings/', views.pendinglistings, name='shop-pendinglistings'),
    path('manageusers/', views.manage_users, name='shop-manage-users'),
    path('manageusers/toggle/<int:user_id>/', views.toggle_suspension, name='shop-toggle-suspension'),

    # Product Management
    path('products/<int:pk>/approve/', views.approve_product, name='approve_product'),
    path('products/<int:pk>/reject/', views.reject_product, name='reject_product'),
    path('products/<int:pk>/remove/', views.remove_product, name='remove_product'),

    # Reporting System
    path('products/<int:pk>/report/', views.report_product, name='report_product'),
    path('reportedlistings/', views.reportedlistings, name='shop-reportedlistings'),
    path('reportedlistings/<int:pk>/<str:action>/', views.resolve_report, name='resolve_report'),

    path('logout/', auth_views.LogoutView.as_view(template_name='shop/logout.html'), name='shop-logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)