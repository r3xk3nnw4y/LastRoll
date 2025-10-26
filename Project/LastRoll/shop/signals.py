# shop/signals.py
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from shop.models import Profile


def connect_buyer_seller_signals():
    """
    Delayed import of Buyer and Seller models once all apps are ready
    (avoids circular import issues).
    """
    Buyer = apps.get_model('store', 'Buyer')
    Seller = apps.get_model('store', 'Seller')

    # --- Direction 1: When a Buyer or Seller is created, update the Profile role ---
    @receiver(post_save, sender=Buyer)
    def set_buyer_role(sender, instance, created, **kwargs):
        if created:
            profile = instance.user.profile
            if profile.role != Profile.ROLE_BUYER:
                profile.role = Profile.ROLE_BUYER
                profile.save()

    @receiver(post_save, sender=Seller)
    def set_seller_role(sender, instance, created, **kwargs):
        if created:
            profile = instance.user.profile
            if profile.role != Profile.ROLE_SELLER:
                profile.role = Profile.ROLE_SELLER
                profile.save()

    # --- Direction 2: When a Profile is created, make a Buyer or Seller record automatically ---
    @receiver(post_save, sender=Profile)
    def create_buyer_or_seller(sender, instance, created, **kwargs):
        if created:
            if instance.role == Profile.ROLE_BUYER:
                Buyer.objects.get_or_create(user=instance.user)
            elif instance.role == Profile.ROLE_SELLER:
                Seller.objects.get_or_create(user=instance.user)

    @receiver(post_save, sender=Profile)
    def ensure_buyer_or_seller_exists(sender, instance, **kwargs):
        """Ensures user always has a matching Buyer/Seller record"""
        if instance.role == Profile.ROLE_BUYER:
            Buyer.objects.get_or_create(user=instance.user)
        elif instance.role == Profile.ROLE_SELLER:
            Seller.objects.get_or_create(user=instance.user)
