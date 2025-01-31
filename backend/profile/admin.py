from django.contrib import admin

from .models import User, SubscriptionHistory, PasswordReset, EmailConfirmationToken


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "email_is_verified", "first_name", "last_name")
    ordering = ("-date_joined",)


admin.site.register(User, UserAdmin)
admin.site.register(SubscriptionHistory)
admin.site.register(PasswordReset)
admin.site.register(EmailConfirmationToken)
