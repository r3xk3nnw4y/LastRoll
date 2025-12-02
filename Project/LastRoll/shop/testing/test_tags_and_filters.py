from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Profile
from store.models import Seller, Product


class TagFilterTests(TestCase):
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
            defaults={"store_name": "Tag Store"},
        )
        if not self.seller.store_name:
            self.seller.store_name = "Tag Store"
            self.seller.save()

        # Two differently tagged products
        self.red_dice = Product.objects.create(
            seller=self.seller,
            name="Red Metal D6",
            description="Red metal die",
            price=5,
            stock=10,
            color="Red",
            material="Metal",
            dice_type="D6",
            status=1,
        )
        self.blue_dice = Product.objects.create(
            seller=self.seller,
            name="Blue Plastic D20",
            description="Blue plastic die",
            price=7,
            stock=10,
            color="Blue",
            material="Plastic",
            dice_type="D20",
            status=1,
        )

    def test_filter_by_color(self):
        url = reverse("shop-alllistings")
        response = self.client.get(url, {"color": "Red"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Red Metal D6")
        self.assertNotContains(response, "Blue Plastic D20")
