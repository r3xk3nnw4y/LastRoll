from django.shortcuts import redirect
from django.urls import reverse

class SuspensionMiddleware:
    """Prevents suspended users from accessing restricted pages."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, "profile", None)
            if profile and profile.suspended:
                allowed_paths = [
                    reverse("shop-buyeraccount"),
                    reverse("shop-selleraccount"),
                    reverse("shop-suspension-notice"),
                    reverse("shop-logout"),
                ]
                if request.path not in allowed_paths:
                    return redirect("shop-suspension-notice")

        return self.get_response(request)