from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class ViewPermissionTests(TestCase):
    def test_buyer_denied_from_seller_dashboard(self):
        user = User.objects.create_user(username="buyer", password="pass123")
        user.profile.role = user.profile.ROLE_BUYER
        user.profile.save()

        self.client.login(username="buyer", password="pass123")
        response = self.client.get(reverse("shop-sellerdashboard"))
        self.assertEqual(response.status_code, 403)
