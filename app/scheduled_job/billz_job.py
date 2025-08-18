from config import BILLZ_SECRET_TOKEN
import requests
from django.core.cache import cache
from app.services.category_service import *
from app.services.product_service import *
from app.services.client_service import *
from app.services.billz_service import BillzService, APIMethods

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


def fetch_categories():
    billz_service = BillzService(method=APIMethods.category)
    categories = billz_service.fetch_categories()
    create_category_from_billz(categories)


def fetch_products():
    billz_service = BillzService(method=APIMethods.products)
    page = 1
    while True:
        products = billz_service.fetch_products(page=page)
        if products:=products:
            create_product_from_billz(products)
        else:
            break
        
        page += 1


# def fetch_clients():
#     billz_service = BillzService(method=APIMethods.clients)
#     page = 1
#     while True:
#         clients = billz_service.fetch_clients(page=page)
#         if clients:=clients:
#             create_client_from_billz(clients)
#         else:
#             break
        
#         page += 1