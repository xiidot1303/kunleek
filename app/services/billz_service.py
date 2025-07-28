from config import BILLZ_SECRET_TOKEN
import requests
from django.core.cache import cache
from app.services import *


class APIMethods:
    category = "v2/category"
    products = "v2/products"
    clients = "v1/client"
    customer = "v1/customer"
    client_card = "v1/client-card"

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
        self.access_token = cache.get("billz_access_token") or self.fetch_and_cache_access_token()
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        

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

    def fetch_categories(self):
        url = f"{self.url}{APIMethods.category}"
        response = requests.get(url, headers=self.headers)
        response_data = response.json()
        return response_data.get("categories", [])
    
    def fetch_products(self, page=1):
        url = f"{self.url}{APIMethods.products}"
        params = {"page": page}
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
        client_details.card = data.get("cards", [])[0] if data.get("cards") else None
        return client_details
    
    def create_client(self, chat_id, first_name, phone_number) -> ClientDetails | None:
        url = f"{self.url}{APIMethods.clients}"
        payload = {
            "first_name": first_name,
            "phone_number": phone_number,
            "chat_id": chat_id
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
        client_details.card = response_data.get("cards", [])[0]['code'] if response_data.get("cards") else None
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
