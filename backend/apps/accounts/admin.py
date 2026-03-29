from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import EmailVerification, Profile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-date_joined",)
    list_display = (
        "email",
        "username",
        "email_verified",
        "is_seller",
        "is_moderator",
        "is_admin",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email_verified",
        "is_seller",
        "is_moderator",
        "is_admin",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ("email", "username")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Marketplace Flags",
            {
                "fields": (
                    "email_verified",
                    "is_seller",
                    "is_moderator",
                    "is_admin",
                )
            },
        ),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            "Marketplace Flags",
            {
                "fields": (
                    "email_verified",
                    "is_seller",
                    "is_moderator",
                    "is_admin",
                )
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "country", "timezone", "locale")
    search_fields = ("user__email", "user__username", "display_name")


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "expires_at", "used_at", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "user__username")
