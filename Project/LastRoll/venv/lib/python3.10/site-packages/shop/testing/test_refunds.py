from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Profile
from store.models import Buyer, Seller, Product, Order, OrderItem


class RefundTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Buyer user + profile + Buyer
        self.buyer_user = User.objects.create_user(
            username="buyer",
            password="pass123"
        )
        self.buyer_profile, _ = Profile.objects.get_or_create(
            user=self.buyer_user,
            defaults={"role": Profile.ROLE_BUYER},
        )
        self.buyer, _ = Buyer.objects.get_or_create(user=self.buyer_user)

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
            defaults={"store_name": "Refund Store"},
        )
        if not self.seller.store_name:
            self.seller.store_name = "Refund Store"
            self.seller.save()

        # Product + Order + OrderItem
        self.product = Product.objects.create(
            seller=self.seller,
            name="Refundable Dice",
            description="Can be refunded",
            price=10,
            stock=5,
            color="Red",
            material="Plastic",
            dice_type="D6",
            status=1,
        )

        self.order = Order.objects.create(
            buyer=self.buyer,
            address="123 Test Street",
            payment="Card",
        )

        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
        )

        self.client.login(username="buyer", password="pass123")

    def test_refund_order_marks_item_refunded(self):
        url = reverse("refund_order", args=[self.order.id])
        response = self.client.post(url, {"reason": "Did not like it"}, follow=True)
        self.assertEqual(response.status_code, 200)

        self.item.refresh_from_db()
        self.assertTrue(self.item.is_refunded)
        self.assertEqual(self.item.refund_reason, "Did not like it")
