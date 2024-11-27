from django.contrib import admin

from .models import User, SubscriptionHistory

admin.site.register(User)
admin.site.register(SubscriptionHistory)
