from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Buyer, Seller, Product, Order
from .serializers import BuyerSerializer, SellerSerializer, ProductSerializer, OrderSerializer

# GET and POST endpoints
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny] # anyone can view products

    def perform_create(self, serializer):
        try:
            seller = Seller.objects.get(user=self.request.user)
        except Seller.DoesNotExist:
            raise PermissionError("This user is not a seller.")
        serializer.save() # attach the seller based on who's logged in

# GET, PUT/PAtCH, and DELETE endpoints
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny] # if we want to restrict further, change to IsAuthenticated

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated] # only logged in users can order
    
    def get_queryset(self):
        return Order.objects.filter(buyer__user=self.request.user) # return orders for logged in buyer

    def perform_create(self, serializer):
        buyer = Buyer.objects.get(user=self.request.user)
        serializer.save(buyer=buyer)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer__user=self.request.user)
