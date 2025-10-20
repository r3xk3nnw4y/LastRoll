from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),  # include store app API URLs

    # 🔐 Authentication routes (using Django’s built-in views)
    path('login/', auth_views.LoginView.as_view(
        template_name='shop/login.html',
        redirect_authenticated_user=True,
        next_page='shop-role-redirect'  # sends users to role_redirect after login
    ), name='shop-login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='shop/logout.html'
    ), name='shop-logout'),

    # 🧭 Role-based redirect after login
    path('redirect/', views.role_redirect, name='shop-role-redirect'),

    # 🏠 Main Pages
    path('', views.home, name='shop-home'),
    path('about/', views.about, name='shop-about'),
    path('register/', views.register, name='shop-register'),

    # 👤 Buyer Pages
    path('buyerhome/', views.buyerhome, name='shop-buyerhome'),
    path('cart/', views.cart, name='shop-cart'),
    path('buyeraccount/', views.buyeraccount, name='shop-buyeraccount'),
    path('alllistings/', views.alllistings, name='shop-alllistings'),
    path('featuredlistings/', views.featuredlistings, name='shop-featuredlistings'),

    # 💼 Seller Pages
    path('sellerdashboard/', views.sellerdashboard, name='shop-sellerdashboard'),
    path('selleraccount/', views.selleraccount, name='shop-selleraccount'),
    path('sellermylistings/', views.sellermylistings, name='shop-sellermylistings'),
    path('sellermyorders/', views.sellermyorders, name='shop-sellermyorders'),
    path('sellersales/', views.sellersales, name='shop-sellersales'),

    # 🧑‍💻 Admin Pages
    path('admindashboard/', views.admindashboard, name='shop-admindashboard'),
    path('adminaccount/', views.adminaccount, name='shop-adminaccount'),
    path('pendingsellers/', views.pendingsellers, name='shop-pendingsellers'),
    path('pendinglistings/', views.pendinglistings, name='shop-pendinglistings'),
    path('reportedlistings/', views.reportedlistings, name='shop-reportedlistings'),

    path('logout/', auth_views.LogoutView.as_view(template_name='shop/logout.html'), name='shop-logout'),
]
