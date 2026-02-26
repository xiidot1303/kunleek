from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import *
from app.services.newsletter_service import (
    send_order_info_to_group, 
    send_invoice_to_user, 
    notify_client_order_error,
    ask_review_from_user,
    send_gratitude_to_client,
    send_gratitude_for_review_to_client,
    notify_client_order_cancellation
    )
from app.services.order_service import send_order_to_billz
from django.db import transaction
from app.services.yandex_delivery_service import create_claim
from config import DEBUG
from app.utils.data_classes import OrderStatus, YandexTripStatus
from celery.signals import task_failure
from app.services.error_handler import run_on_error
from payment.services import cancel_order_payment
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Order)
def handle_cash_payment_order(sender, instance: Order, created, **kwargs):
    if created and (instance.payment_method == "cash" or instance.total == 0):
        instance.status = OrderStatus.NEED_CONFIRMATION
        instance.save(update_fields=["status"])
        # send order to group
        transaction.on_commit(
            lambda: send_order_info_to_group.delay(instance.id)
        )
    elif created:
        # send invoice to user with order information
        transaction.on_commit(
            lambda: send_invoice_to_user.delay(instance.id)
        )


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance: Order, update_fields, **kwargs):
    if not update_fields:
        return
    
    if "payed" in update_fields and instance.payed and instance.status == OrderStatus.CREATED:
        # change order status
        instance.status = OrderStatus.READY_TO_APPROVAL
        instance.save(update_fields=["status"])
    elif (
        instance.status == OrderStatus.READY_TO_APPROVAL
          and "status" in update_fields
          and not instance.billz_id 
          and not DEBUG
        ):
        # send order to billz
        transaction.on_commit(
            lambda: send_order_to_billz.delay(instance.id)
        )

    elif (
        instance.status == OrderStatus.READY_TO_APPROVAL 
        and not instance.sent_to_group
        and "billz_id" in update_fields
        ):
        instance.sent_to_group = True
        instance.save(update_fields=["sent_to_group"])
        transaction.on_commit(
            lambda: send_order_info_to_group.delay(instance.id)
        )
    
    elif (
            instance.status == OrderStatus.READY_TO_APPROVAL
            and instance.delivery_type.type == 'express_yandex'
            and "sent_to_group" in update_fields
        ):
        # Delivery
        if not DEBUG:
            if instance.delivery_type.is_open():
                transaction.on_commit(
                    lambda: create_claim.delay(instance.id)
                )
            else:
                instance.status = OrderStatus.WAITING_DELIVERY_WORKING_HOURS
                instance.save(update_fields=["status"])

    elif instance.status == OrderStatus.DELIVERED and "status" in update_fields:
        # ask review from bot user
        transaction.on_commit(
            lambda: ask_review_from_user.delay(instance.id)
        )

    elif instance.status in [OrderStatus.ERROR_IN_BILLZ_API] and "status" in update_fields:
        # send error notification to client
        transaction.on_commit(
            lambda: notify_client_order_error.delay(instance.id)
        )
        # cancel payment
        status = async_to_sync(cancel_order_payment)(instance)
        if status == "success":
            instance.status = OrderStatus.PAYMENT_RETURNED
            instance.save(update_fields=None)
        elif status == "error":
            instance.status = OrderStatus.PAYMENT_RETURN_ERROR
            instance.save(update_fields=None)
        if instance.payment_method != PaymentMethod.CASH:
            transaction.on_commit(
                lambda: notify_client_order_cancellation.delay(instance.id)
            )


@receiver(post_save, sender=OrderItem)
def handle_order_item_creation(sender, instance: OrderItem, created, **kwargs):
    if created:
        # Perform actions when a new order item is created
        instance.product_name = instance.product.name if instance.product else ""
        instance.save(update_fields=["product_name"])


@receiver(post_save, sender=YandexTrip)
def handle_yandex_trip_status_change(sender, instance: YandexTrip, update_fields, **kwargs):
    if instance.status == YandexTripStatus.DELIVERED and "status" in update_fields:
        # Perform actions when the Yandex trip is delivered
        order: Order = instance.order
        order.status = OrderStatus.DELIVERED
        order.save(update_fields=["status"])


@task_failure.connect
def celery_task_failure_handler(sender=None, task_id=None, exception=None,
                               args=None, kwargs=None, traceback=None, einfo=None, **kw):
    run_on_error(exception)


@receiver(post_save, sender=OrderReview)
def handle_order_review_creation(sender, instance: OrderReview, created, **kwargs):
    if created:
        # send gratitude message to user
        send_gratitude_for_review_to_client.delay(instance.id)
        order: Order = instance.order
        order.status = OrderStatus.RATED
        order.save(update_fields=["status"])