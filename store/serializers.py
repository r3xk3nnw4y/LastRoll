from rest_framework import serializers
from .models import Buyer, Seller, Product, Order, OrderItem

class BuyerSerializer(serializers.ModelSerializer): # ModelSerializer creates fields for us
    class Meta:
        model = Buyer
        fields = ['id', 'user', 'address'] # these are the fields we want exposed through API

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['id', 'user', 'store_name']

class ProductSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True) # when creating product via API, seller is determined by backend (who is logged in?)

    class Meta:
        model = Product
        fields = ['id', 'seller', 'name', 'description', 'price', 'stock', 'image']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']
        extra_kwargs = {
            'price': {'required': False}
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer = BuyerSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'created_at', 'is_paid', 'total', 'items']

    def get_total(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())



