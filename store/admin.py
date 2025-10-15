from django.contrib import admin
from .models import Buyer, Seller, Product, Order

# Register your models here.
admin.site.register(Buyer)
admin.site.register(Seller)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'stock') # Columns shown in admin table
    search_fields = ('name', 'seller__store_name') # Lets you search by field
    list_filter = ('seller',) # Filters in sidebar

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'created_at', 'total', 'is_paid')
    list_filter = ('is_paid', 'created_at')
