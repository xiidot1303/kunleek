from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import *
from app.services.newsletter_service import send_order_info_to_group, send_invoice_to_user
from app.services.order_service import send_order_to_billz
from django.db import transaction
from app.services.yandex_delivery_service import create_claim
from config import DEBUG

@receiver(post_save, sender=Order)
def handle_cash_payment_order(sender, instance: Order, created, **kwargs):
    if created and (instance.payment_method == "cash" or instance.total == 0):
        instance.payed = True
        handle_order_payment_status_change(sender, instance)
    elif created:
        # send invoice to user with order information
        transaction.on_commit(
            lambda: send_invoice_to_user.delay(instance.id)
        )

@receiver(post_save, sender=Order)
def handle_order_payment_status_change(sender, instance: Order, **kwargs):
    if instance.payed and not instance.sent_to_group:
        # Perform actions when payed changes to True
        instance.sent_to_group = True
        instance.save(update_fields=["sent_to_group"])
        transaction.on_commit(
            lambda: send_order_info_to_group.delay(instance.id)
        )

        # send order to billz
        if not DEBUG:
            transaction.on_commit(
                lambda: send_order_to_billz.delay(instance.id)
            )

        # Delivery
        if not DEBUG:
            if instance.delivery_type.type == 'express_yandex':
                transaction.on_commit(
                    lambda: create_claim.delay(instance.id)
                )

@receiver(post_save, sender=OrderItem)
def handle_order_item_creation(sender, instance: OrderItem, created, **kwargs):
    if created:
        # Perform actions when a new order item is created
        instance.product_name = instance.product.name if instance.product else ""
        instance.save(update_fields=["product_name"])