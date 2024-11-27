import stripe
from stripe import Product
from stripe.checkout import Session
from django.conf import settings

from profile.models import User

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
HOME_DOMAIN = settings.HOME_DOMAIN


def create_product(subscription_product: str) -> Session:
    return stripe.Product.create(name=subscription_product)


def create_price_object(product: Product, amount: int, interval: str) -> Session:
    return stripe.Price.create(
        product=product.id,
        unit_amount=amount,
        currency="UAH",
        recurring={"interval": interval},
    )


def create_checkout_session(user: User) -> tuple[Session] | Exception:
    try:
        product_premium = create_product("premium")
        product_profi = create_product("profi")

        price_premium = create_price_object(product_premium, 39900, "month")
        price_profi = create_price_object(product_profi, 69900, "month")

        customer = stripe.Customer.create(name=user.get_full_name(), email=user.email)

        session_premium = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer=customer,
            line_items=[
                {"price": price_premium.id, "quantity": 1},
            ],
            mode="subscription",
            success_url=f"{HOME_DOMAIN}api/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{HOME_DOMAIN}api/payments/cancel",
        )

        session_profi = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer=customer,
            line_items=[
                {"price": price_profi.id, "quantity": 1},
            ],
            mode="subscription",
            success_url=f"{HOME_DOMAIN}api/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{HOME_DOMAIN}api/payments/cancel",
        )

    except Exception as err:
        return err
    return session_premium, session_profi
