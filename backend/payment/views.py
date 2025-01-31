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

        # Retrieve the line items associated with the session
        line_items = stripe.checkout.Session.list_line_items(session.id)
        # Loop through line items to extract price and product details
        for item in line_items.data:
            price = stripe.Price.retrieve(item.price.id)
            product = stripe.Product.retrieve(item.price.product)

            # iterate through all avalible subscription plans
            user_plans_available = request.user.plan_and_subscription.all()
            for current_pln in user_plans_available:
                if (
                    current_pln.status == "PENDING"
                    and current_pln.subscription_type == product.name
                ):
                    # create bill of payment
                    subscription = SubscriptionHistory.objects.create(
                        user=request.user,
                        plan=product.name,
                        price=price.unit_amount_decimal,
                        status=True,
                    )
                    current_pln.status = "PAID"
                # activate subscribtion (is_active)
                current_pln.is_active = current_pln.subscription_type == product.name
                # update subscription id in the DB
                if current_pln.is_active:
                    current_pln.subscription_id = session.subscription
                else:
                    current_pln.subscription_id = ""

                current_pln.save()

        return Response(
            {"message": f"Thank you for payment, {request.user.get_full_name()}!"},
            status=status.HTTP_201_CREATED,
        )
