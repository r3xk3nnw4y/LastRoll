from rest_framework import serializers
from .models import Buyer, Seller, Product, Order, OrderItem
from django.contrib.auth.models import User
from shop.models import Profile

# --- Profile serializer (shows role info) ---
class ProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Profile
        fields = ['role', 'role_display']


# --- User serializer (includes profile) ---
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


# --- Buyer serializer ---
class BuyerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Buyer
        fields = ['id', 'user', 'address']


# --- Seller serializer ---
class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Seller
        fields = ['id', 'user', 'store_name']


# --- Product serializer ---
class ProductSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'seller', 'name', 'description', 'price', 'stock', 'image']


# --- Order item serializer ---
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']


# --- Order serializer ---
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer = BuyerSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'created_at', 'is_paid', 'total', 'items']

    def get_total(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())
