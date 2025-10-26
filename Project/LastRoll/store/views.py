from django.shortcuts import render
from django.urls import path, include
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from .models import Buyer, Seller, Product, Order, OrderItem
from .serializers import BuyerSerializer, SellerSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer

# GET and POST endpoints
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated] # anyone can view products

    def perform_create(self, serializer):
        try:
            seller = Seller.objects.get(user=self.request.user)
        except Seller.DoesNotExist:
            raise PermissionError("This user is not a seller.")
        serializer.save(seller=seller) # attach the seller based on who's logged in

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

class OrderItemListCreateView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order=Order.objects.get(pk=self.request.data['order'])
        product=Product.objects.get(pk=self.request.data['product'])
        serializer.save(
            order=order,
            product=product,
            price=product.price
        )
        order.update_total()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer__user=self.request.user)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.is_paid:
            return Response({"detail": "Order is already paid."}, status=status.HTTP_400_BAD_REQUEST)
        order.is_paid = True
        order.save()
        return Response({"detail": f"Order {order.id} marked as paid."})
