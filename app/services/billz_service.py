from config import BILLZ_SECRET_TOKEN, BILLZ_SHOP_ID, BILLZ_CASHBOX_ID
import requests
from django.core.cache import cache
from app.services import *


class APIMethods:
    category = "v2/category"
    products = "v2/products"
    clients = "v1/client"
    customer = "v1/customer"
    client_card = "v1/client-card"
    create_order = "v2/order"
    shops = "v1/shop"


class ClientDetails:
    id = None
    first_name = None
    last_name = None
    card = None
    balance = 0


class BillzService:
    url = "https://api-admin.billz.ai/"

    def __init__(self, method):
        self.method = method
        self.access_token = cache.get(
            "billz_access_token") or self.fetch_and_cache_access_token()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "platform-id": "7d4a4c38-dd84-4902-b744-0488b80a4c01"
            }

    @staticmethod
    def fetch_and_cache_access_token():
        url = "https://api-admin.billz.ai/v1/auth/login"
        payload = {"secret_token": BILLZ_SECRET_TOKEN}
        response = requests.post(url, json=payload)
        response_data = response.json()
        data = response_data.get("data", {})
        access_token = data.get("access_token")
        if access_token:
            cache.set("billz_access_token", access_token, timeout=86400)
        return access_token

    def fetch_shops(self):
        url = f"{self.url}{APIMethods.shops}"
        response = requests.get(url, headers=self.headers)
        response_data = response.json()
        return response_data.get("shops", [])

    def fetch_categories(self):
        url = f"{self.url}{APIMethods.category}"
        response = requests.get(url, headers=self.headers)
        response_data = response.json()
        return response_data.get("categories", [])

    def fetch_products(self, page=1):
        url = f"{self.url}{APIMethods.products}"
        params = {"page": page, "limit": 500}
        response = requests.get(url, headers=self.headers, params=params)
        response_data = response.json()
        return response_data.get("products", [])

    def fetch_clients(self, page=1):
        url = f"{self.url}{APIMethods.clients}"
        params = {"page": page}
        response = requests.get(url, headers=self.headers, params=params)
        response_data = response.json()
        return response_data.get("clients", [])

    def get_client_by_phone_number(self, phone_number) -> ClientDetails | None:
        url = f"{self.url}{APIMethods.clients}"
        params = {"phone_number": phone_number}
        response = requests.get(url, headers=self.headers, params=params)
        response_data = response.json()
        data = response_data.get("clients", {})
        if not data:
            return None
        data = data[0]
        client_details: ClientDetails = DictToClass(data)
        client_details.card = data.get(
            "cards", [])[0] if data.get("cards") else None
        return client_details

    def create_client(self, chat_id, first_name, phone_number) -> str:
        url = f"{self.url}{APIMethods.clients}"
        payload = {
            "first_name": first_name,
            "phone_number": phone_number,
            "chat_id": str(chat_id)
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response_data = response.json()
        id = response_data.get("id")
        return id

    def get_client_by_id(self, client_id) -> ClientDetails | None:
        url = f"{self.url}{APIMethods.customer}/{client_id}"
        response = requests.get(url, headers=self.headers)
        response_data = response.json()
        client_details: ClientDetails = ClientDetails()
        client_details.id = response_data.get("id")
        client_details.first_name = response_data.get("first_name")
        client_details.last_name = response_data.get("last_name")
        client_details.card = response_data.get(
            "cards", [])[0]['code'] if response_data.get("cards") else None
        client_details.balance = response_data.get("balance", 0)
        return client_details

    def create_client_card(self, client_id):
        url = f"{self.url}{APIMethods.client_card}"
        payload = {
            "customer_id": client_id
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response_data = response.json()
        return response_data["card_code"]

    def create_order(self, shop_id, cashbox_id):
        url = f"{self.url}{APIMethods.create_order}?Billz-Response-Channel=HTTP"
        data = {
            "shop_id": shop_id,
            "cashbox_id": cashbox_id
        }
        response = requests.post(url, headers=self.headers, json=data)
        response_data = response.json()
        order_id = response_data.get("id")
        order_number = response_data.get("data", {}).get("order_number")
        self.order_id = order_id
        self.order_number = order_number
        return response_data

    def add_product_to_order(self, product_id, quantity):
        url = f"{self.url}v2/order-product/{self.order_id}"
        data = {
            "sold_measurement_value": quantity,
            "product_id": product_id,
            "used_wholesale_price": False,
            "is_manual": False,
            "response_type": "HTTP"
        }

        response = requests.post(url, headers=self.headers, json=data)
        response_data = response.json()
        return response_data

    def make_discount(self, amount):
        url = f"{self.url}v2/order-manual-discount/{self.order_id}"
        data = {
            "discount_unit": "CURRENCY",
            "discount_value": int(amount),
        }

        response = requests.post(url, headers=self.headers, json=data)
        response_data = response.json()
        return response_data

    def bind_client_to_order(self, client_id):
        url = f"{self.url}v2/order-customer-new/{self.order_id}?Billz-Response-Channel=HTTP"
        data = {
            "customer_id": client_id,
            "check_auth_code": False
        }

        response = requests.put(url, headers=self.headers, json=data)
        response_data = response.json()
        return response_data

    def complete_order(self, paid_amount, payment_method, with_cashback=0):
        payment_types_by_method = {
            "cash": {
                "id": "f1bbdf7d-58e7-43bd-86ec-91ddf8193311",
                "name": "Наличные"

            },
            "payme": {
                "id": "49677309-d2c4-4dd8-8e9f-c9d05776ef71",
                "name": "Payme"
            },
            "click": {
                "id": "6f443ced-4915-4336-b177-c37e5738110e",
                "name": "Терминал"
            }
        }
        url = f"{self.url}v2/order-payment/{self.order_id}"
        data = {
            "payments": [
                {
                    "company_payment_type_id": payment_types_by_method[payment_method]["id"],
                    "paid_amount": int(paid_amount),
                    "company_payment_type": {
                        "name": payment_types_by_method[payment_method]["name"]
                    },
                    "returned_amount": 0
                },
            ],
            "comment": "Telegra bot order",
            "with_cashback": int(with_cashback),
            "without_cashback": False,
            "skip_ofd": False
        }

        response = requests.post(url, headers=self.headers, json=data)
        response_data = response.json()
        return response_data
