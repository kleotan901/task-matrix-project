from rest_framework import serializers
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "status",
            "subscription_type",
            "is_active",
            "session_url",
            "subscription_id",
        ]
