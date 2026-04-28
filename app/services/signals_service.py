from app.models import *
from app.services.newsletter_service import (
    send_order_info_to_group, 
    send_invoice_to_user, 
    notify_client_order_error,
    ask_review_from_user,
    send_gratitude_to_client,
    send_gratitude_for_review_to_client,
    notify_client_order_cancellation,
    notify_client_order_items_not_available
    )
from app.services.order_service import check_order_items_availability_from_billz
from django.db import transaction
from app.services.yandex_delivery_service import create_claim
from config import DEBUG
from app.utils.data_classes import OrderStatus, YandexTripStatus
from payment.services import cancel_order_payment, fiscalize_payment
from asgiref.sync import async_to_sync
from celery import shared_task
from app.services.billz_service import BillzService, APIMethods


@shared_task
def before_invoice_sending(order_id):
    try:
        order: Order = Order.objects.select_related('shop').get(id=order_id)
        products_not_available: list = check_order_items_availability_from_billz(order)
        if products_not_available:
            notify_client_order_items_not_available(order, products_not_available)
            return

        send_invoice_to_user.delay(order_id)
    except Exception as e:
        notify_client_order_error(order_id)
        error = (
            f"<b>Error occurred before invoice sending:</b> {e}\n"
            f"ID: {order.id}\n"
        )
        raise Exception(error)

