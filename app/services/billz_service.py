from config import BILLZ_SECRET_TOKEN
import requests
from django.core.cache import cache


class APIMethods:
    category = "v2/category"
    products = "v2/products"
    clients = "v1/client"


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