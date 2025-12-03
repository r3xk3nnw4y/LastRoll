from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Profile
from store.models import Seller, Product


class ListingCreationTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Seller user + profile + Seller
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
            defaults={"store_name": "My Test Store"},
        )
        if not self.seller.store_name:
            self.seller.store_name = "My Test Store"
            self.seller.save()

        self.client.login(username="seller", password="pass123")

    def test_create_listing_and_visible_in_all_listings(self):
        create_url = reverse("shop-sellercreatelisting")
        data = {
            "name": "Test Dice",
            "description": "Nice test dice",
            "price": "9.99",
            "stock": 10,
            "color": "Red",
            "material": "Plastic",
            "dice_type": "D6",
        }
        response = self.client.post(create_url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Product should exist
        product = Product.objects.get(name="Test Dice")

        product.status = 1
        product.save()

        # Now it should appear on All Listings
        all_url = reverse("shop-alllistings")
        response_all = self.client.get(all_url)
        self.assertEqual(response_all.status_code, 200)
        self.assertContains(response_all, "Test Dice")
