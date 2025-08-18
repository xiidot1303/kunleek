from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import *
from app.services.newsletter_service import send_order_info_to_group, send_invoice_to_user
from app.services.order_service import send_order_to_billz

@receiver(post_save, sender=Order)
def handle_cash_payment_order(sender, instance: Order, created, **kwargs):
    if created and (instance.payment_method == "cash" or instance.total == 0):
        instance.payed = True
        handle_order_payment_status_change(sender, instance)
    elif created:
        # send invoice to user with order information
        send_invoice_to_user.delay(instance.id)

@receiver(post_save, sender=Order)
def handle_order_payment_status_change(sender, instance: Order, **kwargs):
    if instance.payed and not instance.sent_to_group:
        # Perform actions when payed changes to True
        send_order_info_to_group.delay(instance.id)
        instance.sent_to_group = True
        instance.save(update_fields=["sent_to_group"])

        # send order to billz
        send_order_to_billz.delay(instance.id)