from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Users can only be a buyer or a seller, so OneToOneField

    # Buyer-specific fields go here.
    address = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Buyer: {self.user.username}"

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Seller-specific fields go here.
    store_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Seller: {self.store_name}"

class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE) # A seller can have many products, so ForeignKey
    name = models.CharField(max_length=100) # Product name
    description = models.TextField(blank=True) # Optional description
    price = models.DecimalField(max_digits=8, decimal_places=2) # Cost up to 999,999.99
    stock = models.PositiveIntegerField(default=0) # Inventory count - must be positive
    image = models.ImageField(upload_to='product_images/', blank=True) # Image upload stored in product_images/ folder

    def __str__(self):
        return f"{self.name} by {self.seller.store_name}"

class Order(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE) # Who ordered this?    
    created_at = models.DateTimeField(default=timezone.now) # Timestamp when order was created
    is_paid = models.BooleanField(default=False) # For payment integration later
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Total cost

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.user.username}"

    def update_total(self):
        # Recalculate order total whenever items change
        self.total = sum(item.price for item in self.items.all())
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items') # Links item to order; related_name lets us use order.items.all()
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # What are we ordering?
    quantity = models.PositiveIntegerField(default=1) # How many?
    price = models.DecimalField(max_digits=8, decimal_places=2) # Product price at order time

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
