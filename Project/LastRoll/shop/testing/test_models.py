from django.test import TestCase
from django.contrib.auth.models import User
from store.models import Seller, Buyer, Product

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="pass123")
        self.seller = Seller.objects.create(user=self.user, store_name="Test Store")

    def test_product_creation(self):
        p = Product.objects.create(
            seller=self.seller,
            name="Dice",
            description="Test dice",
            price=10.00,
            stock=5,
            color="Red",
            material="Plastic",
            dice_type="D6"
        )
        self.assertEqual(p.name, "Dice")
        self.assertEqual(p.stock, 5)
        self.assertEqual(str(p), "Dice by Test Store")
