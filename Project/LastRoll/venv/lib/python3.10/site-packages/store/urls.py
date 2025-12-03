from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    ProductListCreateView,
    ProductDetailView,
    OrderListCreateView,
    OrderDetailView,
    OrderItemListCreateView,
    OrderViewSet
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # Products
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # OrderItems
    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),

    # Include all router-generated endpoints...
    path('', include(router.urls)),
]
