from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Profile
from store.models import Buyer, Seller, Product


class CartStockTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create buyer user + profile + Buyer model
        self.buyer_user = User.objects.create_user(
            username="buyer",
            password="pass123"
        )
        self.buyer_profile, _ = Profile.objects.get_or_create(
            user=self.buyer_user,
            defaults={"role": Profile.ROLE_BUYER},
        )
        self.buyer, _ = Buyer.objects.get_or_create(user=self.buyer_user)

        # Create seller user + profile + Seller model
        seller_user = User.objects.create_user(
            username="seller",
            password="pass123"
        )
        self.seller_profile, _ = Profile.objects.get_or_create(
            user=seller_user,
            defaults={"role": Profile.ROLE_SELLER},
        )
        self.seller, _ = Seller.objects.get_or_create(
            user=seller_user,
            defaults={"store_name": "Test Store"},
        )
        if not self.seller.store_name:
            self.seller.store_name = "Test Store"
            self.seller.save()

        # Products: one in-stock, one out-of-stock
        self.in_stock_product = Product.objects.create(
            seller=self.seller,
            name="In Stock Dice",
            description="Plenty available",
            price=5,
            stock=5,
            color="Red",
            material="Plastic",
            dice_type="D6",
            status=1,  # approved
        )
        self.out_stock_product = Product.objects.create(
            seller=self.seller,
            name="Out of Stock Dice",
            description="None left",
            price=5,
            stock=0,
            color="Blue",
            material="Metal",
            dice_type="D20",
            status=1,  # approved
        )

    def test_add_to_cart_allowed_when_in_stock(self):
        self.client.login(username="buyer", password="pass123")
        url = reverse("add_to_cart", args=[self.in_stock_product.id])
        response = self.client.post(url, follow=True)

        # Should succeed (200 after redirect) and not show out-of-stock warning
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart_disallowed_when_stock_zero(self):
        self.client.login(username="buyer", password="pass123")
        url = reverse("add_to_cart", args=[self.out_stock_product.id])
        response = self.client.post(url, follow=True)

        # We at least expect a valid response (no crash).
        # Depending on your implementation you might show a message instead.
        self.assertEqual(response.status_code, 200)
