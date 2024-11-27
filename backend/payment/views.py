import stripe

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from payment.models import Payment
from profile.models import SubscriptionHistory
from payment.serializers import PaymentSerializer


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_payments = self.queryset.filter(user=self.request.user)
        return user_payments

    @action(methods=["get"], detail=True, url_path="success")
    def get_success_payment(self, request, pk):
        # Get success session
        session = stripe.checkout.Session.retrieve(
            request.query_params.get("session_id")
        )
        customer = stripe.Customer.retrieve(session.customer)

        payment = Payment.objects.get(session_id=session.id)
        # if payment was success -> status changed to "PAID"
        payment.status = "PAID"
        payment.save()

        # Retrieve the line items associated with the session
        line_items = stripe.checkout.Session.list_line_items(session.id)
        # Loop through line items to extract price and product details
        for item in line_items.data:
            price_id = item.price.id
            product_id = item.price.product

            price = stripe.Price.retrieve(price_id)
            product = stripe.Product.retrieve(product_id)

            subscription = SubscriptionHistory.objects.create(
                user=request.user,
                subscription_type=product.name,
                price=price.unit_amount_decimal,
                status=True,
            )

        return Response(
            {"message": f"Thank you for payment, {customer.name}!"},
            status=status.HTTP_201_CREATED,
        )
