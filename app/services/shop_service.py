from app.services import *
from app.models import Shop


def create_shop_from_billz(shops_data):
    for shop in shops_data:
        shop_id = shop.get("id")
        shop_name = shop.get("name")
        # get cashbox id
        cashbox_id = None
        for cashbox in shop.get("cash_boxes", []):
            cashbox_id = cashbox.get("id")
            break

        # Create or update the shop in the local database
        shop_instance, created = Shop.objects.get_or_create(
            shop_id=shop_id,
            defaults={
                "name": shop_name,
                "cashbox_id": cashbox_id
            }
        )
        shop_instance.cashbox_id = cashbox_id
        shop_instance.save(update_fields=["cashbox_id"])