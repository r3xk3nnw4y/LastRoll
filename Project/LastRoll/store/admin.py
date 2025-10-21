from django.contrib import admin

# Import models safely inside try/except
try:
    from .models import Buyer, Seller, Product, Order, OrderItem
except ImportError:
    Buyer = Seller = Product = Order = OrderItem = None


if Buyer:
    @admin.register(Buyer)
    class BuyerAdmin(admin.ModelAdmin):
        list_display = ('user', 'address')
        search_fields = ('user__username',)

if Seller:
    @admin.register(Seller)
    class SellerAdmin(admin.ModelAdmin):
        list_display = ('user', 'store_name')
        search_fields = ('user__username',)

if Product:
    @admin.register(Product)
    class ProductAdmin(admin.ModelAdmin):
        list_display = ('name', 'price', 'stock', 'seller')
        search_fields = ('name', 'seller__store_name')

if Order:
    @admin.register(Order)
    class OrderAdmin(admin.ModelAdmin):
        list_display = ('id', 'buyer', 'created_at', 'is_paid', 'total')
        list_filter = ('is_paid',)
        search_fields = ('buyer__user__username',)

if OrderItem:
    @admin.register(OrderItem)
    class OrderItemAdmin(admin.ModelAdmin):
        list_display = ('order', 'product', 'quantity', 'price')
