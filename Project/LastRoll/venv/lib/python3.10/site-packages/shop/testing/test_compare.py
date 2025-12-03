from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Profile
from store.models import Seller, Product


class CompareTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Buyer user + profile
        self.buyer_user = User.objects.create_user(
            username="buyer",
            password="pass123"
        )
        self.buyer_profile, _ = Profile.objects.get_or_create(
            user=self.buyer_user,
            defaults={"role": Profile.ROLE_BUYER},
        )
        self.client.login(username="buyer", password="pass123")

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
            defaults={"store_name": "Compare Store"},
        )
        if not self.seller.store_name:
            self.seller.store_name = "Compare Store"
            self.seller.save()

        # Two products to compare
        self.product1 = Product.objects.create(
            seller=self.seller,
            name="Red Dice",
            description="Red Metal D6",
            price=5,
            stock=10,
            color="Red",
            material="Metal",
            dice_type="D6",
            status=1,
        )
        self.product2 = Product.objects.create(
            seller=self.seller,
            name="Blue Dice",
            description="Blue Plastic D20",
            price=7,
            stock=8,
            color="Blue",
            material="Plastic",
            dice_type="D20",
            status=1,
        )

    def test_compare_two_listings(self):
        url = reverse("shop-compare-listings")

        # Your view expects ?compare=<id>&compare=<id2>
        response = self.client.get(
            url,
            {
                "compare": [str(self.product1.id), str(self.product2.id)],
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Red Dice")
        self.assertContains(response, "Blue Dice")
