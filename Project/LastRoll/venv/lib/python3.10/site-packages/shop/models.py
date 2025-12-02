# shop/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_ADMIN = 1
    ROLE_BUYER = 2
    ROLE_SELLER = 3

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_BUYER, 'Buyer'),
        (ROLE_SELLER, 'Seller'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=ROLE_BUYER)

    suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


# Signals to auto-create / save Profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # in case profile exists, just save it (or will raise if missing),
    # create_user_profile above ensures creation.
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
