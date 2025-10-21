from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile


# Inline admin to show Profile under User in the admin panel
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# Extend the built-in User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# Re-register the User admin with our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Also register Profile separately (optional)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)
