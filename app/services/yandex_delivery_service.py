from celery import shared_task
from app.models import Order, YandexTrip, Shop
from app.services import *
from config import YANDEX_DELIVERY_API_KEY, YANDEX_DELIVERY_URL, YANDEX_DELIVERY_CALLBACK_URL
from app.utils.data_classes import OrderStatus

class PerformerInfo(DictToClass):
    courier_name: str
    car_model: str
    car_color: str
    car_number: str


headers = {
    "Authorization": f"Bearer {YANDEX_DELIVERY_API_KEY}",
    "Content-Type": "application/json",
    "Accept-Language": "ru"
}


@shared_task
def create_claim(order_id: int):
    order: Order = Order.objects.get(id=order_id)
    shop: Shop = order.shop
    # Prepare data for Yandex Delivery API
    data = {
        "items": [
            {
                "cost_currency": "UZS",
                "cost_value": str(int(item.price)),
                "pickup_point": 1,
                "quantity": item.quantity,
                "title": item.product.name,
                "extra_id": order.billz_id,
                "dropoff_point": 2
            } for item in order.items.all()
        ],
        "route_points": [
            {
                "address": {
                    "fullname": shop.address or "Tashkent",
                    "coordinates": [shop.longitude, shop.latitude]
                },
                "contact": {
                    "name": "Магазин Kunleek",
                    "phone": shop.phone
                },
                "point_id": 1,
                "type": "source",
                "visit_order": 1,
                "external_order_id": f"{order.billz_id}",
                "skip_confirmation": True,
            },
            {
                "address": {
                    "fullname": f"{order.address}",
                    "coordinates": [order.longitude, order.latitude]
                },
                "contact": {
                    "name": order.customer.first_name,
                    "phone": order.customer.phone
                },
                "point_id": 2,
                "type": "destination",
                "visit_order": 2,
                "external_order_id": f"{order.billz_id}",
                "skip_confirmation": True,
            }
        ],
        "callback_properties": {
            "callback_url": f"{YANDEX_DELIVERY_CALLBACK_URL}/yandex-delivery-callback"
        },
        "client_requirements": {
            "taxi_class": "express"

        },
        "comment": f"Заказ №{order.billz_id or order.id}\n",
        "emergency_contact": {
            "name": "Buyurtmachi/Заказчик",
            "phone": shop.phone
        }
    }

    # if order is not payed yet, set payment method on delivery
    if not order.payed:
        data["route_points"][0]["buyout"] = {
            "payment_method": "card"
        }
        data["route_points"][0]["payment_on_delivery"] = {
            "payment_method": "card"
        }
        data["route_points"][1]["payment_on_delivery"] = {
            "payment_method": "card"
        }
    response = requests.post(
        f"{YANDEX_DELIVERY_URL}/b2b/cargo/integration/v2/claims/create?request_id={order.id}",
        headers=headers,
        json=data
    )
    if claim_id := response.json().get("id"):
        order.status = OrderStatus.YANDEX_DELIVERING
        order.save(update_fields=["status"])
        # create YandexTrip
        YandexTrip.objects.create(
            order=order,
            claim_id=claim_id,
            status="new"
        )

    else:
        # Handle error
        print(response.json())
    

def check_price(latitude: float, longitude: float):
    data = {
        "route_points": [
            {
                "coordinates": [69.203140, 41.213730],
                "type": "source",
                "id": 1
            },
            {
                "coordinates": [longitude, latitude],
                "id": 2
            }
        ],
        "requirements": {
            "taxi_class": "express"
        }
    }

    response = requests.post(
        f"{YANDEX_DELIVERY_URL}/b2b/cargo/integration/v2/check-price",
        headers=headers,
        json=data
    )
    price = response.json().get("price")

    return price


@shared_task
def accept_order(claim_id):
    data = {
        "version": 1
    }

    response = requests.post(
        f"{YANDEX_DELIVERY_URL}/b2b/cargo/integration/v2/claims/accept?claim_id={claim_id}",
        headers=headers,
        json=data
    )

    return response.json().get("status")


def order_info(claim_id):
    """
    Response example: https://yandex.ru/support/delivery-profile/ru/api/express/openapi/IntegrationV2ClaimsInfo#responses
    """
    response = requests.post(
        f"{YANDEX_DELIVERY_URL}/b2b/cargo/integration/v2/claims/info?claim_id={claim_id}",
        headers=headers
    )
    return response.json()
